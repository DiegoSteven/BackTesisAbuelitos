"""
Controlador para endpoints administrativos
"""
from flask import jsonify
from models.user import User
from models.memory_game import MemoryGameSession, MemoryGameConfig
from models.abecedario import Abecedario
from models.paseo import PaseoSession
from models.train_game import TrainGameSession
from datetime import datetime, timedelta
from sqlalchemy import func
from config.database import db

class AdminController:
    # ... existing methods ...

    @staticmethod
    def get_train_sessions():
        """
        GET /admin/train-sessions
        Obtiene todas las sesiones de Train Game (últimas 20)
        """
        try:
            sessions = db.session.query(TrainGameSession, User.nombre).\
                join(User, TrainGameSession.user_id == User.id).\
                order_by(TrainGameSession.finished_at.desc()).\
                limit(20).\
                all()
            
            result = []
            for session, user_name in sessions:
                session_dict = session.to_dict()
                session_dict['user_name'] = user_name
                result.append(session_dict)
            
            return jsonify({
                'success': True,
                'sessions': result
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @staticmethod
    def get_user_train_sessions(user_id):
        """
        GET /admin/user-train-sessions/<user_id>
        Obtiene todas las sesiones de trenes de un usuario específico
        """
        try:
            sessions = TrainGameSession.query.filter_by(user_id=user_id).\
                order_by(TrainGameSession.finished_at.desc()).\
                all()
            
            return jsonify({
                'success': True,
                'sessions': [s.to_dict() for s in sessions]
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @staticmethod
    def get_user_stats_all_games(user_id):
        """
        GET /admin/user-stats/<user_id>
        Obtiene estadísticas de todos los juegos para un usuario específico
        """
        try:
            # Obtener usuario
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Usuario no encontrado'
                }), 404
            
            # Stats de Memoria
            memory_sessions = MemoryGameSession.query.filter_by(user_id=user_id).all()
            memory_stats = {
                'total_sesiones': len(memory_sessions),
                'promedio_accuracy': sum([s.accuracy_percentage or 0 for s in memory_sessions]) / len(memory_sessions) if memory_sessions else 0,
                'sesiones_completadas': sum([1 for s in memory_sessions if s.completion_status == 'completed'])
            }
            
            # Stats de Abecedario - CORREGIDO: Agrupar por sesiones de juego (por día)
            abecedario_palabras = Abecedario.query.filter_by(user_id=user_id).all()
            
            # Agrupar palabras por fecha (una sesión = un día de juego)
            sesiones_por_dia = {}
            niveles_alcanzados = []  # Para rastrear niveles alcanzados
            
            for palabra in abecedario_palabras:
                fecha = palabra.fecha_juego
                if fecha not in sesiones_por_dia:
                    sesiones_por_dia[fecha] = {
                        'palabras_totales': 0,
                        'palabras_completadas': 0,
                        'tiempo_total': 0
                    }
                sesiones_por_dia[fecha]['palabras_totales'] += 1
                if palabra.completado:
                    sesiones_por_dia[fecha]['palabras_completadas'] += 1
                sesiones_por_dia[fecha]['tiempo_total'] += palabra.tiempo_resolucion
                
                # Rastrear niveles alcanzados
                if palabra.nivel_jugado:
                    niveles_alcanzados.append(palabra.nivel_jugado)
            
            # Determinar el nivel máximo alcanzado
            nivel_alcanzado = 'ninguno'
            if niveles_alcanzados:
                if 'dificil' in niveles_alcanzados:
                    nivel_alcanzado = 'dificil'
                elif 'intermedio' in niveles_alcanzados:
                    nivel_alcanzado = 'intermedio'
                elif 'facil' in niveles_alcanzados:
                    nivel_alcanzado = 'facil'
            
            # Calcular estadísticas
            total_sesiones_abc = len(sesiones_por_dia)  # Una sesión por día
            palabras_completadas_total = sum([s['palabras_completadas'] for s in sesiones_por_dia.values()])
            tiempo_total = sum([s['tiempo_total'] for s in sesiones_por_dia.values()])
            
            abecedario_stats = {
                'total_sesiones': total_sesiones_abc,  # Sesiones de juego (días jugados)
                'palabras_completadas': palabras_completadas_total,  # Total de palabras completadas
                'tiempo_promedio': tiempo_total / total_sesiones_abc if total_sesiones_abc > 0 else 0,  # Tiempo promedio por sesión
                'nivel_alcanzado': nivel_alcanzado  # Nivel máximo alcanzado
            }
            
            
            # Stats de Paseo - CORREGIDO: Agrupar por sesiones de juego (por día)
            paseo_partidas = PaseoSession.query.filter_by(user_id=user_id).all()
            
            # Agrupar partidas por fecha (una sesión = un día de juego)
            sesiones_paseo_por_dia = {}
            
            for partida in paseo_partidas:
                fecha = partida.fecha_juego
                if fecha not in sesiones_paseo_por_dia:
                    sesiones_paseo_por_dia[fecha] = {
                        'partidas_totales': 0,
                        'victorias': 0,
                        'precision_sum': 0,
                        'precision_count': 0
                    }
                sesiones_paseo_por_dia[fecha]['partidas_totales'] += 1
                if partida.resultado == 'victoria':
                    sesiones_paseo_por_dia[fecha]['victorias'] += 1
                if partida.precision is not None:
                    sesiones_paseo_por_dia[fecha]['precision_sum'] += partida.precision
                    sesiones_paseo_por_dia[fecha]['precision_count'] += 1
            
            # Calcular estadísticas
            total_sesiones_paseo = len(sesiones_paseo_por_dia)  # Una sesión por día
            victorias_totales = sum([s['victorias'] for s in sesiones_paseo_por_dia.values()])
            precision_total = sum([s['precision_sum'] for s in sesiones_paseo_por_dia.values()])
            precision_count_total = sum([s['precision_count'] for s in sesiones_paseo_por_dia.values()])
            
            paseo_stats = {
                'total_sesiones': total_sesiones_paseo,  # Sesiones de juego (días jugados)
                'victorias': victorias_totales,  # Total de victorias
                'precision_promedio': precision_total / precision_count_total if precision_count_total > 0 else 0  # Promedio de precisión
            }


            # Stats de Trenes
            train_sessions = TrainGameSession.query.filter_by(user_id=user_id).all()
            train_correct = sum([(s.correct_routing or 0) for s in train_sessions])
            train_wrong = sum([(s.wrong_routing or 0) for s in train_sessions])
            train_total_attempts = train_correct + train_wrong
            
            train_stats = {
                'total_sesiones': len(train_sessions),
                'total_aciertos': train_correct,
                'precision_promedio': (train_correct / train_total_attempts * 100) if train_total_attempts > 0 else 0
            }
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'stats': {
                    'memoria': memory_stats,
                    'abecedario': abecedario_stats,
                    'paseo': paseo_stats,
                    'trenes': train_stats
                }
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    @staticmethod
    def get_abecedario_sessions():
        """
        GET /admin/abecedario-sessions
        Obtiene todas las sesiones de Abecedario (últimas 20)
        """
        try:
            sessions = db.session.query(Abecedario, User.nombre).\
                join(User, Abecedario.user_id == User.id).\
                order_by(Abecedario.created_at.desc()).\
                limit(20).\
                all()
            
            result = []
            for session, user_name in sessions:
                session_dict = session.to_dict()
                session_dict['user_name'] = user_name
                result.append(session_dict)
            
            return jsonify({
                'success': True,
                'sessions': result
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    @staticmethod
    def get_memory_sessions():
        """
        GET /admin/memory-sessions
        Obtiene todas las sesiones de Memory Game (últimas 20)
        """
        try:
            sessions = db.session.query(MemoryGameSession, User.nombre).\
                join(User, MemoryGameSession.user_id == User.id).\
                order_by(MemoryGameSession.finished_at.desc()).\
                limit(20).\
                all()
            
            result = []
            for session, user_name in sessions:
                session_dict = session.to_dict()
                session_dict['user_name'] = user_name
                result.append(session_dict)
            
            return jsonify({
                'success': True,
                'sessions': result
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_memory_configs():
        """
        GET /admin/memory-configs
        Obtiene todas las configuraciones actuales de usuarios
        """
        try:
            configs = MemoryGameConfig.query.all()
            
            return jsonify({
                'success': True,
                'configs': [c.to_dict() | {'user_id': c.user_id, 'last_updated': c.last_updated.isoformat()} 
                           for c in configs]
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_paseo_sessions():
        """
        GET /admin/paseo-sessions
        Obtiene todas las sesiones de Paseo (últimas 20)
        """
        try:
            sessions = db.session.query(PaseoSession, User.nombre).\
                join(User, PaseoSession.user_id == User.id).\
                order_by(PaseoSession.created_at.desc()).\
                limit(20).\
                all()
            
            result = []
            for session, user_name in sessions:
                session_dict = session.to_dict()
                session_dict['user_name'] = user_name
                result.append(session_dict)
            
            return jsonify({
                'success': True,
                'sessions': result
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    

    
    @staticmethod
    def get_user_memory_sessions(user_id):
        """
        GET /admin/user-memory-sessions/<user_id>
        Obtiene todas las sesiones de memoria de un usuario específico
        """
        try:
            sessions = MemoryGameSession.query.filter_by(user_id=user_id).\
                order_by(MemoryGameSession.finished_at.desc()).\
                all()
            
            return jsonify({
                'success': True,
                'sessions': [s.to_dict() for s in sessions]
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_user_abecedario_sessions(user_id):
        """
        GET /admin/user-abecedario-sessions/<user_id>
        Obtiene sesiones de abecedario agrupadas por fecha y nivel
        Estructura: Sesión (por fecha) -> Niveles -> Palabras
        """
        try:
            palabras = Abecedario.query.filter_by(user_id=user_id).\
                order_by(Abecedario.fecha_juego.desc(), Abecedario.created_at.asc()).\
                all()
            
            # Agrupar por FECHA (sesión)
            sesiones = {}
            for palabra in palabras:
                fecha = palabra.fecha_juego.isoformat()
                
                if fecha not in sesiones:
                    sesiones[fecha] = {
                        'fecha': fecha,
                        'niveles': {},
                        'resumen': {
                            'total_palabras': 0,
                            'palabras_completadas': 0,
                            'tiempo_total': 0
                        }
                    }
                
                # Agrupar por NIVEL dentro de cada sesión
                nivel = palabra.nivel_jugado or 'facil'
                if nivel not in sesiones[fecha]['niveles']:
                    sesiones[fecha]['niveles'][nivel] = {
                        'nivel': nivel,
                        'palabras': []
                    }
                
                # Agregar palabra al nivel correspondiente
                sesiones[fecha]['niveles'][nivel]['palabras'].append({
                    'palabra': palabra.palabra_objetivo,
                    'completado': palabra.completado,
                    'tiempo': palabra.tiempo_resolucion,
                    'errores': palabra.cantidad_errores,
                    'pistas': palabra.pistas_usadas,
                    'hora': palabra.created_at.strftime('%H:%M:%S')
                })
                
                # Actualizar resumen de la sesión
                sesiones[fecha]['resumen']['total_palabras'] += 1
                if palabra.completado:
                    sesiones[fecha]['resumen']['palabras_completadas'] += 1
                sesiones[fecha]['resumen']['tiempo_total'] += palabra.tiempo_resolucion
            
            # Convertir dict a lista ordenada
            sesiones_lista = []
            for fecha_key in sorted(sesiones.keys(), reverse=True):
                sesion = sesiones[fecha_key]
                
                # Convertir niveles a lista ordenada
                niveles_lista = []
                for nivel_key in ['facil', 'intermedio', 'dificil']:
                    if nivel_key in sesion['niveles']:
                        niveles_lista.append(sesion['niveles'][nivel_key])
                
                sesion['niveles'] = niveles_lista
                sesiones_lista.append(sesion)
            
            return jsonify({
                'success': True,
                'total_sesiones': len(sesiones_lista),
                'sesiones': sesiones_lista
            }), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_user_paseo_sessions(user_id):
        """
        GET /admin/user-paseo-sessions/<user_id>
        Obtiene sesiones de paseo agrupadas por fecha y nivel
        Estructura: Sesión (por fecha) -> Niveles -> Partidas individuales
        """
        try:
            sessions = PaseoSession.query.filter_by(user_id=user_id).\
                order_by(PaseoSession.fecha_juego.desc(), PaseoSession.created_at.asc()).\
                all()
            
            # Agrupar por FECHA (sesión del día)
            sesiones_agrupadas = {}
            for session in sessions:
                fecha = session.fecha_juego.isoformat()
                
                if fecha not in sesiones_agrupadas:
                    sesiones_agrupadas[fecha] = {
                        'fecha': fecha,
                        'niveles': {},
                        'resumen': {
                            'total_partidas': 0,
                            'victorias': 0,
                            'derrotas': 0,
                            'precision_promedio': 0,
                            'total_aciertos': 0
                        }
                    }
                
                # Agrupar por NIVEL dentro de cada sesión
                nivel = session.nivel_dificultad or 'facil'
                if nivel not in sesiones_agrupadas[fecha]['niveles']:
                    sesiones_agrupadas[fecha]['niveles'][nivel] = {
                        'nivel': nivel,
                        'partidas': []
                    }
                
                # Agregar partida al nivel correspondiente
                sesiones_agrupadas[fecha]['niveles'][nivel]['partidas'].append({
                    'id': session.id,
                    'hora': session.created_at.strftime('%H:%M:%S'),
                    'duracion': session.tiempo_total_sesion or session.duracion_segmento,
                    'aciertos': session.esferas_rojas_atrapadas,
                    'errores': session.esferas_azules_atrapadas,
                    'precision': session.precision,
                    'resultado': session.resultado,
                    'meta_aciertos': session.meta_aciertos,
                    'razon_derrota': session.razon_derrota,
                    'velocidad': session.velocidad_esferas,
                    'cambio_nivel': session.cambio_nivel
                })
                
                # Actualizar resumen del día
                sesiones_agrupadas[fecha]['resumen']['total_partidas'] += 1
                if session.resultado == 'victoria':
                    sesiones_agrupadas[fecha]['resumen']['victorias'] += 1
                else:
                    sesiones_agrupadas[fecha]['resumen']['derrotas'] += 1
                sesiones_agrupadas[fecha]['resumen']['total_aciertos'] += session.esferas_rojas_atrapadas or 0
            
            # Calcular precision promedio y convertir a lista
            sesiones_lista = []
            for fecha_key in sorted(sesiones_agrupadas.keys(), reverse=True):
                sesion = sesiones_agrupadas[fecha_key]
                
                # Calcular precision promedio del día
                total_partidas = sesion['resumen']['total_partidas']
                precision_sum = 0
                conteo = 0
                for nivel_data in sesion['niveles'].values():
                    for partida in nivel_data['partidas']:
                        if partida['precision'] is not None:
                            precision_sum += partida['precision']
                            conteo += 1
                
                if conteo > 0:
                    sesion['resumen']['precision_promedio'] = round(precision_sum / conteo, 2)
                
                # Convertir niveles a lista ordenada
                niveles_lista = []
                for nivel_key in ['facil', 'intermedio', 'dificil']:
                    if nivel_key in sesion['niveles']:
                        niveles_lista.append(sesion['niveles'][nivel_key])
                
                sesion['niveles'] = niveles_lista
                sesiones_lista.append(sesion)
            
            return jsonify({
                'success': True,
                'total_sesiones': len(sesiones_lista),
                'sesiones': sesiones_lista
            }), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_admin_stats():
        """
        GET /admin/stats
        Obtiene estadísticas globales del sistema
        """
        try:
            # Total de sesiones por juego
            memory_count = MemoryGameSession.query.count()
            
            # ABECEDARIO - Contar sesiones agrupadas por usuario y día
            abecedario_query = db.session.query(
                Abecedario.user_id,
                Abecedario.fecha_juego
            ).distinct().all()
            abecedario_count = len(abecedario_query)  # Sesiones únicas (usuario + día)
            
            paseo_count = PaseoSession.query.count()
            train_count = TrainGameSession.query.count()
            
            total_sessions = memory_count + abecedario_count + paseo_count + train_count
            
            # Total de usuarios
            total_users = User.query.count()

            # Sesiones de hoy (Global)
            today = datetime.utcnow().date()
            
            # Helper to count today's sessions for a model with a specific date field
            def count_today(model, date_field):
                return model.query.filter(func.date(date_field) == today).count()

            # Abecedario hoy - Contar sesiones únicas (usuario + día)
            abecedario_today = db.session.query(
                Abecedario.user_id
            ).filter(
                Abecedario.fecha_juego == today
            ).distinct().count()

            sessions_today = (
                count_today(MemoryGameSession, MemoryGameSession.finished_at) +
                abecedario_today +
                count_today(PaseoSession, PaseoSession.created_at) +
                count_today(TrainGameSession, TrainGameSession.finished_at)
            )

            # Activity last 7 days
            last_7_days = []
            for i in range(7):
                day = today - timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                
                def count_day(model, date_field):
                    return model.query.filter(func.date(date_field) == day).count()
                
                # Abecedario - Contar sesiones únicas por día
                abecedario_day = db.session.query(
                    Abecedario.user_id
                ).filter(
                    Abecedario.fecha_juego == day
                ).distinct().count()
                
                count = (
                    count_day(MemoryGameSession, MemoryGameSession.finished_at) +
                    abecedario_day +
                    count_day(PaseoSession, PaseoSession.created_at) +
                    count_day(TrainGameSession, TrainGameSession.finished_at)
                )
                last_7_days.append({'date': day_str, 'count': count})
            
            last_7_days.reverse() # Chronological order
            
            # AI Metrics
            ai_memory_adjustments = MemoryGameSession.query.filter(
                MemoryGameSession.ai_adjustment_decision.isnot(None)
            ).count()
            
            ai_abecedario_changes = Abecedario.query.filter(
                Abecedario.cambio_nivel == True
            ).count()
            
            ai_paseo_recommendations = PaseoSession.query.filter(
                PaseoSession.recomendacion_siguiente.isnot(None)
            ).count()
            
            total_ai_actions = ai_memory_adjustments + ai_abecedario_changes + ai_paseo_recommendations

            return jsonify({
                'success': True,
                'total_sessions': total_sessions,
                'sessions_today': sessions_today,
                'total_users': total_users,
                'game_distribution': {
                    'memoria': memory_count,
                    'abecedario': abecedario_count,
                    'paseo': paseo_count,
                    'trenes': train_count
                },
                'activity_history': last_7_days,
                'ai_metrics': {
                    'total_actions': total_ai_actions,
                    'memory_adjustments': ai_memory_adjustments,
                    'abecedario_level_changes': ai_abecedario_changes,
                    'paseo_recommendations': ai_paseo_recommendations
                }
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    @staticmethod
    def get_train_configs():
        """
        GET /admin/train-configs
        Obtiene todas las configuraciones actuales de usuarios para Train Game
        """
        try:
            from models.train_game import TrainGameConfig
            configs = db.session.query(TrainGameConfig, User.nombre).\
                join(User, TrainGameConfig.user_id == User.id).\
                all()
            
            result = []
            for config, user_name in configs:
                config_dict = config.to_dict()
                config_dict['user_id'] = config.user_id
                config_dict['user_name'] = user_name
                result.append(config_dict)
            
            return jsonify({
                'success': True,
                'configs': result
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
