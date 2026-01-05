from config.database import db
from datetime import datetime

class PaseoSession(db.Model):
    """
    Modelo para sesiones del Juego de Paseo Adaptativo
    Almacena métricas de cada sesión completa (3 minutos)
    """
    __tablename__ = 'paseo_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Timestamp de la sesión
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_juego = db.Column(db.Date, default=datetime.utcnow)
    
    # Configuración aplicada en esta sesión (FIJA durante 3 min)
    velocidad_esferas = db.Column(db.Float, nullable=False)
    intervalo_spawn = db.Column(db.Float, nullable=False)
    colores_activos = db.Column(db.String(50))  # "rojo" | "rojo,azul" | "todos"
    color_correcto = db.Column(db.String(20))   # Color a atrapar (FIJO)
    
    # ==================== MÉTRICAS DE RENDIMIENTO ====================
    # Duración de la sesión
    duracion_segmento = db.Column(db.Float, nullable=False)  # Por segmento (30s)
    tiempo_total_sesion = db.Column(db.Float)                 # Total al finalizar (180s)
    
    # Aciertos y errores diferenciados
    esferas_rojas_atrapadas = db.Column(db.Integer, default=0)     # Legacy: aciertos
    esferas_azules_atrapadas = db.Column(db.Integer, default=0)    # Legacy: errores
    esferas_perdidas = db.Column(db.Integer, default=0)            # No atrapadas
    
    # Métricas calculadas
    precision = db.Column(db.Float)                          # % aciertos
    tiempo_reaccion_promedio = db.Column(db.Float)           # Tiempo promedio
    
    # Estado del juego
    fase = db.Column(db.String(20))                          # "tutorial" | "adaptativo"
    nivel_dificultad = db.Column(db.String(20))              # "facil" | "intermedio" | "dificil"
    
    # ==================== NUEVOS CAMPOS ====================
    sesion_completa = db.Column(db.Boolean, default=False)   # True = sesión finalizada
    ajustado_por_ia = db.Column(db.Boolean, default=False)   # Si fue planificada por IA
    recomendacion_siguiente = db.Column(db.String(500))      # Plan para próxima sesión
    
    # ✅ Nuevos campos para sistema de sub-sesiones
    resultado = db.Column(db.String(20))  # "victoria", "derrota_timeout", "derrota_errores", "derrota_abandono"
    meta_aciertos = db.Column(db.Integer)  # 15 (facil), 20 (intermedio), 30 (dificil)
    razon_derrota = db.Column(db.String(50))  # "timeout", "errores_excesivos", "abandono", null
    cambio_nivel = db.Column(db.Boolean, default=False)  # ✅ Flag para detectar cambios de nivel
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'fecha_juego': self.fecha_juego.isoformat(),
            'velocidad_esferas': self.velocidad_esferas,
            'intervalo_spawn': self.intervalo_spawn,
            'colores_activos': self.colores_activos,
            'color_correcto': self.color_correcto,
            'duracion_segmento': self.duracion_segmento,
            'tiempo_total_sesion': self.tiempo_total_sesion,
            'esferas_rojas_atrapadas': self.esferas_rojas_atrapadas,
            'esferas_azules_atrapadas': self.esferas_azules_atrapadas,
            'esferas_perdidas': self.esferas_perdidas,
            'precision': self.precision,
            'tiempo_reaccion_promedio': self.tiempo_reaccion_promedio,
            'fase': self.fase,
            'nivel_dificultad': self.nivel_dificultad,
            'sesion_completa': self.sesion_completa,
            'ajustado_por_ia': self.ajustado_por_ia,
            'recomendacion_siguiente': self.recomendacion_siguiente,
            'resultado': self.resultado,
            'meta_aciertos': self.meta_aciertos,
            'razon_derrota': self.razon_derrota,
            'cambio_nivel': self.cambio_nivel
        }
    
    @staticmethod
    def to_collection_dict(sesiones):
        return [sesion.to_dict() for sesion in sesiones]
