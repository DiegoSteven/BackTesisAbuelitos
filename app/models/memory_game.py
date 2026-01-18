"""
Modelos de base de datos para el juego de memoria
"""
from datetime import datetime
from config.database import db

class MemoryGameSession(db.Model):
    __tablename__ = 'memory_game_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), default='memory_cards')
    
    # Configuración
    difficulty_level = db.Column(db.String(20))
    total_pairs = db.Column(db.Integer, nullable=False)
    grid_size = db.Column(db.String(10))
    
    # Métricas
    total_flips = db.Column(db.Integer, default=0)
    pairs_found = db.Column(db.Integer, default=0)
    elapsed_time_seconds = db.Column(db.Float)
    completion_status = db.Column(db.String(20))
    accuracy_percentage = db.Column(db.Float)
    memory_score = db.Column(db.Float)
    
    # Métricas de IA (para seguimiento del terapeuta)
    ai_adjustment_decision = db.Column(db.String(20))  # increase, decrease, maintain
    ai_reason = db.Column(db.String(500))  # Razón del ajuste
    ai_memory_assessment = db.Column(db.String(20))  # low, medium, high
    ai_speed_assessment = db.Column(db.String(20))  # slow, normal, fast
    ai_accuracy_assessment = db.Column(db.String(20))  # low, medium, high
    ai_overall_score = db.Column(db.Float)  # 0-10
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    
    # Relación
    user = db.relationship('User', backref=db.backref('memory_sessions', lazy=True))
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'difficulty_level': self.difficulty_level,
            'total_pairs': self.total_pairs,
            'grid_size': self.grid_size,
            'total_flips': self.total_flips,
            'pairs_found': self.pairs_found,
            'elapsed_time': self.elapsed_time_seconds,
            'completion_status': self.completion_status,
            'accuracy': self.accuracy_percentage,
            'memory_score': self.memory_score,
            'ai_metrics': {
                'adjustment_decision': self.ai_adjustment_decision,
                'reason': self.ai_reason,
                'memory': self.ai_memory_assessment,
                'speed': self.ai_speed_assessment,
                'accuracy': self.ai_accuracy_assessment,
                'overall_score': self.ai_overall_score
            },
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }


class MemoryGameConfig(db.Model):
    __tablename__ = 'memory_game_configs'
    
    config_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Configuración
    total_pairs = db.Column(db.Integer, default=3)
    grid_size = db.Column(db.String(10), default='2x3')
    time_limit = db.Column(db.Integer, default=60)
    memorization_time = db.Column(db.Integer, default=5)
    difficulty_label = db.Column(db.String(20), default='tutorial')
    
    # Contador de sesiones consecutivas en "MAINTAIN" (para micro-ajustes)
    consecutive_maintains = db.Column(db.Integer, default=0)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    user = db.relationship('User', backref=db.backref('memory_config', uselist=False))
    
    def to_dict(self):
        return {
            'total_pairs': self.total_pairs,
            'grid_size': self.grid_size,
            'time_limit': self.time_limit,
            'memorization_time': self.memorization_time,
            'difficulty_label': self.difficulty_label,
            'consecutive_maintains': self.consecutive_maintains
        }
