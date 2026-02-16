"""
Controlador para endpoints administrativos
"""
from flask import jsonify
from models.user import User
from models.memory_game import MemoryGameSession, MemoryGameConfig
from models.abecedario import Abecedario
from models.paseo import PaseoSession
from models.train_game import TrainGameSession, TrainGameConfig
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
        Obtiene sesiones de trenes agrupadas por fecha y nivel de dificultad
        Estructura: Sesión (por fecha) -> Niveles (por color_count) -> Partidas individuales
        """
        try:
            sessions = TrainGameSession.query.filter_by(user_id=user_id).\
                order_by(TrainGameSession.finished_at.desc()).\
                all()
            
            # Agrupar por FECHA (sesión del día)
            sesiones_agrupadas = {}
            for session in sessions:
                # Usar finished_at o started_at para obtener la fecha
                fecha_dt = session.finished_at or session.started_at
                if not fecha_dt:
                    continue
                fecha = fecha_dt.strftime('%Y-%m-%d')
                
                if fecha not in sesiones_agrupadas:
                    sesiones_agrupadas[fecha] = {
                        'fecha': fecha,
                        'niveles': {},
                        'resumen': {
                            'total_partidas': 0,
                            'completadas': 0,
                            'total_aciertos': 0,
                            'total_errores': 0,
                            'tiempo_total': 0
                        }
                    }
                
                # Agrupar por número de colores (como proxy de dificultad)
                color_count = session.color_count or 3
                nivel_label = f'{color_count}_colores'
                if nivel_label not in sesiones_agrupadas[fecha]['niveles']:
                    sesiones_agrupadas[fecha]['niveles'][nivel_label] = {
                        'nivel': nivel_label,
                        'color_count': color_count,
                        'partidas': []
                    }
                
                # Calcular duración desde timestamps
                duracion = 0
                if session.started_at and session.finished_at:
                    duracion = (session.finished_at - session.started_at).total_seconds()
                
                # Calcular precisión
                total_attempts = (session.correct_routing or 0) + (session.wrong_routing or 0)
                precision = (session.correct_routing / total_attempts * 100) if total_attempts > 0 else 0
                
                # Agregar partida al nivel correspondiente
                sesiones_agrupadas[fecha]['niveles'][nivel_label]['partidas'].append({
                    'session_id': session.session_id,
                    'hora': fecha_dt.strftime('%H:%M:%S'),
                    'duracion': duracion,
                    'aciertos': session.correct_routing,
                    'errores': session.wrong_routing,
                    'choques': session.crash_count,
                    'precision': precision,
                    'velocidad': session.train_speed,
                    'spawn_rate': session.spawn_rate,
                    'estado': session.completion_status
                })
                
                # Actualizar resumen de la sesión
                sesiones_agrupadas[fecha]['resumen']['total_partidas'] += 1
                if session.completion_status == 'completed':
                    sesiones_agrupadas[fecha]['resumen']['completadas'] += 1
                sesiones_agrupadas[fecha]['resumen']['total_aciertos'] += session.correct_routing or 0
                sesiones_agrupadas[fecha]['resumen']['total_errores'] += session.wrong_routing or 0
                sesiones_agrupadas[fecha]['resumen']['tiempo_total'] += duracion
            
            # Calcular promedios y convertir a lista ordenada
            sesiones_lista = []
            for fecha_key in sorted(sesiones_agrupadas.keys(), reverse=True):
                sesion = sesiones_agrupadas[fecha_key]
                
                # Calcular precisión promedio
                total = sesion['resumen']['total_aciertos'] + sesion['resumen']['total_errores']
                sesion['resumen']['precision_promedio'] = (sesion['resumen']['total_aciertos'] / total * 100) if total > 0 else 0
                
                # Convertir niveles a lista ordenada por color_count
                niveles_lista = sorted(sesion['niveles'].values(), key=lambda x: x['color_count'])
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
            
            mem_tiempo_total = sum([s.elapsed_time_seconds or 0 for s in memory_sessions])
            mem_niveles = [s.difficulty_level for s in memory_sessions if s.difficulty_level]
            
            # Determinar nivel máximo memoria
            mem_nivel_max = 'N/A'
            # Memory game uses English level names: tutorial, easy, medium, hard
            difficulty_order = {'tutorial': 0, 'easy': 1, 'medium': 2, 'hard': 3}
            if mem_niveles:
                mem_nivel_max = max(mem_niveles, key=lambda x: difficulty_order.get(x.lower(), 0))

            memory_stats = {
                'total_sesiones': len(memory_sessions),
                'promedio_accuracy': sum([s.accuracy_percentage or 0 for s in memory_sessions]) / len(memory_sessions) if memory_sessions else 0,
                'sesiones_completadas': sum([1 for s in memory_sessions if s.completion_status == 'completed']),
                'tiempo_total': mem_tiempo_total,
                'tiempo_promedio': mem_tiempo_total / len(memory_sessions) if memory_sessions else 0,
                'nivel_maximo': mem_nivel_max
            }
            
            # Stats de Abecedario
            abecedario_palabras = Abecedario.query.filter_by(user_id=user_id).all()
            
            # Agrupar palabras por fecha (una sesión = un día de juego)
            sesiones_por_dia = {}
            niveles_alcanzados = []
            
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
                
                if palabra.nivel_jugado:
                    niveles_alcanzados.append(palabra.nivel_jugado)
            
            # Determinar el nivel máximo alcanzado
            abc_nivel_max = 'ninguno'
            if niveles_alcanzados:
                if 'dificil' in niveles_alcanzados:
                    abc_nivel_max = 'dificil'
                elif 'intermedio' in niveles_alcanzados:
                    abc_nivel_max = 'intermedio'
                elif 'facil' in niveles_alcanzados:
                    abc_nivel_max = 'facil'
            
            total_sesiones_abc = len(sesiones_por_dia)
            palabras_completadas_total = sum([s['palabras_completadas'] for s in sesiones_por_dia.values()])
            abc_tiempo_total = sum([s['tiempo_total'] for s in sesiones_por_dia.values()])
            
            abecedario_stats = {
                'total_sesiones': total_sesiones_abc,
                'palabras_completadas': palabras_completadas_total,
                'tiempo_promedio': abc_tiempo_total / total_sesiones_abc if total_sesiones_abc > 0 else 0,
                'tiempo_total': abc_tiempo_total,
                'nivel_alcanzado': abc_nivel_max
            }
            
            # Stats de Paseo
            paseo_partidas = PaseoSession.query.filter_by(user_id=user_id).all()
            
            sesiones_paseo_por_dia = {}
            paseo_niveles = []
            
            for partida in paseo_partidas:
                fecha = partida.fecha_juego
                if fecha not in sesiones_paseo_por_dia:
                    sesiones_paseo_por_dia[fecha] = {
                        'partidas_totales': 0,
                        'victorias': 0,
                        'precision_sum': 0,
                        'precision_count': 0,
                        'tiempo_total': 0
                    }
                sesiones_paseo_por_dia[fecha]['partidas_totales'] += 1
                if partida.resultado == 'victoria':
                    sesiones_paseo_por_dia[fecha]['victorias'] += 1
                if partida.precision is not None:
                    sesiones_paseo_por_dia[fecha]['precision_sum'] += partida.precision
                    sesiones_paseo_por_dia[fecha]['precision_count'] += 1
                
                # Tiempo total (usando duracion_segmento o un estimado si es nulo)
                duracion = partida.tiempo_total_sesion or partida.duracion_segmento or 0
                sesiones_paseo_por_dia[fecha]['tiempo_total'] += duracion
                
                if partida.nivel_dificultad:
                    paseo_niveles.append(partida.nivel_dificultad)

            # Nivel maximo paseo
            paseo_nivel_max = 'N/A'
            if paseo_niveles:
                if 'dificil' in paseo_niveles:
                    paseo_nivel_max = 'dificil'
                elif 'medio' in paseo_niveles:
                    paseo_nivel_max = 'medio'
                elif 'facil' in paseo_niveles:
                    paseo_nivel_max = 'facil'

            total_sesiones_paseo = len(sesiones_paseo_por_dia)
            victorias_totales = sum([s['victorias'] for s in sesiones_paseo_por_dia.values()])
            precision_total = sum([s['precision_sum'] for s in sesiones_paseo_por_dia.values()])
            precision_count_total = sum([s['precision_count'] for s in sesiones_paseo_por_dia.values()])
            paseo_tiempo_total = sum([s['tiempo_total'] for s in sesiones_paseo_por_dia.values()])
            
            paseo_stats = {
                'total_sesiones': total_sesiones_paseo,
                'victorias': victorias_totales,
                'precision_promedio': precision_total / precision_count_total if precision_count_total > 0 else 0,
                'tiempo_total': paseo_tiempo_total,
                'tiempo_promedio': paseo_tiempo_total / total_sesiones_paseo if total_sesiones_paseo > 0 else 0,
                'nivel_maximo': paseo_nivel_max
            }

            # Stats de Trenes
            train_sessions = TrainGameSession.query.filter_by(user_id=user_id).all()
            train_correct = sum([(s.correct_routing or 0) for s in train_sessions])
            train_wrong = sum([(s.wrong_routing or 0) for s in train_sessions])
            train_total_attempts = train_correct + train_wrong
            
            # Calcular tiempo total usando timestamps (started_at y finished_at)
            train_tiempo_total = 0
            for s in train_sessions:
                if s.started_at and s.finished_at:
                    duration = (s.finished_at - s.started_at).total_seconds()
                    train_tiempo_total += duration
            
            # Nivel maximo trenes - basado en configuración del usuario
            train_nivel_max = 'N/A'
            train_config = db.session.query(TrainGameConfig).filter_by(user_id=user_id).first()
            if train_config:
                train_nivel_max = train_config.difficulty_label or 'N/A'
            
            train_stats = {
                'total_sesiones': len(train_sessions),
                'total_aciertos': train_correct,
                'precision_promedio': (train_correct / train_total_attempts * 100) if train_total_attempts > 0 else 0,
                'tiempo_total': train_tiempo_total,
                'tiempo_promedio': train_tiempo_total / len(train_sessions) if train_sessions else 0,
                'nivel_maximo': train_nivel_max
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
        Obtiene sesiones de memoria agrupadas por fecha y nivel
        Estructura: Sesión (por fecha) -> Niveles -> Partidas individuales
        """
        try:
            sessions = MemoryGameSession.query.filter_by(user_id=user_id).\
                order_by(MemoryGameSession.finished_at.desc()).\
                all()
            
            # Agrupar por FECHA (sesión del día)
            sesiones_agrupadas = {}
            for session in sessions:
                # Usar finished_at o started_at para obtener la fecha
                fecha_dt = session.finished_at or session.started_at
                if not fecha_dt:
                    continue
                fecha = fecha_dt.strftime('%Y-%m-%d')
                
                if fecha not in sesiones_agrupadas:
                    sesiones_agrupadas[fecha] = {
                        'fecha': fecha,
                        'niveles': {},
                        'resumen': {
                            'total_partidas': 0,
                            'completadas': 0,
                            'accuracy_promedio': 0,
                            'tiempo_total': 0
                        }
                    }
                
                # Agrupar por NIVEL dentro de cada sesión
                nivel = session.difficulty_level or 'tutorial'
                if nivel not in sesiones_agrupadas[fecha]['niveles']:
                    sesiones_agrupadas[fecha]['niveles'][nivel] = {
                        'nivel': nivel,
                        'partidas': []
                    }
                
                # Agregar partida al nivel correspondiente
                sesiones_agrupadas[fecha]['niveles'][nivel]['partidas'].append({
                    'session_id': session.session_id,
                    'hora': fecha_dt.strftime('%H:%M:%S'),
                    'duracion': session.elapsed_time_seconds,
                    'accuracy': session.accuracy_percentage,
                    'pares_encontrados': session.pairs_found,
                    'total_pares': session.total_pairs,
                    'flips': session.total_flips,
                    'grid_size': session.grid_size,
                    'estado': session.completion_status,
                    'ai_score': session.ai_overall_score,
                    'ai_decision': session.ai_adjustment_decision,
                    'ai_memory': session.ai_memory_assessment,
                    'ai_speed': session.ai_speed_assessment
                })
                
                # Actualizar resumen de la sesión
                sesiones_agrupadas[fecha]['resumen']['total_partidas'] += 1
                if session.completion_status == 'completed':
                    sesiones_agrupadas[fecha]['resumen']['completadas'] += 1
                sesiones_agrupadas[fecha]['resumen']['accuracy_promedio'] += session.accuracy_percentage or 0
                sesiones_agrupadas[fecha]['resumen']['tiempo_total'] += session.elapsed_time_seconds or 0
            
            # Calcular promedios y convertir a lista ordenada
            sesiones_lista = []
            for fecha_key in sorted(sesiones_agrupadas.keys(), reverse=True):
                sesion = sesiones_agrupadas[fecha_key]
                
                # Calcular promedio de accuracy
                if sesion['resumen']['total_partidas'] > 0:
                    sesion['resumen']['accuracy_promedio'] /= sesion['resumen']['total_partidas']
                
                # Convertir niveles a lista ordenada
                niveles_lista = []
                for nivel_key in ['tutorial', 'easy', 'medium', 'hard']:
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

    @staticmethod
    def get_progression_stats(user_id):
        """
        GET /admin/progression-stats/<user_id>
        Obtiene el historial de niveles de dificultad por fecha para todos los juegos
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

            # Helper para formatear fecha (solo fecha, sin hora)
            def fmt_date(dt):
                return dt.strftime('%Y-%m-%d') if dt else None

            # 1. Abecedario Progression (agrupado por día)
            # Nivel: facil=0, intermedio=1, dificil=2
            abc_map = {'facil': 0, 'intermedio': 1, 'dificil': 2}
            abc_sessions = Abecedario.query.filter_by(user_id=user_id).order_by(Abecedario.created_at).all()
            abc_daily = {}
            for s in abc_sessions:
                date_str = fmt_date(s.created_at)
                if not date_str: continue
                val = abc_map.get(s.nivel_jugado or 'facil', 0)
                if date_str not in abc_daily: abc_daily[date_str] = []
                abc_daily[date_str].append(val)
            abc_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(abc_daily.items())]

            # 2. Memory Progression (agrupado por día)
            # Nivel: tutorial=0, easy=1, medium=2, hard=3
            mem_map = {'tutorial': 0, 'easy': 1, 'medium': 2, 'hard': 3}
            mem_sessions = MemoryGameSession.query.filter_by(user_id=user_id).order_by(MemoryGameSession.started_at).all()
            mem_daily = {}
            for s in mem_sessions:
                date_str = fmt_date(s.started_at)
                if not date_str: continue
                val = mem_map.get(s.difficulty_level or 'tutorial', 0)
                if date_str not in mem_daily: mem_daily[date_str] = []
                mem_daily[date_str].append(val)
            mem_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(mem_daily.items())]

            # 3. Paseo Progression (agrupado por día)
            # Nivel: facil=0, intermedio=1, dificil=2
            paseo_map = {'facil': 0, 'intermedio': 1, 'dificil': 2}
            paseo_sessions = PaseoSession.query.filter_by(user_id=user_id).order_by(PaseoSession.created_at).all()
            paseo_daily = {}
            for s in paseo_sessions:
                date_str = fmt_date(s.created_at)
                if not date_str: continue
                val = paseo_map.get(s.nivel_dificultad or 'facil', 0)
                if date_str not in paseo_daily: paseo_daily[date_str] = []
                paseo_daily[date_str].append(val)
            paseo_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(paseo_daily.items())]

            # 4. Train Progression (agrupado por día)
            # Nivel: easy=0, medium=1, hard=2 (Inferido por color_count)
            train_sessions = TrainGameSession.query.filter_by(user_id=user_id).order_by(TrainGameSession.started_at).all()
            train_daily = {}
            for s in train_sessions:
                date_str = fmt_date(s.started_at)
                if not date_str: continue
                cc = s.color_count or 3
                if cc <= 3: val = 0
                elif cc <= 5: val = 1
                else: val = 2
                if date_str not in train_daily: train_daily[date_str] = []
                train_daily[date_str].append(val)
            train_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(train_daily.items())]

            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'progression': {
                    'abecedario': abc_data,
                    'memoria': mem_data,
                    'paseo': paseo_data,
                    'trenes': train_data
                }
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def get_general_progression_stats():
        """
        GET /admin/general-progression-stats
        Obtiene el promedio de niveles de dificultad por fecha para todos los juegos (todos los usuarios)
        """
        try:
            # Helper para formatear fecha (solo día)
            def fmt_date(dt):
                return dt.strftime('%Y-%m-%d') if dt else None

            # 1. Abecedario
            abc_map = {'facil': 0, 'intermedio': 1, 'dificil': 2}
            abc_sessions = db.session.query(Abecedario.created_at, Abecedario.nivel_jugado).all()
            
            abc_daily = {}
            for s in abc_sessions:
                date_str = fmt_date(s.created_at)
                if not date_str: continue
                val = abc_map.get(s.nivel_jugado or 'facil', 0)
                if date_str not in abc_daily: abc_daily[date_str] = []
                abc_daily[date_str].append(val)
            
            abc_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(abc_daily.items())]

            # 2. Memory
            mem_map = {'tutorial': 0, 'easy': 1, 'medium': 2, 'hard': 3}
            mem_sessions = db.session.query(MemoryGameSession.started_at, MemoryGameSession.difficulty_level).all()
            
            mem_daily = {}
            for s in mem_sessions:
                date_str = fmt_date(s.started_at)
                if not date_str: continue
                val = mem_map.get(s.difficulty_level or 'tutorial', 0)
                if date_str not in mem_daily: mem_daily[date_str] = []
                mem_daily[date_str].append(val)
                
            mem_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(mem_daily.items())]

            # 3. Paseo
            paseo_map = {'facil': 0, 'intermedio': 1, 'dificil': 2}
            paseo_sessions = db.session.query(PaseoSession.created_at, PaseoSession.nivel_dificultad).all()
            
            paseo_daily = {}
            for s in paseo_sessions:
                date_str = fmt_date(s.created_at)
                if not date_str: continue
                val = paseo_map.get(s.nivel_dificultad or 'facil', 0)
                if date_str not in paseo_daily: paseo_daily[date_str] = []
                paseo_daily[date_str].append(val)
                
            paseo_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(paseo_daily.items())]

            # 4. Train
            train_sessions = db.session.query(TrainGameSession.started_at, TrainGameSession.color_count).all()
            
            train_daily = {}
            for s in train_sessions:
                date_str = fmt_date(s.started_at)
                if not date_str: continue
                cc = s.color_count or 3
                if cc <= 3: val = 0
                elif cc <= 5: val = 1
                else: val = 2
                
                if date_str not in train_daily: train_daily[date_str] = []
                train_daily[date_str].append(val)
                
            train_data = [{'date': k, 'level_value': sum(v)/len(v)} for k, v in sorted(train_daily.items())]

            return jsonify({
                'success': True,
                'progression': {
                    'abecedario': abc_data,
                    'memoria': mem_data,
                    'paseo': paseo_data,
                    'trenes': train_data
                }
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def get_indicators(user_id=None):
        """
        GET /admin/indicators o /admin/indicators/<user_id>
        Obtiene los indicadores KPI para todos los juegos
        Indicadores:
        1. Número de aciertos
        2. Tiempo promedio de resolución
        3. Nivel máximo de dificultad
        4. Número de sesiones completadas
        5. Tiempo total de interacción
        """
        try:
            # Determinar si es consulta general o por usuario
            is_general = user_id is None or user_id == 'general'
            
            # ═══════════════════════════════════════════════
            # ABECEDARIO
            # ═══════════════════════════════════════════════
            if is_general:
                abc_sessions = Abecedario.query.all()
            else:
                abc_sessions = Abecedario.query.filter_by(user_id=user_id).all()
            
            abc_total = len(abc_sessions)
            abc_aciertos = sum(1 for s in abc_sessions if s.completado)
            abc_tiempo_total = sum(s.tiempo_resolucion or 0 for s in abc_sessions)
            abc_tiempo_promedio = abc_tiempo_total / abc_total if abc_total > 0 else 0
            abc_nivel_map = {'facil': 0, 'intermedio': 1, 'dificil': 2}
            abc_nivel_max_val = max((abc_nivel_map.get(s.nivel_jugado or 'facil', 0) for s in abc_sessions), default=0)
            abc_nivel_max = {0: 'Fácil', 1: 'Intermedio', 2: 'Difícil'}.get(abc_nivel_max_val, 'Fácil')
            abc_precision = (abc_aciertos / abc_total * 100) if abc_total > 0 else 0
            
            abc_indicators = {
                'total_sesiones': abc_total,
                'aciertos': abc_aciertos,
                'precision': round(abc_precision, 1),
                'tiempo_promedio': round(abc_tiempo_promedio, 1),
                'tiempo_total': round(abc_tiempo_total / 60, 1),  # minutos
                'nivel_maximo': abc_nivel_max,
                'sesiones_completadas': abc_aciertos  # En Abecedario, completado = acierto
            }
            
            # ═══════════════════════════════════════════════
            # MEMORY
            # ═══════════════════════════════════════════════
            if is_general:
                mem_sessions = MemoryGameSession.query.all()
            else:
                mem_sessions = MemoryGameSession.query.filter_by(user_id=user_id).all()
            
            mem_total = len(mem_sessions)
            mem_completadas = sum(1 for s in mem_sessions if s.completion_status == 'completed')
            mem_aciertos = sum(s.pairs_found or 0 for s in mem_sessions)
            mem_precision_avg = sum(s.accuracy_percentage or 0 for s in mem_sessions) / mem_total if mem_total > 0 else 0
            mem_tiempo_total = sum(s.elapsed_time_seconds or 0 for s in mem_sessions)
            mem_tiempo_promedio = mem_tiempo_total / mem_total if mem_total > 0 else 0
            mem_nivel_map = {'tutorial': 0, 'easy': 1, 'medium': 2, 'hard': 3}
            mem_nivel_max_val = max((mem_nivel_map.get(s.difficulty_level or 'tutorial', 0) for s in mem_sessions), default=0)
            mem_nivel_max = {0: 'Tutorial', 1: 'Fácil', 2: 'Medio', 3: 'Difícil'}.get(mem_nivel_max_val, 'Tutorial')
            mem_score_avg = sum(s.memory_score or 0 for s in mem_sessions) / mem_total if mem_total > 0 else 0
            
            mem_indicators = {
                'total_sesiones': mem_total,
                'aciertos': mem_aciertos,  # Pares encontrados
                'precision': round(mem_precision_avg, 1),
                'tiempo_promedio': round(mem_tiempo_promedio, 1),
                'tiempo_total': round(mem_tiempo_total / 60, 1),  # minutos
                'nivel_maximo': mem_nivel_max,
                'sesiones_completadas': mem_completadas,
                'score_promedio': round(mem_score_avg, 1)
            }
            
            # ═══════════════════════════════════════════════
            # PASEO
            # ═══════════════════════════════════════════════
            if is_general:
                paseo_sessions = PaseoSession.query.all()
            else:
                paseo_sessions = PaseoSession.query.filter_by(user_id=user_id).all()
            
            paseo_total = len(paseo_sessions)
            paseo_victorias = sum(1 for s in paseo_sessions if s.resultado == 'victoria')
            paseo_aciertos = sum(s.esferas_rojas_atrapadas or 0 for s in paseo_sessions)
            paseo_errores = sum(s.esferas_azules_atrapadas or 0 for s in paseo_sessions)
            paseo_precision_avg = sum(s.precision or 0 for s in paseo_sessions) / paseo_total if paseo_total > 0 else 0
            paseo_tiempo_total = sum(s.duracion_segmento or 0 for s in paseo_sessions)
            paseo_tiempo_promedio = paseo_tiempo_total / paseo_total if paseo_total > 0 else 0
            paseo_nivel_map = {'tutorial': 0, 'facil': 1, 'intermedio': 2, 'dificil': 3}
            paseo_nivel_max_val = max((paseo_nivel_map.get(s.nivel_dificultad or 'facil', 0) for s in paseo_sessions), default=0)
            paseo_nivel_max = {0: 'Tutorial', 1: 'Fácil', 2: 'Intermedio', 3: 'Difícil'}.get(paseo_nivel_max_val, 'Fácil')
            
            paseo_indicators = {
                'total_sesiones': paseo_total,
                'aciertos': paseo_aciertos,
                'errores': paseo_errores,
                'precision': round(paseo_precision_avg, 1),
                'tiempo_promedio': round(paseo_tiempo_promedio, 1),
                'tiempo_total': round(paseo_tiempo_total / 60, 1),  # minutos
                'nivel_maximo': paseo_nivel_max,
                'sesiones_completadas': paseo_victorias,
                'victorias': paseo_victorias
            }
            
            # ═══════════════════════════════════════════════
            # TRAIN
            # ═══════════════════════════════════════════════
            if is_general:
                train_sessions = TrainGameSession.query.all()
            else:
                train_sessions = TrainGameSession.query.filter_by(user_id=user_id).all()
            
            train_total = len(train_sessions)
            train_completadas = sum(1 for s in train_sessions if s.completion_status == 'completed')
            train_aciertos = sum(s.correct_routing or 0 for s in train_sessions)
            train_errores = sum((s.wrong_routing or 0) + (s.crash_count or 0) for s in train_sessions)
            train_precision = (train_aciertos / (train_aciertos + train_errores) * 100) if (train_aciertos + train_errores) > 0 else 0
            
            # Calcular tiempo total basado en diferencia started_at y finished_at
            train_tiempo_total = 0
            for s in train_sessions:
                if s.started_at and s.finished_at:
                    delta = (s.finished_at - s.started_at).total_seconds()
                    train_tiempo_total += max(0, delta)
            
            train_tiempo_promedio = train_tiempo_total / train_total if train_total > 0 else 0
            
            # Nivel máximo basado en velocidad
            train_speeds = [s.train_speed or 1.5 for s in train_sessions]
            train_max_speed = max(train_speeds) if train_speeds else 1.5
            if train_max_speed <= 2.5:
                train_nivel_max = 'Fácil'
            elif train_max_speed <= 4.0:
                train_nivel_max = 'Medio'
            else:
                train_nivel_max = 'Difícil'
            
            train_indicators = {
                'total_sesiones': train_total,
                'aciertos': train_aciertos,
                'errores': train_errores,
                'precision': round(train_precision, 1),
                'tiempo_promedio': round(train_tiempo_promedio, 1),
                'tiempo_total': round(train_tiempo_total / 60, 1),  # minutos
                'nivel_maximo': train_nivel_max,
                'sesiones_completadas': train_completadas,
                'velocidad_maxima': round(train_max_speed, 1)
            }
            
            return jsonify({
                'success': True,
                'user_id': user_id if not is_general else 'general',
                'indicators': {
                    'abecedario': abc_indicators,
                    'memoria': mem_indicators,
                    'paseo': paseo_indicators,
                    'trenes': train_indicators
                }
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
