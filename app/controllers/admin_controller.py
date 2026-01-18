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
            
            # Stats de Abecedario  
            abecedario_sessions = Abecedario.query.filter_by(user_id=user_id).all()
            abecedario_stats = {
                'total_sesiones': len(abecedario_sessions),
                'palabras_completadas': sum([1 for s in abecedario_sessions if s.completado]),
                'tiempo_promedio': sum([s.tiempo_resolucion for s in abecedario_sessions]) / len(abecedario_sessions) if abecedario_sessions else 0
            }
            
            # Stats de Paseo
            paseo_sessions = PaseoSession.query.filter_by(user_id=user_id).all()
            paseo_stats = {
                'total_sesiones': len(paseo_sessions),
                'victorias': sum([1 for s in paseo_sessions if s.resultado == 'victoria']),
                'precision_promedio': sum([s.precision or 0 for s in paseo_sessions]) / len(paseo_sessions) if paseo_sessions else 0
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
        Obtiene todas las sesiones de abecedario de un usuario específico
        """
        try:
            sessions = Abecedario.query.filter_by(user_id=user_id).\
                order_by(Abecedario.created_at.desc()).\
                all()
            
            return jsonify({
                'success': True,
                'sessions': Abecedario.to_collection_dict(sessions)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_user_paseo_sessions(user_id):
        """
        GET /admin/user-paseo-sessions/<user_id>
        Obtiene todas las sesiones de paseo de un usuario específico
        """
        try:
            sessions = PaseoSession.query.filter_by(user_id=user_id).\
                order_by(PaseoSession.created_at.desc()).\
                all()
            
            return jsonify({
                'success': True,
                'sessions': PaseoSession.to_collection_dict(sessions)
            }), 200
        except Exception as e:
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
            abecedario_count = Abecedario.query.count()
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

            sessions_today = (
                count_today(MemoryGameSession, MemoryGameSession.finished_at) +
                count_today(Abecedario, Abecedario.created_at) +
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
                
                count = (
                    count_day(MemoryGameSession, MemoryGameSession.finished_at) +
                    count_day(Abecedario, Abecedario.created_at) +
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
