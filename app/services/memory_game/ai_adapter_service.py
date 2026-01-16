"""
Servicio de adaptación de IA para Memory Game usando Gemini
"""
from typing import Dict, Any
import os
import json
import google.generativeai as genai

class AIAdapterService:
    # Configuraciones predefinidas (FALLBACK)
    DIFFICULTY_CONFIGS = {
        'tutorial': {'total_pairs': 3, 'grid_size': '2x3', 'time_limit': 60, 'memorization_time': 5},
        'easy': {'total_pairs': 4, 'grid_size': '2x4', 'time_limit': 90, 'memorization_time': 4},
        'medium': {'total_pairs': 6, 'grid_size': '3x4', 'time_limit': 120, 'memorization_time': 3},
        'hard': {'total_pairs': 8, 'grid_size': '4x4', 'time_limit': 180, 'memorization_time': 2}
    }
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.use_ai = True
        else:
            print("[MEMORY IA] GEMINI_API_KEY no encontrada. Usando lógica clásica.")
            self.use_ai = False

    def analyze_and_recommend(self, session_data: Dict, current_difficulty: str) -> Dict:
        """
        Analiza desempeño y recomienda nueva configuración.
        Intenta usar Gemini; si falla, usa lógica determinista (fallback).
        """
        if self.use_ai:
            try:
                return self._analyze_with_gemini(session_data, current_difficulty)
            except Exception as e:
                print(f"[MEMORY IA ERROR] {e}. Usando fallback.")
                return self._analyze_fallback(session_data, current_difficulty)
        else:
            return self._analyze_fallback(session_data, current_difficulty)

    def _analyze_with_gemini(self, session_data: Dict, current_difficulty: str) -> Dict:
        """Usa Gemini para decidir la configuración exacta del próximo juego."""
        
        # Construir Prompt Estructurado
        prompt = f"""
        Actúa como un Terapeuta Cognitivo experto en rehabilitación de adultos mayores.
        Tu tarea es ajustar la dificultad del "Juego de Memoria" basándote en el desempeño reciente del usuario.

        CONTEXTO DEL JUEGO:
        - El usuario debe encontrar pares de cartas.
        - Dificultades: tutorial (3 pares), easy (4 pares), medium (6 pares), hard (8 pares).
        - Variables ajustables: Tiempo límite, Tiempo de memorización inicial.

        CONFIGURACIÓN ACTUAL:
        - Nivel: {current_difficulty}
        - Tiempo límite: {session_data.get('time_limit', 'N/A')}s

        DESEMPEÑO DE LA SESIÓN:
        - Estado: {session_data.get('completion_status', 'unknown')}
        - Tiempo usado: {session_data.get('elapsed_time', 0)}s
        - Errores cometidos: {session_data.get('mistakes', 0)}
        - Pares encontrados: {session_data.get('pairs_found', 0)} / {session_data.get('total_pairs', 0)}

        OBJETIVO:
        - Si el usuario completó rápido y sin errores -> AUMENTAR dificultad (más pares o menos tiempo).
        - Si el usuario completó pero con dificultad -> MANTENER o ajustar levemente (más tiempo).
        - Si el usuario NO completó o tuvo muchos errores -> DISMINUIR dificultad (menos pares o más tiempo).

        SALIDA REQUERIDA (JSON):
        Devuelve un JSON con la configuración EXACTA para Unity.
        {{
            "ai_decision": "LEVEL_UP" | "MAINTAIN" | "LEVEL_DOWN",
            "reason": "Explicación breve y motivadora para el terapeuta.",
            "next_config": {{
                "difficulty_level": "medium",
                "grid_rows": 3,
                "grid_cols": 4,
                "time_limit": 120,
                "memorization_time": 3
            }}
        }}
        
        REGLAS DE CONFIGURACIÓN:
        - Grid sizes válidos: 2x3 (3 pares), 2x4 (4 pares), 3x4 (6 pares), 4x4 (8 pares).
        - time_limit: entre 45 y 300 segundos.
        - memorization_time: entre 1 y 10 segundos.
        """

        response = self.model.generate_content(prompt)
        text = response.text
        
        # Parsear JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end <= start:
            raise ValueError("No se encontró JSON en la respuesta de IA")
            
        result = json.loads(text[start:end])
        
        # Estructurar respuesta para el controlador
        return {
            'adjustment_decision': result.get('ai_decision', 'MAINTAIN'),
            'reason': result.get('reason', 'Ajuste por IA'),
            'next_session_config': result.get('next_config'),
            'ai_generated': True
        }

    def _analyze_fallback(self, session_data: Dict, current_difficulty: str) -> Dict:
        """Lógica determinista original (Backup)"""
        score = self._evaluate_performance(session_data)
        adjustment = self._decide_adjustment(score)
        new_difficulty = self._get_next_difficulty(current_difficulty, adjustment)
        new_config = self.DIFFICULTY_CONFIGS[new_difficulty].copy()
        new_config['difficulty_level'] = new_difficulty # Ensure label exists
        
        # Mapear grid string a rows/cols para consistencia con IA
        rows, cols = map(int, new_config.pop('grid_size').split('x'))
        new_config['grid_rows'] = rows
        new_config['grid_cols'] = cols

        return {
            'adjustment_decision': adjustment,
            'reason': f"Fallback Logic: Score {score}/10 -> {adjustment}",
            'next_session_config': new_config,
            'ai_generated': False
        }

    # --- Métodos auxiliares del Fallback ---
    def _evaluate_performance(self, session_data: Dict) -> float:
        if session_data.get('completion_status') != 'completed':
            return 2.0
        # Simple score logic
        mistakes = session_data.get('mistakes', 0)
        time_ratio = session_data.get('elapsed_time', 0) / session_data.get('time_limit', 1)
        
        score = 10 - mistakes
        if time_ratio < 0.5: score += 2
        return max(0, min(10, score))

    def _decide_adjustment(self, score: float) -> str:
        if score >= 8: return "LEVEL_UP"
        if score <= 4: return "LEVEL_DOWN"
        return "MAINTAIN"

    def _get_next_difficulty(self, current: str, adjustment: str) -> str:
        levels = ['tutorial', 'easy', 'medium', 'hard']
        try:
            idx = levels.index(current)
        except:
            return 'easy'
            
        if adjustment == "LEVEL_UP" and idx < len(levels)-1: idx += 1
        if adjustment == "LEVEL_DOWN" and idx > 0: idx -= 1
        return levels[idx]
