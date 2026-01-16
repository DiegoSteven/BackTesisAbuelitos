from models.train_game import TrainGameSession, TrainGameConfig
from .train_ai_adapter import TrainAIAdapter
from config.database import db
from datetime import datetime

class TrainGameService:
    def __init__(self):
        self.ai_adapter = TrainAIAdapter()
        
    def get_config(self, user_id):
        """Obtiene o crea la configuración para un usuario"""
        config = TrainGameConfig.query.filter_by(user_id=user_id).first()
        
        if not config:
            # Configuración inicial (Nivel Fácil)
            initial = self.ai_adapter.get_initial_config()
            config = TrainGameConfig(
                user_id=user_id,
                train_speed=initial['train_speed'],
                spawn_rate=initial['spawn_rate'],
                total_trains=initial['total_trains'],
                color_count=initial['color_count'],
                time_limit=initial['time_limit'],
                difficulty_label=initial['difficulty_label']
            )
            db.session.add(config)
            db.session.commit()
            
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "current_config": config.to_dict()
            }
        }
        
    def submit_results(self, user_id, session_data):
        """Guarda resultados y calcula nueva dificultad"""
        
        # 1. Obtener Config Actual PRIMERO (para guardar en la sesión)
        current_config_db = TrainGameConfig.query.filter_by(user_id=user_id).first()
        if not current_config_db:
            initial = self.ai_adapter.get_initial_config()
            current_config_db = TrainGameConfig(
                user_id=user_id,
                train_speed=initial['train_speed'],
                spawn_rate=initial['spawn_rate'],
                total_trains=initial['total_trains'],
                color_count=initial['color_count'],
                time_limit=initial['time_limit'],
                difficulty_label=initial['difficulty_label']
            )
            db.session.add(current_config_db)
            db.session.commit()
        
        # 2. Guardar Sesión con valores de la config actual
        new_session = TrainGameSession(
            user_id=user_id,
            train_speed=current_config_db.train_speed,  # Usar config actual
            color_count=current_config_db.color_count,  # Usar config actual
            spawn_rate=current_config_db.spawn_rate,    # Usar config actual
            total_spawned=session_data.get('total_spawned', 0),
            correct_routing=session_data.get('correct_routing', 0),
            wrong_routing=session_data.get('wrong_routing', 0),
            crash_count=session_data.get('crash_count', 0),
            completion_status=session_data.get('completion_status', 'unknown'),
            finished_at=datetime.utcnow()
        )
        
        db.session.add(new_session)
        
        current_config_dict = current_config_db.to_dict()
        
        # 3. Análisis de IA
        analysis = self.ai_adapter.analyze_performance(session_data, current_config_dict)
        
        # 4. Actualizar Configuración en BD
        next_config = analysis['next_config']
        current_config_db.train_speed = next_config['train_speed']
        current_config_db.spawn_rate = next_config['spawn_rate']
        current_config_db.total_trains = next_config['total_trains']
        current_config_db.color_count = next_config['color_count']
        current_config_db.time_limit = next_config['time_limit']
        current_config_db.difficulty_label = next_config['difficulty_label']
        current_config_db.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return {
            "success": True,
            "data": {
                "session_id": new_session.session_id,
                "ai_analysis": analysis
            }
        }
        
    def get_stats(self, user_id):
        """Obtiene estadísticas acumuladas"""
        sessions = TrainGameSession.query.filter_by(user_id=user_id).all()
        
        total_sessions = len(sessions)
        if total_sessions == 0:
            return {"success": True, "data": {"total_sessions": 0}}
            
        total_correct = sum(s.correct_routing for s in sessions)
        total_wrong = sum(s.wrong_routing for s in sessions)
        total_attempts = total_correct + total_wrong
        
        avg_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_sessions": total_sessions,
                "total_trains_routed": total_correct,
                "average_accuracy": round(avg_accuracy, 1),
                "recent_sessions": [s.to_dict() for s in sessions[-5:]] # Últimas 5
            }
        }
