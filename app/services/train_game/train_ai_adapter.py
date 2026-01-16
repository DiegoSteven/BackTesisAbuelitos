"""
Servicio de adaptación de IA para Train Game - ACTUALIZADO
Implementa parámetros ADAPTATIVOS y FIJOS según BACKEND_CAMBIOS_PENDIENTES.md
"""
import os
import json
import google.generativeai as genai

# ============================================================
# VALORES FIJOS por nivel de dificultad
# ============================================================
DIFFICULTY_FIXED_VALUES = {
    "easy": {
        "total_trains": 6,
        "color_count": 3
    },
    "medium": {
        "total_trains": 8,
        "color_count": 4
    },
    "hard": {
        "total_trains": 10,
        "color_count": 5
    }
}

# ============================================================
# LÍMITES para valores ADAPTATIVOS
# ============================================================
MIN_SPEED = 3.0
MAX_SPEED = 6.0
MIN_SPAWN_RATE = 5.0
MAX_SPAWN_RATE = 10.0

# Incrementos/Decrementos
SPEED_INCREMENT = 0.3
SPEED_DECREMENT = 0.5
SPAWN_RATE_ADJUSTMENT = 0.5

# Umbrales de precisión
ACCURACY_HIGH = 85
ACCURACY_LOW = 50

# Tiempo fijo
TIME_LIMIT = 90


def get_difficulty_label(speed: float) -> str:
    """Determina la etiqueta de dificultad basada en la velocidad."""
    if speed <= 3.5:
        return "easy"
    elif speed <= 5.0:
        return "medium"
    else:
        return "hard"


class TrainAIAdapter:
    """
    Lógica de adaptación de dificultad para el Juego de Trenes.
    
    - Velocidad y Spawn Rate: ADAPTATIVOS (ajuste gradual)
    - Trenes y Colores: FIJOS según etiqueta de dificultad
    """
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_ai = True
            print("[TRAIN IA] Gemini 1.5 Flash configurado")
        else:
            print("[TRAIN IA] Sin API key. Usando lógica clásica.")
            self.use_ai = False

    def analyze_performance(self, session_data: dict, current_config: dict) -> dict:
        """
        Analiza el desempeño y retorna la nueva configuración.
        Solo usa IA para casos ambiguos (50-85% precisión).
        """
        correct = session_data.get('correct_routing', 0) or 0
        wrong = session_data.get('wrong_routing', 0) or 0
        total = session_data.get('total_spawned', correct + wrong)
        completion_status = session_data.get('completion_status', 'completed')
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Casos obvios: usar lógica clásica
        if completion_status == 'timeout':
            return self._analyze_classic(session_data, current_config)
        if accuracy < ACCURACY_LOW:
            return self._analyze_classic(session_data, current_config)
        if accuracy >= ACCURACY_HIGH:
            return self._analyze_classic(session_data, current_config)
        
        # Zona gris (50-85%): usar IA si está disponible
        if self.use_ai:
            try:
                return self._analyze_with_gemini(session_data, current_config, accuracy)
            except Exception as e:
                print(f"[TRAIN IA] Error Gemini: {e}. Usando fallback.")
                return self._analyze_classic(session_data, current_config)
        else:
            return self._analyze_classic(session_data, current_config)

    def _analyze_with_gemini(self, session_data: dict, current_config: dict, accuracy: float) -> dict:
        """Prompt optimizado para casos ambiguos."""
        current_speed = current_config.get('train_speed', MIN_SPEED) or MIN_SPEED
        current_spawn = current_config.get('spawn_rate', MAX_SPAWN_RATE) or MAX_SPAWN_RATE
        
        prompt = f"""Juego cognitivo adultos mayores. Precisión={accuracy:.0f}%, velocidad={current_speed}.
Decide: si mejora tendencia→subir, si errores frecuentes→mantener/bajar.
JSON:{{"d":"up"|"down"|"keep","r":"razón corta"}}"""
        
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        
        if '```' in response_text:
            lines = response_text.split('\n')
            response_text = '\n'.join([l for l in lines if not l.startswith('```')])
        
        result = json.loads(response_text)
        
        decision_map = {'up': 'increase_difficulty', 'down': 'decrease_difficulty', 'keep': 'maintain'}
        decision = decision_map.get(result.get('d', 'keep'), 'maintain')
        reason = result.get('r', 'Decisión basada en análisis')
        
        # Calcular nueva velocidad
        if decision == 'increase_difficulty':
            new_speed = min(current_speed + SPEED_INCREMENT, MAX_SPEED)
        elif decision == 'decrease_difficulty':
            new_speed = max(current_speed - SPEED_DECREMENT, MIN_SPEED)
        else:
            new_speed = current_speed
        
        return {
            'decision': decision,
            'reason': reason,
            'used_ai': True,
            'accuracy': accuracy,
            'next_config': self._build_next_config(round(new_speed, 1), current_spawn, decision)
        }

    def _analyze_classic(self, session_data: dict, current_config: dict) -> dict:
        """Lógica clásica basada en reglas."""
        correct = session_data.get('correct_routing', 0) or 0
        wrong = session_data.get('wrong_routing', 0) or 0
        total = session_data.get('total_spawned', correct + wrong)
        completion_status = session_data.get('completion_status', 'completed')
        current_speed = current_config.get('train_speed', MIN_SPEED) or MIN_SPEED
        current_spawn = current_config.get('spawn_rate', MAX_SPAWN_RATE) or MAX_SPAWN_RATE
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # TIMEOUT = SIEMPRE bajar
        if completion_status == 'timeout':
            decision = 'decrease_difficulty'
            reason = "Tiempo agotado. Reduciendo dificultad."
            new_speed = max(current_speed - SPEED_DECREMENT, MIN_SPEED)
        
        # Alta precisión = subir
        elif accuracy >= ACCURACY_HIGH:
            decision = 'increase_difficulty'
            reason = f"Excelente ({accuracy:.0f}%). Aumentando dificultad."
            new_speed = min(current_speed + SPEED_INCREMENT, MAX_SPEED)
        
        # Baja precisión = bajar
        elif accuracy < ACCURACY_LOW:
            decision = 'decrease_difficulty'
            reason = f"Precisión baja ({accuracy:.0f}%). Reduciendo dificultad."
            new_speed = max(current_speed - SPEED_DECREMENT, MIN_SPEED)
        
        # Zona media = mantener
        else:
            decision = 'maintain'
            reason = f"Desempeño estable ({accuracy:.0f}%). Manteniendo nivel."
            new_speed = current_speed
        
        return {
            'decision': decision,
            'reason': reason,
            'used_ai': False,
            'accuracy': accuracy,
            'next_config': self._build_next_config(round(new_speed, 1), current_spawn, decision)
        }

    def _build_next_config(self, new_speed: float, current_spawn_rate: float, decision: str) -> dict:
        """
        Construye la configuración para la próxima sesión.
        
        - Velocidad y Spawn Rate: ADAPTATIVOS (graduales)
        - Trenes y Colores: FIJOS según etiqueta de dificultad
        """
        
        # 1. Calcular nuevo spawn rate (ADAPTATIVO)
        if decision == "increase_difficulty":
            new_spawn_rate = max(current_spawn_rate - SPAWN_RATE_ADJUSTMENT, MIN_SPAWN_RATE)
        elif decision == "decrease_difficulty":
            new_spawn_rate = min(current_spawn_rate + SPAWN_RATE_ADJUSTMENT, MAX_SPAWN_RATE)
        else:
            new_spawn_rate = current_spawn_rate
        
        # 2. Determinar etiqueta de dificultad basada en velocidad
        difficulty_label = get_difficulty_label(new_speed)
        
        # 3. Obtener valores FIJOS según dificultad
        fixed_values = DIFFICULTY_FIXED_VALUES[difficulty_label]
        
        # 4. Construir configuración final
        return {
            # Valores ADAPTATIVOS (graduales)
            "train_speed": new_speed,
            "spawn_rate": round(new_spawn_rate, 1),
            
            # Valores FIJOS (según dificultad)
            "total_trains": fixed_values["total_trains"],
            "color_count": fixed_values["color_count"],
            
            # Metadata
            "time_limit": TIME_LIMIT,
            "session_duration": TIME_LIMIT,
            "difficulty_label": difficulty_label
        }

    def get_initial_config(self) -> dict:
        """Configuración inicial para un nuevo usuario."""
        return {
            "train_speed": MIN_SPEED,
            "spawn_rate": MAX_SPAWN_RATE,
            "total_trains": DIFFICULTY_FIXED_VALUES["easy"]["total_trains"],
            "color_count": DIFFICULTY_FIXED_VALUES["easy"]["color_count"],
            "time_limit": TIME_LIMIT,
            "session_duration": TIME_LIMIT,
            "difficulty_label": "easy"
        }
