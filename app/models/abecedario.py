from config.database import db
from datetime import datetime

class Abecedario(db.Model):
    __tablename__ = 'abecedario_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Datos de la palabra jugada
    palabra_objetivo = db.Column(db.String(50), nullable=False)
    longitud_palabra = db.Column(db.Integer, nullable=False)
    
    # Métricas de desempeño
    tiempo_resolucion = db.Column(db.Float, nullable=False)  # en segundos
    cantidad_errores = db.Column(db.Integer, default=0)
    pistas_usadas = db.Column(db.Integer, default=0)
    completado = db.Column(db.Boolean, default=False)
    nivel_jugado = db.Column(db.String(20), default='facil')  # Nivel en que se jugó
    cambio_nivel = db.Column(db.Boolean, default=False)  # Marca cuando hubo cambio de nivel
    
    
    # Fecha y hora
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_juego = db.Column(db.Date, nullable=False)  # Para agrupar por día
    
    # Relación con usuario
    user = db.relationship('User', backref='word_sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'palabra_objetivo': self.palabra_objetivo,
            'longitud_palabra': self.longitud_palabra,
            'tiempo_resolucion': self.tiempo_resolucion,
            'cantidad_errores': self.cantidad_errores,
            'pistas_usadas': self.pistas_usadas,
            'completado': self.completado,
            'created_at': self.created_at.isoformat(),
            'fecha_juego': self.fecha_juego.isoformat()
        }
    
    @staticmethod
    def to_collection_dict(items):
        return [item.to_dict() for item in items]
