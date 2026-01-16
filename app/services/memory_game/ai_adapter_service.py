"""
Servicio de adaptación de IA para Memory Game usando Gemini
"""
import google.generativeai as genai
import os
import json
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# CONFIGURACIÓN DE NIVELES (Referencia para Fallback y Límites)
# ---------------------------------------------------------
DIFFICULTY_LEVELS = {
    'tutorial': {'total_pairs': 3, 'grid_size': '2x3', 'time_limit': 60, 'memorization_time': 5},
    'easy':     {'total_pairs': 4, 'grid_size': '2x4', 'time_limit': 90, 'memorization_time': 5},
    'medium':   {'total_pairs': 6, 'grid_size': '3x4', 'time_limit': 120, 'memorization_time': 4},
    'hard':     {'total_pairs': 8, 'grid_size': '2x8', 'time_limit': 150, 'memorization_time': 3},
    'expert':   {'total_pairs': 10, 'grid_size': '4x5', 'time_limit': 180, 'memorization_time': 3},
    'master':   {'total_pairs': 12, 'grid_size': '3x8', 'time_limit': 200, 'memorization_time': 2}
}

LEVEL_ORDER = ['tutorial', 'easy', 'medium', 'hard', 'expert', 'master']

class AIAdapterService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini AI configurado correctamente")
        else:
            logger.warning("⚠️ GEMINI_API_KEY no encontrada. Usando modo fallback.")
            self.model = None

    def analyze_and_recommend(self, user_id, current_config, session_data):
        """
        Analiza el desempeño y recomienda la nueva configuración.
        """
        try:
            # 1. Preparar datos para el prompt
            performance_data = {
                "current_difficulty": current_config.difficulty_label,
                "total_pairs": session_data.total_pairs,
                "pairs_found": session_data.pairs_found,
                "total_flips": session_data.total_flips,
                "elapsed_time": session_data.elapsed_time_seconds,
                "time_limit": current_config.time_limit,
                "completed": session_data.completion_status == "completed",
                "accuracy": session_data.accuracy_percentage or 0
            }

            # 2. Intentar usar IA
            if self.model:
                try:
                    return self._analyze_with_ai(performance_data, current_config)
                except Exception as e:
                    logger.error(f"❌ Error en Gemini: {str(e)}. Usando fallback.")
                    return self._analyze_fallback(performance_data, current_config)
            else:
                return self._analyze_fallback(performance_data, current_config)

        except Exception as e:
            logger.error(f"❌ Error crítico en analyze_and_recommend: {str(e)}")
            # Retornar configuración actual en caso de pánico total
            return {
                "ai_analysis": {
                    "adjustment_decision": "maintain",
                    "reason": "Error interno del servidor, manteniendo configuración.",
                    "adjustment_summary": {
                        "previous_difficulty": current_config.difficulty_label,
                        "new_difficulty": current_config.difficulty_label,
                        "changed_fields": []
                    },
                    "next_session_config": current_config.to_dict(),
                    "performance_assessment": {
                        "overall_score": 0,
                        "memory_retention": "unknown",
                        "speed": "unknown",
                        "accuracy": "unknown"
                    }
                }
            }

    def _analyze_with_ai(self, data, current_config):
        prompt = f"""
        Actúa como un sistema experto de ajuste de dificultad para un juego de memoria terapéutico para adultos mayores.
        
        DATOS DE LA SESIÓN:
        - Dificultad actual: {data['current_difficulty']}
        - Resultado: {"VICTORIA" if data['completed'] else "DERROTA (Tiempo Agotado)"}
        - Pares encontrados: {data['pairs_found']} de {data['total_pairs']}
        - Intentos (flips): {data['total_flips']}
        - Tiempo usado: {data['elapsed_time']}s (Límite: {data['time_limit']}s)
        - Precisión: {data['accuracy']}%

        REGLAS DE AJUSTE:
        1. SI PERDIÓ (Tiempo agotado):
           - DEBE facilitar el juego.
           - Prioridad: Aumentar 'time_limit' (+15-30s) O reducir 'total_pairs'.
           - Nunca aumentar dificultad si perdió.
        
        2. SI GANÓ (Completado):
           - Evaluar desempeño (Velocidad y Precisión).
           - Si fue MUY FÁCIL (Rápido y alta precisión): Aumentar dificultad (Siguiente nivel o reducir tiempo).
           - Si fue NORMAL: Mantener dificultad o ajustes leves.
           - Si le costó mucho (Casi se acaba el tiempo): Mantener o facilitar ligeramente (más tiempo).

        NIVELES DISPONIBLES (Referencia):
        {json.dumps(DIFFICULTY_LEVELS, indent=2)}

        Genera una respuesta JSON ESTRICTA con este formato:
        {{
            "analysis": {{
                "decision": "increase" | "decrease" | "maintain",
                "reason": "Explicación corta para el terapeuta",
                "score": 1-10 (Calidad del juego),
                "metrics": {{
                    "memory": "low"|"medium"|"high",
                    "speed": "slow"|"normal"|"fast",
                    "accuracy": "low"|"medium"|"high"
                }}
            }},
            "new_config": {{
                "difficulty_label": "nombre_del_nivel",
                "total_pairs": int,
                "grid_size": "FxC" (ej. "3x4"),
                "time_limit": int,
                "memorization_time": int
            }}
        }}
        """

        response = self.model.generate_content(prompt)
        result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        
        # Validar y asegurar grid_size
        new_conf = result['new_config']
        if 'grid_size' not in new_conf:
             # Fallback si la IA olvida el grid_size
             new_conf['grid_size'] = self._calculate_grid_size(new_conf['total_pairs'])

        return self._format_response(data, result, current_config)

    def _analyze_fallback(self, data, current_config):
        """Lógica determinista si falla la IA - Ahora con score calculado"""
        current_level = data['current_difficulty']
        idx = LEVEL_ORDER.index(current_level) if current_level in LEVEL_ORDER else 0
        
        decision = "maintain"
        reason = "Desempeño estable."
        new_idx = idx
        time_adjust = 0
        
        # ═══════════════════════════════════════════════════════════
        # CALCULAR SCORE BASADO EN DESEMPEÑO REAL
        # ═══════════════════════════════════════════════════════════
        
        accuracy = data['accuracy']  # 0-100%
        time_used = data['elapsed_time']
        time_limit = data['time_limit']
        completed = data['completed']
        
        # Base score según accuracy (máximo 6 puntos)
        accuracy_score = (accuracy / 100) * 6
        
        # Bonus por velocidad (máximo 2 puntos)
        if time_limit > 0:
            time_ratio = time_used / time_limit
            if time_ratio < 0.5:      # Muy rápido
                speed_bonus = 2.0
            elif time_ratio < 0.7:    # Rápido
                speed_bonus = 1.5
            elif time_ratio < 0.9:    # Normal
                speed_bonus = 1.0
            else:                     # Lento
                speed_bonus = 0.5
        else:
            speed_bonus = 1.0
        
        # Bonus por completar (máximo 2 puntos)
        completion_bonus = 2.0 if completed else 0.0
        
        # Calcular score final (0-10)
        calculated_score = min(10, accuracy_score + speed_bonus + completion_bonus)
        calculated_score = max(1, calculated_score)  # Mínimo 1
        
        # ═══════════════════════════════════════════════════════════
        # DETERMINAR MÉTRICAS CUALITATIVAS
        # ═══════════════════════════════════════════════════════════
        
        # Memory assessment
        if accuracy >= 80:
            memory_assessment = "high"
        elif accuracy >= 50:
            memory_assessment = "medium"
        else:
            memory_assessment = "low"
        
        # Speed assessment
        if time_limit > 0:
            if time_ratio < 0.5:
                speed_assessment = "fast"
            elif time_ratio < 0.8:
                speed_assessment = "normal"
            else:
                speed_assessment = "slow"
        else:
            speed_assessment = "normal"
        
        # Accuracy assessment
        if accuracy >= 80:
            accuracy_assessment = "high"
        elif accuracy >= 50:
            accuracy_assessment = "medium"
        else:
            accuracy_assessment = "low"
        
        # ═══════════════════════════════════════════════════════════
        # LÓGICA DE AJUSTE DE DIFICULTAD
        # ═══════════════════════════════════════════════════════════
        
        if not completed:
            # PERDIÓ: Facilitar
            decision = "decrease"
            reason = f"Tiempo agotado con {data['pairs_found']}/{data['total_pairs']} pares. Reduciendo dificultad."
            if idx > 0:
                new_idx = idx - 1
            else:
                # Ya está en tutorial, dar más tiempo
                time_adjust = 30
        else:
            # GANÓ
            if accuracy > 80 and time_ratio < 0.6:
                # Muy fácil -> Subir
                decision = "increase"
                reason = f"Excelente desempeño ({accuracy:.0f}% precisión en {time_ratio*100:.0f}% del tiempo). Aumentando dificultad."
                if idx < len(LEVEL_ORDER) - 1:
                    new_idx = idx + 1
            elif accuracy < 50:
                # Muchos errores -> Mantener para practicar
                decision = "maintain"
                reason = f"Completado pero con precisión baja ({accuracy:.0f}%). Manteniendo para practicar."
            else:
                # Normal
                decision = "maintain"
                reason = f"Buen desempeño ({accuracy:.0f}% precisión). Manteniendo nivel actual."

        # ═══════════════════════════════════════════════════════════
        # CONSTRUIR RESPUESTA
        # ═══════════════════════════════════════════════════════════
        
        target_level = LEVEL_ORDER[new_idx]
        base_config = DIFFICULTY_LEVELS[target_level].copy()
        
        # Aplicar ajustes finos
        base_config['time_limit'] += time_adjust
        base_config['difficulty_label'] = target_level

        result = {
            "analysis": {
                "decision": decision,
                "reason": reason,
                "score": round(calculated_score, 1),  # ← SCORE CALCULADO, NO FIJO
                "metrics": {
                    "memory": memory_assessment,
                    "speed": speed_assessment,
                    "accuracy": accuracy_assessment
                }
            },
            "new_config": base_config
        }
        
        return self._format_response(data, result, current_config)

    def _format_response(self, data, ai_result, current_config):
        """Formatea la respuesta final para el controlador"""
        new_conf = ai_result['new_config']
        
        # Detectar cambios
        changed_fields = []
        if new_conf['total_pairs'] != current_config.total_pairs: 
            changed_fields.append('total_pairs')
        if new_conf['time_limit'] != current_config.time_limit: 
            changed_fields.append('time_limit')
        if new_conf['difficulty_label'] != current_config.difficulty_label: 
            changed_fields.append('difficulty')

        return {
            "ai_analysis": {
                "adjustment_decision": ai_result['analysis']['decision'],
                "reason": ai_result['analysis']['reason'],
                "adjustment_summary": {
                    "previous_difficulty": current_config.difficulty_label,
                    "new_difficulty": new_conf['difficulty_label'],
                    "changed_fields": changed_fields
                },
                "next_session_config": new_conf,
                "performance_assessment": {
                    "overall_score": ai_result['analysis']['score'],
                    "memory_retention": ai_result['analysis']['metrics']['memory'],
                    "speed": ai_result['analysis']['metrics']['speed'],
                    "accuracy": ai_result['analysis']['metrics']['accuracy']
                }
            }
        }

    def _calculate_grid_size(self, total_pairs):
        """Helper para calcular grid si falta"""
        total_cards = total_pairs * 2
        if total_cards <= 6: return "2x3"
        if total_cards <= 8: return "2x4"
        if total_cards <= 12: return "3x4"
        if total_cards <= 16: return "2x8"
        if total_cards <= 20: return "4x5"
        return "3x8" # Max 24 cartas
