"""
Servicio de adaptaciÃ³n de IA
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
        Analiza desempeÃ±o y recomienda nueva configuraciÃ³n
        """
        # 1. Evaluar desempeÃ±o (0-10)
        score = self._evaluate_performance(session_data)
        
        # 2. Decidir ajuste
        adjustment = self._decide_adjustment(score)
        
        # 3. Generar nueva configuraciÃ³n
        new_difficulty = self._get_next_difficulty(current_difficulty, adjustment)
        new_config = self.DIFFICULTY_CONFIGS[new_difficulty].copy()
        
        # 4. Generar anÃ¡lisis
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
            "increase_difficulty": f"Excelente desempeÃ±o (score {score}/10). Listo para mÃ¡s desafÃ­o.",
            "keep_same": f"Buen desempeÃ±o (score {score}/10). Mantener nivel actual.",
            "decrease_difficulty": f"DesempeÃ±o bajo (score {score}/10). Reducir dificultad."
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
