# 🎮 Guía de Implementación Backend - Juego de Memoria

## 📋 Índice
1. [Estructura de Archivos](#estructura-de-archivos)
2. [Base de Datos](#base-de-datos)
3. [Modelos](#modelos)
4. [Servicios](#servicios)
5. [Controladores](#controladores)
6. [Rutas](#rutas)
7. [Testing](#testing)

---

## 📁 Estructura de Archivos

Añade estos archivos a tu backend siguiendo la estructura existente:

```
BackTesisAbuelitos/
└── app/
    ├── models/
    │   └── memory_game.py          [NUEVO]
    ├── services/
    │   └── memory_game/            [NUEVA CARPETA]
    │       ├── __init__.py
    │       ├── memory_game_service.py
    │       └── ai_adapter_service.py
    └── controllers/
        └── memory_game_controller.py [NUEVO]
```

---

## 💾 Base de Datos

### Tablas a Crear

#### 1. `memory_game_sessions`
Almacena cada sesión de juego completada.

```sql
CREATE TABLE memory_game_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    game_type VARCHAR(50) DEFAULT 'memory_cards',
    
    -- Configuración
    difficulty_level VARCHAR(20),
    total_pairs INT NOT NULL,
    grid_size VARCHAR(10),
    
    -- Métricas
    total_flips INT DEFAULT 0,
    pairs_found INT DEFAULT 0,
    elapsed_time_seconds FLOAT,
    completion_status VARCHAR(20),
    accuracy_percentage FLOAT,
    memory_score FLOAT,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### 2. `memory_game_configs`
Una fila por usuario con su configuración actual.

```sql
CREATE TABLE memory_game_configs (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    
    -- Configuración
    total_pairs INT DEFAULT 3,
    grid_size VARCHAR(10) DEFAULT '2x3',
    time_limit INT DEFAULT 60,
    memorization_time INT DEFAULT 5,
    difficulty_label VARCHAR(20) DEFAULT 'tutorial',
    
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

---

## 🗂️ Modelos

### Archivo: `app/models/memory_game.py`

```python
"""
Modelos de base de datos para el juego de memoria
"""
from datetime import datetime
from app.config.database import db

class MemoryGameSession(db.Model):
    __tablename__ = 'memory_game_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
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
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }


class MemoryGameConfig(db.Model):
    __tablename__ = 'memory_game_configs'
    
    config_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    
    # Configuración
    total_pairs = db.Column(db.Integer, default=3)
    grid_size = db.Column(db.String(10), default='2x3')
    time_limit = db.Column(db.Integer, default=60)
    memorization_time = db.Column(db.Integer, default=5)
    difficulty_label = db.Column(db.String(20), default='tutorial')
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    user = db.relationship('User', backref=db.backref('memory_config', uselist=False))
    
    def to_dict(self):
        return {
            'total_pairs': self.total_pairs,
            'grid_size': self.grid_size,
            'time_limit': self.time_limit,
            'memorization_time': self.memorization_time,
            'difficulty_label': self.difficulty_label
        }
```

---

## ⚙️ Servicios

### Archivo: `app/services/memory_game/__init__.py`

```python
from .memory_game_service import MemoryGameService
from .ai_adapter_service import AIAdapterService

__all__ = ['MemoryGameService', 'AIAdapterService']
```

### Archivo: `app/services/memory_game/memory_game_service.py`

```python
"""
Servicio de lógica de negocio para el juego de memoria
"""
from datetime import datetime
from app.config.database import db
from app.models.memory_game import MemoryGameSession, MemoryGameConfig
from .ai_adapter_service import AIAdapterService

class MemoryGameService:
    def __init__(self):
        self.ai_adapter = AIAdapterService()
    
    def get_user_config(self, user_id: int) -> dict:
        """
        Obtiene la configuración actual del usuario.
        Si no existe, crea una con valores por defecto.
        """
        config = MemoryGameConfig.query.filter_by(user_id=user_id).first()
        
        if not config:
            # Crear configuración por defecto
            config = MemoryGameConfig(user_id=user_id)
            db.session.add(config)
            db.session.commit()
            is_first_time = True
        else:
            is_first_time = False
        
        return {
            'user_id': user_id,
            'current_config': config.to_dict(),
            'is_first_time': is_first_time,
            'last_updated': config.last_updated.isoformat()
        }
    
    def save_session_and_analyze(self, user_id: int, session_data: dict) -> dict:
        """
        Guarda la sesión y usa IA para generar nueva configuración
        """
        # 1. Obtener configuración actual
        current_config = MemoryGameConfig.query.filter_by(user_id=user_id).first()
        if not current_config:
            current_config = MemoryGameConfig(user_id=user_id)
            db.session.add(current_config)
            db.session.commit()
        
        # 2. Guardar sesión
        session = MemoryGameSession(
            user_id=user_id,
            difficulty_level=current_config.difficulty_label,
            total_pairs=session_data.get('total_pairs'),
            grid_size=current_config.grid_size,
            total_flips=session_data.get('total_flips'),
            pairs_found=session_data.get('pairs_found'),
            elapsed_time_seconds=session_data.get('elapsed_time'),
            completion_status=session_data.get('completion_status'),
            accuracy_percentage=session_data.get('accuracy'),
            finished_at=datetime.utcnow()
        )
        
        # Calcular memory score simple
        session.memory_score = self._calculate_memory_score(session_data)
        
        db.session.add(session)
        db.session.commit()
        
        # 3. Analizar con IA y obtener nueva configuración
        ai_analysis = self.ai_adapter.analyze_and_recommend(
            session_data, 
            current_config.difficulty_label
        )
        
        # 4. Actualizar configuración del usuario
        new_config = ai_analysis['next_session_config']
        current_config.total_pairs = new_config['total_pairs']
        current_config.grid_size = new_config['grid_size']
        current_config.time_limit = new_config['time_limit']
        current_config.memorization_time = new_config['memorization_time']
        current_config.difficulty_label = new_config['difficulty_label']
        
        db.session.commit()
        
        return {
            'session_saved': True,
            'session_id': session.session_id,
            'ai_analysis': ai_analysis
        }
    
    def _calculate_memory_score(self, session_data: dict) -> float:
        """
        Calcula un score de memoria (0-10)
        """
        if session_data.get('completion_status') != 'completed':
            return 0.0
        
        accuracy = session_data.get('accuracy', 0)
        return min(accuracy / 10, 10)
    
    def get_user_stats(self, user_id: int) -> dict:
        """
        Obtiene estadísticas del usuario
        """
        sessions = MemoryGameSession.query.filter_by(user_id=user_id).all()
        
        if not sessions:
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'average_accuracy': 0,
                'best_time': None
            }
        
        completed = [s for s in sessions if s.completion_status == 'completed']
        
        return {
            'total_sessions': len(sessions),
            'completed_sessions': len(completed),
            'average_accuracy': sum(s.accuracy_percentage or 0 for s in completed) / len(completed) if completed else 0,
            'best_time': min(s.elapsed_time_seconds for s in completed) if completed else None,
            'recent_sessions': [s.to_dict() for s in sessions[-5:]]
        }
```

### Archivo: `app/services/memory_game/ai_adapter_service.py`

```python
"""
Servicio de adaptación de IA
"""
from typing import Dict, Any

class AIAdapterService:
    # Configuraciones predefinidas
    DIFFICULTY_CONFIGS = {
        'tutorial': {
            'total_pairs': 3,
            'grid_size': '2x3',
            'time_limit': 60,
            'memorization_time': 5
        },
        'easy': {
            'total_pairs': 4,
            'grid_size': '2x4',
            'time_limit': 90,
            'memorization_time': 4
        },
        'medium': {
            'total_pairs': 6,
            'grid_size': '3x4',
            'time_limit': 120,
            'memorization_time': 3
        },
        'hard': {
            'total_pairs': 8,
            'grid_size': '4x4',
            'time_limit': 180,
            'memorization_time': 2
        }
    }
    
    DIFFICULTY_PROGRESSION = ['tutorial', 'easy', 'medium', 'hard']
    
    def analyze_and_recommend(self, session_data: Dict, current_difficulty: str) -> Dict:
        """
        Analiza desempeño y recomienda nueva configuración
        """
        # 1. Evaluar desempeño (0-10)
        score = self._evaluate_performance(session_data)
        
        # 2. Decidir ajuste
        adjustment = self._decide_adjustment(score)
        
        # 3. Generar nueva configuración
        new_difficulty = self._get_next_difficulty(current_difficulty, adjustment)
        new_config = self.DIFFICULTY_CONFIGS[new_difficulty].copy()
        
        # 4. Generar análisis
        return {
            'performance_assessment': {
                'overall_score': score,
                'memory_retention': self._get_memory_level(score),
                'speed': self._get_speed_level(score),
                'accuracy': self._get_accuracy_level(score)
            },
            'adjustment_decision': adjustment,
            'next_session_config': {
                **new_config,
                'difficulty_label': new_difficulty
            },
            'reason': self._generate_reason(score, adjustment, current_difficulty, new_difficulty),
            'adjustment_summary': {
                'changed_fields': self._get_changed_fields(current_difficulty, new_difficulty),
                'previous_difficulty': current_difficulty,
                'new_difficulty': new_difficulty
            }
        }
    
    def _evaluate_performance(self, session_data: Dict) -> float:
        """Score de 0-10"""
        if session_data['completion_status'] != 'completed':
            return 2.0
        
        # Accuracy (60%)
        accuracy_score = min(session_data.get('accuracy', 0) / 10, 10)
        
        # Tiempo (40%)
        time_ratio = session_data['elapsed_time'] / session_data['time_limit']
        if time_ratio < 0.5:
            time_score = 10
        elif time_ratio < 0.75:
            time_score = 8
        elif time_ratio < 1.0:
            time_score = 6
        else:
            time_score = 3
        
        return round((accuracy_score * 0.6) + (time_score * 0.4), 1)
    
    def _decide_adjustment(self, score: float) -> str:
        if score >= 8.0:
            return "increase_difficulty"
        elif score >= 5.0:
            return "keep_same"
        else:
            return "decrease_difficulty"
    
    def _get_next_difficulty(self, current: str, adjustment: str) -> str:
        if adjustment == "keep_same":
            return current
        
        try:
            idx = self.DIFFICULTY_PROGRESSION.index(current)
        except ValueError:
            return 'tutorial'
        
        if adjustment == "increase_difficulty":
            idx = min(idx + 1, len(self.DIFFICULTY_PROGRESSION) - 1)
        else:
            idx = max(idx - 1, 0)
        
        return self.DIFFICULTY_PROGRESSION[idx]
    
    def _get_memory_level(self, score: float) -> str:
        if score >= 8.0:
            return "high"
        elif score >= 6.0:
            return "good"
        elif score >= 4.0:
            return "medium"
        return "low"
    
    def _get_speed_level(self, score: float) -> str:
        return self._get_memory_level(score)  # Mismo criterio
    
    def _get_accuracy_level(self, score: float) -> str:
        return self._get_memory_level(score)
    
    def _generate_reason(self, score: float, adjustment: str, old: str, new: str) -> str:
        reasons = {
            "increase_difficulty": f"Excelente desempeño (score {score}/10). Listo para más desafío.",
            "keep_same": f"Buen desempeño (score {score}/10). Mantener nivel actual.",
            "decrease_difficulty": f"Desempeño bajo (score {score}/10). Reducir dificultad."
        }
        
        base = reasons.get(adjustment, "Ajuste recomendado")
        if old != new:
            base += f" Cambiando de {old} a {new}."
        return base
    
    def _get_changed_fields(self, old: str, new: str) -> list:
        if old == new:
            return []
        
        old_config = self.DIFFICULTY_CONFIGS[old]
        new_config = self.DIFFICULTY_CONFIGS[new]
        
        return [k for k in old_config if old_config[k] != new_config[k]]
```

---

## 🎛️ Controladores

### Archivo: `app/controllers/memory_game_controller.py`

```python
"""
Controlador de endpoints para el juego de memoria
"""
from flask import Blueprint, request, jsonify
from app.services.memory_game import MemoryGameService
from datetime import datetime

memory_game_bp = Blueprint('memory_game', __name__, url_prefix='/api/memory-game')

service = MemoryGameService()

@memory_game_bp.route('/config/<int:user_id>', methods=['GET'])
def get_config(user_id):
    """
    GET /api/memory-game/config/{user_id}
    Obtiene la configuración actual del usuario
    """
    try:
        data = service.get_user_config(user_id)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@memory_game_bp.route('/submit-results', methods=['POST'])
def submit_results():
    """
    POST /api/memory-game/submit-results
    Envía resultados de sesión y obtiene nueva configuración con análisis de IA
    
    Body:
    {
        "user_id": 1,
        "session_data": {
            "completion_status": "completed",
            "total_flips": 12,
            "pairs_found": 3,
            "total_pairs": 3,
            "elapsed_time": 45.5,
            "time_limit": 60,
            "accuracy": 75.0
        }
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        session_data = data.get('session_data')
        
        if not user_id or not session_data:
            return jsonify({
                'success': False,
                'error': 'Missing user_id or session_data'
            }), 400
        
        result = service.save_session_and_analyze(user_id, session_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@memory_game_bp.route('/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    """
    GET /api/memory-game/stats/{user_id}
    Obtiene estadísticas del usuario
    """
    try:
        stats = service.get_user_stats(user_id)
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## 🚀 Rutas

### Archivo: `app/app.py`

Añade estas líneas al archivo principal:

```python
# Importar el blueprint
from app.controllers.memory_game_controller import memory_game_bp

# Registrar el blueprint
app.register_blueprint(memory_game_bp)
```

---

## 🗄️ Migración de Base de Datos

### Opción 1: SQL Manual

Ejecuta este script SQL en tu base de datos:

```sql
-- Crear tabla de sesiones
CREATE TABLE IF NOT EXISTS memory_game_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    game_type VARCHAR(50) DEFAULT 'memory_cards',
    difficulty_level VARCHAR(20),
    total_pairs INT NOT NULL,
    grid_size VARCHAR(10),
    total_flips INT DEFAULT 0,
    pairs_found INT DEFAULT 0,
    elapsed_time_seconds FLOAT,
    completion_status VARCHAR(20),
    accuracy_percentage FLOAT,
    memory_score FLOAT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Crear tabla de configuraciones
CREATE TABLE IF NOT EXISTS memory_game_configs (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    total_pairs INT DEFAULT 3,
    grid_size VARCHAR(10) DEFAULT '2x3',
    time_limit INT DEFAULT 60,
    memorization_time INT DEFAULT 5,
    difficulty_label VARCHAR(20) DEFAULT 'tutorial',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### Opción 2: Script Python

Archivo: `app/create_memory_tables.py`

```python
from app import app
from app.config.database import db
from app.models.memory_game import MemoryGameSession, MemoryGameConfig

with app.app_context():
    # Crear tablas
    db.create_all()
    print("✅ Tablas de juego de memoria creadas")
```

Ejecutar:
```bash
python -m app.create_memory_tables
```

---

## 🧪 Testing

### Endpoints Disponibles

#### 1. Obtener Configuración
```bash
GET http://localhost:5000/api/memory-game/config/1
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "current_config": {
      "total_pairs": 3,
      "grid_size": "2x3",
      "time_limit": 60,
      "memorization_time": 5,
      "difficulty_label": "tutorial"
    },
    "is_first_time": true,
    "last_updated": "2025-12-15T20:00:00"
  }
}
```

#### 2. Enviar Resultados
```bash
POST http://localhost:5000/api/memory-game/submit-results
Content-Type: application/json

{
  "user_id": 1,
  "session_data": {
    "completion_status": "completed",
    "total_flips": 12,
    "pairs_found": 3,
    "total_pairs": 3,
    "elapsed_time": 45.5,
    "time_limit": 60,
    "accuracy": 75.0
  }
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "session_saved": true,
    "session_id": 1,
    "ai_analysis": {
      "performance_assessment": {
        "overall_score": 8.5,
        "memory_retention": "high",
        "speed": "good",
        "accuracy": "good"
      },
      "adjustment_decision": "increase_difficulty",
      "next_session_config": {
        "total_pairs": 4,
        "grid_size": "2x4",
        "time_limit": 90,
        "memorization_time": 4,
        "difficulty_label": "easy"
      },
      "reason": "Excelente desempeño...",
      "adjustment_summary": {
        "changed_fields": ["total_pairs", "grid_size"],
        "previous_difficulty": "tutorial",
        "new_difficulty": "easy"
      }
    }
  },
  "timestamp": "2025-12-15T20:00:00Z"
}
```

---

## ✅ Checklist de Implementación

- [ ] Crear archivo `app/models/memory_game.py`
- [ ] Crear carpeta `app/services/memory_game/`
- [ ] Crear archivo `app/services/memory_game/__init__.py`
- [ ] Crear archivo `app/services/memory_game/memory_game_service.py`
- [ ] Crear archivo `app/services/memory_game/ai_adapter_service.py`
- [ ] Crear archivo `app/controllers/memory_game_controller.py`
- [ ] Registrar blueprint en `app/app.py`
- [ ] Crear tablas en la base de datos
- [ ] Probar endpoint de configuración
- [ ] Probar endpoint de resultados
- [ ] Verificar que Unity puede conectarse

---

## 🔧 Troubleshooting

### Error: "Table doesn't exist"
Asegúrate de ejecutar el script de creación de tablas.

### Error: "CORS policy"
Añade Flask-CORS si aún no está:
```python
from flask_cors import CORS
CORS(app)
```

### Error: "Foreign key constraint"
Verifica que la tabla `users` existe y tiene el campo `user_id`.

---

¡Implementación completa! 🎉
