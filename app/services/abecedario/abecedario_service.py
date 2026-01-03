from config.database import db
from models.abecedario import Abecedario
from datetime import datetime, date
from sqlalchemy import func
import json
import os
import random

class AbecedarioService:
    
    # Cache de palabras predefinidas
    _palabras_cache = None
    
    @staticmethod
    def _cargar_palabras_predefinidas():
        """Carga el JSON de palabras una sola vez (singleton)"""
        if AbecedarioService._palabras_cache is None:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'palabras_predefinidas.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                AbecedarioService._palabras_cache = json.load(f)
        return AbecedarioService._palabras_cache
    
    @staticmethod
    def get_palabra_local(nivel, palabras_usadas_recientes=[]):
        """Obtiene una palabra local para niveles FACIL e INTERMEDIO (sin IA)"""
        palabras_db = AbecedarioService._cargar_palabras_predefinidas()
        
        if nivel not in ['facil', 'intermedio']:
            return None  # Solo para niveles básicos
        
        # Filtrar palabras no usadas recientemente
        palabras_disponibles = [
            p for p in palabras_db[nivel]
            if p['palabra_objetivo'] not in palabras_usadas_recientes
        ]
        
        # Si todas fueron usadas, resetear el pool
        if not palabras_disponibles:
            palabras_disponibles = palabras_db[nivel]
        
        # Seleccionar aleatoriamente
        return random.choice(palabras_disponibles)
    
    @staticmethod
    def save_session(user_id, session_data):
        """Guarda sesión con nivel jugado (Unity debe enviar nivel_dificultad)"""
        try:
            required_fields = ['palabra_objetivo', 'tiempo_resolucion', 'cantidad_errores', 'pistas_usadas', 'completado', 'nivel_dificultad']
            if not all(field in session_data for field in required_fields):
                return None, f"Faltan campos requeridos. Recibido: {list(session_data.keys())}"
            
            # Usar el nivel que Unity envía (el que se determinó en /next-challenge)
            nivel_jugado = session_data['nivel_dificultad']
            
            # Verificar si hubo cambio de nivel O cambio de día
            ultima_sesion = Abecedario.query.filter_by(user_id=user_id).order_by(Abecedario.created_at.desc()).first()
            cambio_nivel = False
            
            fecha_hoy = date.today()
            
            if not ultima_sesion:
                # Primera sesión del usuario
                cambio_nivel = True
                print(f"[SERVICE] PRIMERA SESIÓN - Nivel inicial: {nivel_jugado}")
            elif ultima_sesion.fecha_juego < fecha_hoy:
                # 🆕 NUEVO DÍA: Resetear COMPLETAMENTE (regresa a FÁCIL y 0/5)
                cambio_nivel = True
                print(f"[SERVICE] NUEVO DÍA DETECTADO: {ultima_sesion.fecha_juego} -> {fecha_hoy}")
                print(f"[SERVICE] Reseteando a FÁCIL con progreso 0/5")
            elif ultima_sesion.nivel_jugado and ultima_sesion.nivel_jugado != nivel_jugado:
                # Cambio de nivel (subió o bajó)
                cambio_nivel = True
                print(f"[SERVICE] CAMBIO DE NIVEL DETECTADO: {ultima_sesion.nivel_jugado} -> {nivel_jugado}")
            
            nueva_sesion = Abecedario(
                user_id=user_id,
                palabra_objetivo=session_data['palabra_objetivo'],
                longitud_palabra=len(session_data['palabra_objetivo']),
                tiempo_resolucion=session_data['tiempo_resolucion'],
                cantidad_errores=session_data['cantidad_errores'],
                pistas_usadas=session_data['pistas_usadas'],
                completado=session_data['completado'],
                fecha_juego=date.today(),
                nivel_jugado=nivel_jugado,
                cambio_nivel=cambio_nivel
            )
            
            db.session.add(nueva_sesion)
            db.session.commit()
            
            print(f"[SERVICE] Sesión guardada - Nivel: {nivel_jugado}, Completado: {session_data['completado']}, Cambio: {cambio_nivel}")
            
            return nueva_sesion, None
            
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    @staticmethod
    def get_recent_performance(user_id, limit=10):
        """
        Obtiene las últimas N sesiones del usuario para análisis
        INCLUYENDO las NO completadas para detectar dificultades
        """
        try:
            sesiones = Abecedario.query.filter_by(
                user_id=user_id
            ).order_by(Abecedario.created_at.desc()).limit(limit).all()
            
            return sesiones, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def analizar_necesidad_bajar_nivel(user_id):
        """
        NUEVA LÓGICA: Analiza las últimas 5 palabras para detectar frustración.
        Si el usuario falló en 4 de las últimas 5 palabras, baja de nivel.
        
        Returns:
            bool: True si debe bajar de nivel, False si no
        """
        try:
            # Obtener las últimas 5 sesiones (completadas o no)
            ultimas_5 = Abecedario.query.filter_by(
                user_id=user_id
            ).order_by(Abecedario.created_at.desc()).limit(5).all()
            
            if len(ultimas_5) < 5:
                return False  # No hay suficiente historial
            
            # Contar cuántas NO fueron completadas
            fallidas = sum(1 for s in ultimas_5 if not s.completado)
            
            debe_bajar = fallidas >= 4
            
            if debe_bajar:
                print(f"[ANÁLISIS] FRUSTRACIÓN DETECTADA: {fallidas}/5 palabras falladas → BAJAR NIVEL")
            else:
                print(f"[ANÁLISIS] Rendimiento aceptable: {fallidas}/5 falladas")
            
            return debe_bajar
            
        except Exception as e:
            print(f"[ANÁLISIS ERROR] {str(e)}")
            return False
    
    @staticmethod
    def determinar_nivel_optimo(user_id):
        """
        LÓGICA OPTIMIZADA DE NIVELES:
        1. Usuario nuevo → FACIL
        2. Nuevo día (fecha_juego < hoy) → FACIL (reseteo completo)
        3. Falló 4 de las últimas 5 palabras → BAJA un nivel
        4. Completó 5 palabras en el nivel actual → SUBE de nivel
        5. Caso contrario → MANTIENE nivel
        
        Returns:
            str: 'facil', 'intermedio' o 'dificil'
        """
        try:
            fecha_hoy = date.today()
            
            # Obtener última sesión para saber nivel actual
            ultima_sesion = Abecedario.query.filter_by(
                user_id=user_id
            ).order_by(Abecedario.created_at.desc()).first()
            
            # Usuario nuevo
            if not ultima_sesion:
                print("[NIVEL] Usuario nuevo → FACIL")
                return 'facil'
            
            # 🆕 NUEVO DÍA: Resetear a FACIL para comparar evolución
            if ultima_sesion.fecha_juego < fecha_hoy:
                print(f"[NIVEL] Nuevo día ({ultima_sesion.fecha_juego} -> {fecha_hoy}) → Resetear a FACIL")
                return 'facil'
            
            nivel_actual = ultima_sesion.nivel_jugado or 'facil'
            
            # REGLA 1: Detectar frustración (4 de 5 falladas)
            debe_bajar = AbecedarioService.analizar_necesidad_bajar_nivel(user_id)
            
            if debe_bajar:
                if nivel_actual == 'dificil':
                    print(f"[NIVEL] Frustración detectada → BAJA de DIFICIL a INTERMEDIO")
                    return 'intermedio'
                elif nivel_actual == 'intermedio':
                    print(f"[NIVEL] Frustración detectada → BAJA de INTERMEDIO a FACIL")
                    return 'facil'
                else:
                    print(f"[NIVEL] Frustración detectada pero ya en FACIL → MANTIENE FACIL")
                    return 'facil'
            
            # REGLA 2: Contar palabras completadas en nivel actual desde último cambio
            ultima_sesion_cambio = Abecedario.query.filter_by(
                user_id=user_id,
                cambio_nivel=True
            ).order_by(Abecedario.created_at.desc()).first()
            
            query = Abecedario.query.filter_by(
                user_id=user_id,
                nivel_jugado=nivel_actual,
                completado=True
            )
            
            if ultima_sesion_cambio:
                query = query.filter(Abecedario.created_at >= ultima_sesion_cambio.created_at)
            
            completadas_en_nivel = min(query.count(), 5)
            
            print(f"[NIVEL] Nivel actual: {nivel_actual.upper()}, Completadas: {completadas_en_nivel}/5")
            
            # REGLA 3: Si completó 5, sube de nivel
            if completadas_en_nivel >= 5:
                if nivel_actual == 'facil':
                    print(f"[NIVEL] 5/5 completadas → SUBE de FACIL a INTERMEDIO")
                    return 'intermedio'
                elif nivel_actual == 'intermedio':
                    print(f"[NIVEL] 5/5 completadas → SUBE de INTERMEDIO a DIFICIL")
                    return 'dificil'
                else:
                    print(f"[NIVEL] Permanece en DIFICIL (nivel máximo)")
                    return 'dificil'
            
            # REGLA 4: Mantener nivel
            print(f"[NIVEL] Mantiene nivel {nivel_actual.upper()}")
            return nivel_actual
            
        except Exception as e:
            print(f"[NIVEL ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            return 'facil'  # Fallback seguro
    
    @staticmethod
    def get_performance_stats(user_id, limit=10):
        """
        Calcula estadísticas de rendimiento (simplificado)
        Ya no se usa para determinar nivel (eso lo hace determinar_nivel_optimo)
        """
        print(f"[SERVICE] Obteniendo stats para user_id: {user_id}, limit: {limit}")
        
        try:
            sesiones, error = AbecedarioService.get_recent_performance(user_id, limit)
            
            print(f"[SERVICE] Sesiones encontradas: {len(sesiones) if sesiones else 0}")
            
            if error:
                print(f"[SERVICE ERROR] {error}")
                return None, error
            
            if not sesiones:
                print("[SERVICE] Usuario nuevo - sin sesiones previas")
                stats = {
                    'promedio_tiempo': 0,
                    'promedio_errores': 0,
                    'tasa_exito': 0,
                    'total_sesiones': 0,
                    'completadas': 0,
                    'ultima_palabra': None,
                    'tendencia': 'sin_datos',
                    'sesion_reciente_dificil': False,
                    'ultimas_3_errores': 0
                }
                print(f"[SERVICE] Stats calculadas: {stats}")
                return stats, None
            
            total_sesiones = len(sesiones)
            promedio_tiempo = sum(s.tiempo_resolucion for s in sesiones) / total_sesiones
            promedio_errores = sum(s.cantidad_errores for s in sesiones) / total_sesiones
            completadas = sum(1 for s in sesiones if s.completado)
            tasa_exito = (completadas / total_sesiones) * 100
            
            # Determinar tendencia simplificada
            if total_sesiones >= 4:
                mitad = total_sesiones // 2
                tiempo_reciente = sum(s.tiempo_resolucion for s in sesiones[:mitad]) / mitad
                tiempo_anterior = sum(s.tiempo_resolucion for s in sesiones[mitad:]) / (total_sesiones - mitad)
                
                if tiempo_reciente < tiempo_anterior * 0.9:
                    tendencia = 'mejorando'
                elif tiempo_reciente > tiempo_anterior * 1.1:
                    tendencia = 'empeorando'
                else:
                    tendencia = 'estable'
            else:
                tendencia = 'insuficientes_datos'
            
            stats = {
                'promedio_tiempo': round(promedio_tiempo, 2),
                'promedio_errores': round(promedio_errores, 2),
                'tasa_exito': round(tasa_exito, 2),
                'total_sesiones': total_sesiones,
                'completadas': completadas,
                'ultima_palabra': sesiones[0].palabra_objetivo if sesiones else None,
                'ultima_longitud': sesiones[0].longitud_palabra if sesiones else 0,
                'ultimo_tiempo': sesiones[0].tiempo_resolucion if sesiones else 0,
                'ultimos_errores': sesiones[0].cantidad_errores if sesiones else 0,
                'tendencia': tendencia,
                'historial': [
                    {
                        'palabra': s.palabra_objetivo,
                        'tiempo': s.tiempo_resolucion,
                        'errores': s.cantidad_errores,
                        'completado': s.completado
                    } for s in sesiones
                ]
            }
            
            print(f"[SERVICE] Stats calculadas: total_sesiones={stats['total_sesiones']}, tasa_exito={stats['tasa_exito']}%")
            
            return stats, None
            
        except Exception as e:
            print(f"[SERVICE EXCEPTION] {str(e)}")
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    @staticmethod
    def get_sessions_by_date_range(user_id, fecha_inicio, fecha_fin):
        """
        Obtiene sesiones en un rango de fechas para análisis
        """
        try:
            sesiones = Abecedario.query.filter(
                Abecedario.user_id == user_id,
                Abecedario.fecha_juego >= fecha_inicio,
                Abecedario.fecha_juego <= fecha_fin
            ).order_by(Abecedario.created_at.asc()).all()
            
            return sesiones, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_daily_summary(user_id, fecha=None):
        """
        Resumen de sesiones por día
        """
        try:
            if fecha is None:
                fecha = date.today()
            
            sesiones = Abecedario.query.filter_by(
                user_id=user_id,
                fecha_juego=fecha
            ).all()
            
            if not sesiones:
                return {
                    'fecha': fecha.isoformat(),
                    'total_palabras': 0,
                    'palabras_completadas': 0,
                    'tiempo_total': 0,
                    'errores_totales': 0
                }, None
            
            return {
                'fecha': fecha.isoformat(),
                'total_palabras': len(sesiones),
                'palabras_completadas': sum(1 for s in sesiones if s.completado),
                'tiempo_total': sum(s.tiempo_resolucion for s in sesiones),
                'errores_totales': sum(s.cantidad_errores for s in sesiones),
                'promedio_tiempo': sum(s.tiempo_resolucion for s in sesiones) / len(sesiones),
                'sesiones': Abecedario.to_collection_dict(sesiones)
            }, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_evolution_report(user_id):
        """
        Reporte de evolución RESUMIDO del usuario.
        Solo métricas clave por fecha y nivel (sin detalles de sesiones).
        """
        try:
            sesiones = Abecedario.query.filter_by(user_id=user_id).order_by(
                Abecedario.fecha_juego.asc(), 
                Abecedario.created_at.asc()
            ).all()
            
            if not sesiones:
                return {'mensaje': 'Sin datos', 'evolucion_por_fecha': []}, None
            
            # Agrupar por FECHA primero
            evolucion_por_fecha = {}
            
            for sesion in sesiones:
                fecha_str = sesion.fecha_juego.isoformat()
                nivel = sesion.nivel_jugado or 'facil'
                
                # Crear estructura por fecha si no existe
                if fecha_str not in evolucion_por_fecha:
                    evolucion_por_fecha[fecha_str] = {
                        'fecha': fecha_str,
                        'niveles': {},
                        'resumen_dia': {
                            'total_palabras': 0,
                            'total_completadas': 0,
                            'tiempo_total_dia': 0
                        }
                    }
                
                # Crear estructura por nivel dentro de la fecha
                if nivel not in evolucion_por_fecha[fecha_str]['niveles']:
                    evolucion_por_fecha[fecha_str]['niveles'][nivel] = {
                        'nivel': nivel.upper(),
                        'total_palabras': 0,
                        'completadas': 0,
                        'tiempo_total': 0,
                        'tasa_exito': 0,
                        'sesiones_detalle': [],  # Temporal para cálculo
                        'progresion': {
                            'completo_5_de_5': False,
                            'tiempo_para_completar_nivel': None
                        }
                    }
                
                nivel_data = evolucion_por_fecha[fecha_str]['niveles'][nivel]
                
                # Agregar sesión
                nivel_data['total_palabras'] += 1
                if sesion.completado:
                    nivel_data['completadas'] += 1
                    
                nivel_data['tiempo_total'] += sesion.tiempo_resolucion
                
                nivel_data['sesiones_detalle'].append({
                    'completado': sesion.completado,
                    'tiempo': sesion.tiempo_resolucion,
                    'hora': sesion.created_at.strftime('%H:%M:%S'),
                    'cambio_nivel': sesion.cambio_nivel
                })
                
                # Actualizar resumen del día
                evolucion_por_fecha[fecha_str]['resumen_dia']['total_palabras'] += 1
                if sesion.completado:
                    evolucion_por_fecha[fecha_str]['resumen_dia']['total_completadas'] += 1
                evolucion_por_fecha[fecha_str]['resumen_dia']['tiempo_total_dia'] += sesion.tiempo_resolucion
            
            # Calcular métricas de PROGRESIÓN (solo lo esencial)
            for fecha_str in evolucion_por_fecha:
                for nivel in evolucion_por_fecha[fecha_str]['niveles']:
                    nivel_data = evolucion_por_fecha[fecha_str]['niveles'][nivel]
                    
                    # Calcular tasa de éxito
                    total = nivel_data['total_palabras']
                    nivel_data['tasa_exito'] = round((nivel_data['completadas'] / total) * 100, 2)
                    nivel_data['tiempo_total'] = round(nivel_data['tiempo_total'], 2)
                    
                    # 🎯 MÉTRICA CLAVE: Tiempo para completar 5/5
                    completadas_consecutivas = 0
                    tiempo_acumulado = 0
                    inicio_progresion = None
                    fin_progresion = None
                    
                    for sesion in nivel_data['sesiones_detalle']:
                        # Detectar inicio de progresión (cambio de nivel)
                        if sesion['cambio_nivel']:
                            completadas_consecutivas = 0
                            tiempo_acumulado = 0
                            inicio_progresion = sesion['hora']
                        
                        tiempo_acumulado += sesion['tiempo']
                        
                        if sesion['completado']:
                            completadas_consecutivas += 1
                            fin_progresion = sesion['hora']
                            
                            # Si completó 5, guardamos el tiempo
                            if completadas_consecutivas >= 5:
                                nivel_data['progresion']['completo_5_de_5'] = True
                                nivel_data['progresion']['tiempo_para_completar_nivel'] = round(tiempo_acumulado, 2)
                                nivel_data['progresion']['hora_inicio'] = inicio_progresion
                                nivel_data['progresion']['hora_fin'] = fin_progresion
                                break
                    
                    # Si no completó 5/5, indicar progreso actual
                    if not nivel_data['progresion']['completo_5_de_5']:
                        nivel_data['progresion']['palabras_completadas'] = completadas_consecutivas
                        nivel_data['progresion']['faltan'] = 5 - completadas_consecutivas
                    
                    # 🗑️ Eliminar sesiones_detalle (no se necesita en respuesta)
                    del nivel_data['sesiones_detalle']
                
                # Calcular resumen del día
                resumen = evolucion_por_fecha[fecha_str]['resumen_dia']
                resumen['tiempo_total_dia'] = round(resumen['tiempo_total_dia'], 2)
                resumen['tasa_exito_dia'] = round(
                    (resumen['total_completadas'] / resumen['total_palabras']) * 100, 2
                ) if resumen['total_palabras'] > 0 else 0
            
            # Convertir a lista ordenada por fecha (más reciente primero)
            resultado = []
            for fecha_str in sorted(evolucion_por_fecha.keys(), reverse=True):
                fecha_data = evolucion_por_fecha[fecha_str]
                
                # Convertir niveles de dict a lista
                niveles_lista = []
                for nivel_key in ['facil', 'intermedio', 'dificil']:
                    if nivel_key in fecha_data['niveles']:
                        niveles_lista.append(fecha_data['niveles'][nivel_key])
                
                resultado.append({
                    'fecha': fecha_data['fecha'],
                    'resumen_dia': fecha_data['resumen_dia'],
                    'niveles': niveles_lista
                })
            
            return {
                'total_sesiones': len(sesiones),
                'evolucion_por_fecha': resultado
            }, None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    @staticmethod
    def get_final_game_stats(user_id, fecha=None):
        """
        Calcula estadísticas finales del juego usando SOLO campos existentes.
        Incluye cálculo de puntos basado en desempeño.
        
        Returns:
            dict: Estadísticas completas con puntos calculados
        """
        try:
            if fecha is None:
                fecha = date.today()
            
            # Obtener todas las sesiones del día
            sesiones = Abecedario.query.filter_by(
                user_id=user_id,
                fecha_juego=fecha
            ).order_by(Abecedario.created_at.asc()).all()
            
            if not sesiones:
                return {
                    'fecha': fecha.isoformat(),
                    'puntos_totales': 0,
                    'palabras_completadas': 0,
                    'palabras_totales': 0,
                    'por_nivel': {},
                    'metricas_globales': {
                        'tiempo_promedio': 0,
                        'mejor_tiempo': 0,
                        'precision': 0,
                        'total_errores': 0,
                        'total_pistas': 0
                    }
                }, None
            
            # Inicializar contadores
            puntos_totales = 0
            palabras_completadas = 0
            palabras_totales = len(sesiones)
            
            # Métricas por nivel
            por_nivel = {
                'facil': {'palabras': 0, 'completadas': 0, 'puntos': 0},
                'intermedio': {'palabras': 0, 'completadas': 0, 'puntos': 0},
                'dificil': {'palabras': 0, 'completadas': 0, 'puntos': 0}
            }
            
            # Métricas globales
            tiempos = []
            total_errores = 0
            total_pistas = 0
            
            # Puntos base por nivel
            puntos_base = {
                'facil': 10,
                'intermedio': 25,
                'dificil': 50
            }
            
            # Procesar cada sesión
            for sesion in sesiones:
                nivel = sesion.nivel_jugado or 'facil'
                
                # Contar palabras por nivel
                por_nivel[nivel]['palabras'] += 1
                
                if sesion.completado:
                    palabras_completadas += 1
                    por_nivel[nivel]['completadas'] += 1
                    
                    # CALCULAR PUNTOS SOLO SI COMPLETÓ LA PALABRA
                    base = puntos_base[nivel]
                    multiplicador = 1.0
                    
                    # Bonificación: Sin errores (+50%)
                    if sesion.cantidad_errores == 0:
                        multiplicador += 0.5
                    
                    # Bonificación: Sin pistas en nivel difícil (+25%)
                    if sesion.pistas_usadas == 0 and nivel == 'dificil':
                        multiplicador += 0.25
                    
                    # Bonificación: Tiempo rápido < 15s (+20%)
                    if sesion.tiempo_resolucion < 15:
                        multiplicador += 0.2
                    
                    # Penalización: Errores (-5 puntos cada uno)
                    penalizacion = sesion.cantidad_errores * 5
                    
                    # Calcular puntos finales (mínimo 0)
                    puntos_palabra = max(0, int((base * multiplicador) - penalizacion))
                    
                    puntos_totales += puntos_palabra
                    por_nivel[nivel]['puntos'] += puntos_palabra
                
                # Acumular métricas
                if sesion.completado:
                    tiempos.append(sesion.tiempo_resolucion)
                total_errores += sesion.cantidad_errores
                total_pistas += sesion.pistas_usadas
            
            # Calcular métricas globales
            tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
            mejor_tiempo = min(tiempos) if tiempos else 0
            precision = (palabras_completadas / palabras_totales * 100) if palabras_totales > 0 else 0
            
            # Construir respuesta
            resultado = {
                'fecha': fecha.isoformat(),
                'puntos_totales': puntos_totales,
                'palabras_completadas': palabras_completadas,
                'palabras_totales': palabras_totales,
                'por_nivel': {
                    'facil': {
                        'total': por_nivel['facil']['palabras'],
                        'completadas': por_nivel['facil']['completadas'],
                        'puntos': por_nivel['facil']['puntos']
                    },
                    'intermedio': {
                        'total': por_nivel['intermedio']['palabras'],
                        'completadas': por_nivel['intermedio']['completadas'],
                        'puntos': por_nivel['intermedio']['puntos']
                    },
                    'dificil': {
                        'total': por_nivel['dificil']['palabras'],
                        'completadas': por_nivel['dificil']['completadas'],
                        'puntos': por_nivel['dificil']['puntos']
                    }
                },
                'metricas_globales': {
                    'tiempo_promedio': round(tiempo_promedio, 2),
                    'mejor_tiempo': round(mejor_tiempo, 2),
                    'precision': round(precision, 2),
                    'total_errores': total_errores,
                    'total_pistas': total_pistas
                }
            }
            
            return resultado, None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, str(e)
