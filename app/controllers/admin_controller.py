"""
Controlador para endpoints administrativos
"""
from flask import jsonify
from models.user import User
from models.memory_game import MemoryGameSession, MemoryGameConfig
from models.abecedario import Abecedario
from datetime import datetime, timedelta
from sqlalchemy import func

class AdminController:
    @staticmethod
    def get_abecedario_sessions():
        """
        GET /admin/abecedario-sessions
        Obtiene todas las sesiones de Abecedario (últimas 20)
        """
        try:
            sessions = Abecedario.query.\
                order_by(Abecedario.created_at.desc()).\
                limit(20).\
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
    def get_memory_sessions():
        """
        GET /admin/memory-sessions
        Obtiene todas las sesiones de Memory Game (últimas 20)
        """
        try:
            sessions = MemoryGameSession.query.\
                order_by(MemoryGameSession.finished_at.desc()).\
                limit(20).\
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
    def get_admin_stats():
        """
        GET /admin/stats
        Obtiene estadísticas globales del sistema
        """
        try:
            # Total de sesiones
            total_sessions = MemoryGameSession.query.count()
            
            # Sesiones de hoy
            today = datetime.utcnow().date()
            sessions_today = MemoryGameSession.query.filter(
                func.date(MemoryGameSession.finished_at) == today
            ).count()
            
            # Accuracy promedio
            avg_accuracy = MemoryGameSession.query.\
                filter(MemoryGameSession.accuracy_percentage != None).\
                with_entities(func.avg(MemoryGameSession.accuracy_percentage)).\
                scalar()
            
            return jsonify({
                'success': True,
                'total_sessions': total_sessions,
                'sessions_today': sessions_today,
                'average_accuracy': float(avg_accuracy) if avg_accuracy else 0
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
