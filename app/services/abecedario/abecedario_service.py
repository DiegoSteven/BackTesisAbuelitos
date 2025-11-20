from config.database import db
from models.abecedario import Abecedario
from datetime import datetime, date
from sqlalchemy import func

class AbecedarioService:
    
    @staticmethod
    def save_session(user_id, session_data):
        """Guarda sesión con nivel jugado (Unity debe enviar nivel_dificultad)"""
        try:
            required_fields = ['palabra_objetivo', 'tiempo_resolucion', 'cantidad_errores', 'pistas_usadas', 'completado', 'nivel_dificultad']
            if not all(field in session_data for field in required_fields):
                return None, f"Faltan campos requeridos. Recibido: {list(session_data.keys())}"
            
            # Usar el nivel que Unity envía (el que se determinó en /next-challenge)
            nivel_jugado = session_data['nivel_dificultad']
            
            # Verificar si hubo cambio de nivel
            ultima_sesion = Abecedario.query.filter_by(user_id=user_id).order_by(Abecedario.created_at.desc()).first()
            cambio_nivel = False
            
            if ultima_sesion and ultima_sesion.nivel_jugado and ultima_sesion.nivel_jugado != nivel_jugado:
                cambio_nivel = True
                print(f"[SERVICE] CAMBIO DE NIVEL DETECTADO: {ultima_sesion.nivel_jugado} -> {nivel_jugado}")
            elif not ultima_sesion:
                # Primera sesión del usuario
                cambio_nivel = True
                print(f"[SERVICE] PRIMERA SESIÓN - Nivel inicial: {nivel_jugado}")
            
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
    def get_performance_stats(user_id, limit=10):
        """
        Calcula estadísticas de rendimiento para el prompt de IA
        ANÁLISIS ADAPTATIVO: Detecta sesiones problemáticas recientes
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
            
            # NUEVO: Detectar sesión reciente con MUCHOS errores (≥8)
            sesion_reciente_dificil = any(s.cantidad_errores >= 8 for s in sesiones[:3])
            
            # NUEVO: Promedio de errores en las últimas 3 sesiones
            ultimas_3 = sesiones[:min(3, len(sesiones))]
            ultimas_3_errores = sum(s.cantidad_errores for s in ultimas_3) / len(ultimas_3)
            
            print(f"[SERVICE] Sesión reciente difícil: {sesion_reciente_dificil}")
            print(f"[SERVICE] Promedio errores últimas 3: {ultimas_3_errores}")
            
            # Determinar tendencia (comparar primera mitad vs segunda mitad)
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
                'sesion_reciente_dificil': sesion_reciente_dificil,
                'ultimas_3_errores': round(ultimas_3_errores, 2),
                'historial': [
                    {
                        'palabra': s.palabra_objetivo,
                        'tiempo': s.tiempo_resolucion,
                        'errores': s.cantidad_errores,
                        'completado': s.completado
                    } for s in sesiones
                ]
            }
            
            print(f"[SERVICE] Stats calculadas: total_sesiones={stats['total_sesiones']}, tasa_exito={stats['tasa_exito']}%, sesion_dificil={sesion_reciente_dificil}")
            
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
        Reporte de evolución del usuario agrupado por fecha y nivel
        """
        try:
            sesiones = Abecedario.query.filter_by(user_id=user_id).order_by(Abecedario.fecha_juego.desc()).all()
            
            if not sesiones:
                return {'mensaje': 'Sin datos', 'evolucion': []}, None
            
            # Agrupar por fecha y nivel
            evolucion = {}
            
            for sesion in sesiones:
                fecha_str = sesion.fecha_juego.isoformat()
                nivel = sesion.nivel_jugado or 'facil'
                
                # Crear clave fecha-nivel
                clave = f"{fecha_str}_{nivel}"
                
                if clave not in evolucion:
                    evolucion[clave] = {
                        'fecha': fecha_str,
                        'nivel': nivel.upper(),
                        'total_palabras': 0,
                        'completadas': 0,
                        'tiempo_total': 0,
                        'errores_totales': 0,
                        'pistas_usadas': 0
                    }
                
                evolucion[clave]['total_palabras'] += 1
                if sesion.completado:
                    evolucion[clave]['completadas'] += 1
                evolucion[clave]['tiempo_total'] += sesion.tiempo_resolucion
                evolucion[clave]['errores_totales'] += sesion.cantidad_errores
                evolucion[clave]['pistas_usadas'] += sesion.pistas_usadas
            
            # Calcular promedios
            for key in evolucion:
                total = evolucion[key]['total_palabras']
                evolucion[key]['promedio_tiempo'] = round(evolucion[key]['tiempo_total'] / total, 2)
                evolucion[key]['promedio_errores'] = round(evolucion[key]['errores_totales'] / total, 2)
                evolucion[key]['tasa_exito'] = round((evolucion[key]['completadas'] / total) * 100, 2)
            
            # Convertir a lista ordenada por fecha descendente
            resultado = sorted(evolucion.values(), key=lambda x: x['fecha'], reverse=True)
            
            return {
                'total_sesiones': len(sesiones),
                'evolucion': resultado
            }, None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, str(e)
