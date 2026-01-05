from models.paseo import PaseoSession
from config.database import db
from datetime import date

class PaseoService:
    """Servicio SIMPLIFICADO para Paseo - Patrón de Abecedario"""
    
    @staticmethod
    def save_session(user_id, session_data):
        """
        Guarda cada nivel jugado (FACIL/INTERMEDIO/DIFICIL)
        Detecta cambios de nivel y cambios de día
        """
        try:
            required_fields = [
                'nivel_dificultad', 'meta_aciertos', 'total_aciertos',
                'total_errores_incorrecto', 'total_errores_perdidas',
                'duracion_total', 'completado'
            ]
            
            if not all(field in session_data for field in required_fields):
                return None, f"Faltan campos requeridos. Recibido: {list(session_data.keys())}"
            
            # Nivel que Unity envía
            nivel_jugado = session_data['nivel_dificultad']
            
            # Verificar cambio de nivel O cambio de día
            ultima_sesion = PaseoSession.query.filter_by(
                user_id=user_id
            ).order_by(PaseoSession.created_at.desc()).first()
            
            cambio_nivel = False
            fecha_hoy = date.today()
            
            if not ultima_sesion:
                # Primera sesión del usuario
                cambio_nivel = True
                print(f"[PASEO] PRIMERA SESIÓN - Nivel: {nivel_jugado}")
            elif ultima_sesion.fecha_juego < fecha_hoy:
                # NUEVO DÍA: Resetear (regresa a nivel que IA decida)
                cambio_nivel = True
                print(f"[PASEO] NUEVO DÍA: {ultima_sesion.fecha_juego} -> {fecha_hoy}")
            elif ultima_sesion.nivel_dificultad and ultima_sesion.nivel_dificultad != nivel_jugado:
                # Cambio de nivel (FACIL→INTERMEDIO→DIFICIL)
                cambio_nivel = True
                print(f"[PASEO] CAMBIO DE NIVEL: {ultima_sesion.nivel_dificultad} -> {nivel_jugado}")
            
            # Calcular precisión
            aciertos = session_data['total_aciertos']
            meta = session_data['meta_aciertos']
            total_esferas = (aciertos + session_data['total_errores_incorrecto'] + 
                           session_data['total_errores_perdidas'])
            precision = (aciertos / total_esferas * 100) if total_esferas > 0 else 0
            
            # Determinar resultado
            completado = session_data['completado']
            if completado and aciertos >= meta:
                resultado = "victoria"
            else:
                resultado = "derrota"
            
            # Guardar sesión
            nueva_sesion = PaseoSession(
                user_id=user_id,
                velocidad_esferas=session_data.get('velocidad_esferas', 3.0),
                intervalo_spawn=session_data.get('intervalo_spawn', 2.0),
                colores_activos=session_data.get('colores_activos', 'rojo'),
                color_correcto=session_data.get('color_correcto', 'rojo'),
                duracion_segmento=session_data['duracion_total'],
                esferas_rojas_atrapadas=aciertos,
                esferas_azules_atrapadas=session_data['total_errores_incorrecto'],
                esferas_perdidas=session_data['total_errores_perdidas'],
                precision=precision,
                nivel_dificultad=nivel_jugado,
                meta_aciertos=meta,
                resultado=resultado,
                cambio_nivel=cambio_nivel,  # ✅ Flag de cambio
                fecha_juego=fecha_hoy,
                fase='adaptativo',
                sesion_completa=True,  # Cada nivel es una sesión completa
                tiempo_reaccion_promedio=session_data.get('tiempo_reaccion_promedio', 1.0)
            )
            
            db.session.add(nueva_sesion)
            db.session.commit()
            
            print(f"[PASEO] ✅ Sesión guardada - Nivel: {nivel_jugado}, Resultado: {resultado}, Cambio: {cambio_nivel}")
            
            return nueva_sesion, None
            
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    @staticmethod
    def get_ultima_sesion(user_id):
        """Obtiene la última sesión jugada (cualquier día)"""
        try:
            ultima = PaseoSession.query.filter_by(
                user_id=user_id
            ).order_by(PaseoSession.created_at.desc()).first()
            
            if not ultima:
                return None, None
            
            return {
                'nivel': ultima.nivel_dificultad,
                'resultado': ultima.resultado,
                'fecha': ultima.fecha_juego,
                'aciertos': ultima.esferas_rojas_atrapadas,
                'meta': ultima.meta_aciertos
            }, None
            
        except Exception as e:
            print(f"[PASEO ERROR] get_ultima_sesion: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_final_stats(user_id, fecha=None):
        """
        Calcula estadísticas finales del juego usando SOLO campos existentes.
        Retorna: precisión, total de errores, total de aciertos del día
        """
        try:
            if fecha is None:
                fecha = date.today()
            
            # Obtener todas las sesiones del día
            sesiones = PaseoSession.query.filter_by(
                user_id=user_id,
                fecha_juego=fecha
            ).order_by(PaseoSession.created_at.asc()).all()
            
            if not sesiones:
                return {
                    'fecha': fecha.isoformat(),
                    'precision': 0.0,
                    'total_errores': 0,
                    'total_aciertos': 0,
                    'total_sesiones': 0
                }, None
            
            # Calcular totales
            total_aciertos = 0
            total_errores = 0
            
            for sesion in sesiones:
                total_aciertos += sesion.esferas_rojas_atrapadas or 0
                total_errores += (sesion.esferas_azules_atrapadas or 0) + (sesion.esferas_perdidas or 0)
            
            # Calcular precisión
            total_esferas = total_aciertos + total_errores
            precision = (total_aciertos / total_esferas * 100) if total_esferas > 0 else 0
            
            resultado = {
                'fecha': fecha.isoformat(),
                'precision': round(precision, 1),
                'total_errores': total_errores,
                'total_aciertos': total_aciertos,
                'total_sesiones': len(sesiones)
            }
            
            return resultado, None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, str(e)
