"""
Modelos de base de datos para el juego de trenes (Switching Game)
"""
from datetime import datetime
from config.database import db

class TrainGameSession(db.Model):
    __tablename__ = 'train_game_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), default='train_switching')
    
    # Configuración usada
    train_speed = db.Column(db.Float)
    color_count = db.Column(db.Integer)
    spawn_rate = db.Column(db.Float)
    
    # Métricas
    total_spawned = db.Column(db.Integer, default=0)
    correct_routing = db.Column(db.Integer, default=0) # Trenes a estación correcta
    wrong_routing = db.Column(db.Integer, default=0)   # Trenes a estación incorrecta
    crash_count = db.Column(db.Integer, default=0)     # Choques (opcional)
    completion_status = db.Column(db.String(20))       # completed, timeout, abandoned
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    
    # Relación
    user = db.relationship('User', backref=db.backref('train_sessions', lazy=True))
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'train_speed': self.train_speed,
            'color_count': self.color_count,
            'spawn_rate': self.spawn_rate,
            'total_spawned': self.total_spawned,
            'correct_routing': self.correct_routing,
            'wrong_routing': self.wrong_routing,
            'crash_count': self.crash_count,
            'completion_status': self.completion_status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }


class TrainGameConfig(db.Model):
    __tablename__ = 'train_game_configs'
    
    config_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Configuración Adaptativa
    train_speed = db.Column(db.Float, default=3.0)
    spawn_rate = db.Column(db.Float, default=10.0)
    
    # Configuración Fija (basada en dificultad)
    total_trains = db.Column(db.Integer, default=6)
    color_count = db.Column(db.Integer, default=3)
    time_limit = db.Column(db.Integer, default=90)
    difficulty_label = db.Column(db.String(20), default='easy')
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    user = db.relationship('User', backref=db.backref('train_config', uselist=False))
    
    def to_dict(self):
        return {
            'train_speed': self.train_speed,
            'spawn_rate': self.spawn_rate,
            'total_trains': self.total_trains,
            'color_count': self.color_count,
            'time_limit': self.time_limit,
            'session_duration': self.time_limit,
            'difficulty_label': self.difficulty_label
        }
