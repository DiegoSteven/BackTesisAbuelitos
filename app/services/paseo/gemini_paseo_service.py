import random
from datetime import date
from services.paseo.paseo_service import PaseoService
import os
import json
import google.generativeai as genai

class GeminiPaseoService:
    """Servicio con IA para Paseo - Usa Gemini SOLO para nivel DIFICIL"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.gemini_activo = True
        else:
            print("[PASEO IA] GEMINI_API_KEY no configurada - Modo degradado")
            self.gemini_activo = False
    
    def decidir_nivel_inicial(self, user_id):
        """
        Decide nivel inicial - Usa Gemini SOLO si perdió en DIFICIL
        """
        ultima_sesion, _ = PaseoService.get_ultima_sesion(user_id)
        
        if not ultima_sesion:
            print("[PASEO IA] Primera vez → FACIL")
            return "facil"
        
        nivel_anterior = ultima_sesion['nivel']
        resultado = ultima_sesion['resultado']
        aciertos = ultima_sesion.get('aciertos', 0)
        meta = ultima_sesion.get('meta', 5)
        
        # Tutorial → FACIL
        if nivel_anterior == 'tutorial':
            print("[PASEO IA] Después de tutorial → FACIL")
            return "facil"
        
        # Victoria → Subir
        if resultado == 'victoria':
            if nivel_anterior == 'facil':
                print("[PASEO IA] Victoria FACIL → INTERMEDIO")
                return "intermedio"
            elif nivel_anterior == 'intermedio':
                print("[PASEO IA] Victoria INTERMEDIO → DIFICIL")
                return "dificil"
            else:
                print("[PASEO IA] Victoria DIFICIL → Mantiene DIFICIL")
                return "dificil"
        
        # Derrota en INTERMEDIO → Baja a FACIL
        if nivel_anterior == 'intermedio':
            print(f"[PASEO IA] Derrota INTERMEDIO ({aciertos}/{meta}) → FACIL")
            return "facil"
        
        # Derrota en DIFICIL → Usar Gemini para análisis profundo
        if nivel_anterior == 'dificil' and self.gemini_activo:
            print(f"[PASEO IA] Derrota DIFICIL ({aciertos}/{meta}) - Consultando Gemini...")
            return self._analizar_derrota_dificil(user_id, aciertos, meta)
        
        # Derrota en FACIL o fallback
        print(f"[PASEO IA] Derrota {nivel_anterior.upper()} → Mantiene {nivel_anterior.upper()}")
        return nivel_anterior
    
    def _analizar_derrota_dificil(self, user_id, aciertos, meta):
        """
        Usa Gemini para analizar derrota en DIFICIL y decidir nivel + velocidad
        """
        try:
            # Obtener historial reciente
            from models.paseo import PaseoSession
            from datetime import date, timedelta
            
            sesiones_recientes = PaseoSession.query.filter_by(
                user_id=user_id,
                nivel_dificultad='dificil'
            ).order_by(PaseoSession.created_at.desc()).limit(3).all()
            
            # Calcular métricas
            total_intentos = len(sesiones_recientes)
            total_aciertos_historico = sum(s.esferas_rojas_atrapadas for s in sesiones_recientes)
            total_errores = sum(s.esferas_azules_atrapadas + s.esferas_perdidas for s in sesiones_recientes)
            precision_promedio = sum(s.precision for s in sesiones_recientes) / total_intentos if total_intentos > 0 else 0
            
            # Prompt conciso para Gemini
            prompt = f"""Eres un terapeuta cognitivo. Analiza el rendimiento de un adulto mayor en nivel DIFICIL:

ÚLTIMA SESIÓN DIFICIL:
- Aciertos: {aciertos}/{meta}
- Porcentaje: {(aciertos/meta*100):.0f}%

HISTORIAL (últimas 3 sesiones DIFICIL):
- Total intentos: {total_intentos}
- Promedio precisión: {precision_promedio:.0f}%
- Aciertos totales: {total_aciertos_historico}
- Errores totales: {total_errores}

DECISIÓN REQUERIDA:
1. ¿A qué nivel bajar? FACIL o INTERMEDIO (raramente DIFICIL)
2. ¿Qué velocidad usar en ESE nivel? (ajustar según frustración)

VELOCIDADES NORMALES:
- FACIL: 3.0
- INTERMEDIO: 4.0  
- DIFICIL: 5.0

Responde SOLO este JSON:
{{
  "nivel_recomendado": "facil",
  "razonamiento_breve": "Tuvo X% aciertos, frustración alta",
  "velocidad_ajustada": 2.5
}}

GUÍA:
- Si <30% aciertos → FACIL, velocidad 2.5-3.0 (reducir frustración)
- Si 30-60% aciertos → INTERMEDIO, velocidad 3.5-4.0
- Si >60% aciertos → DIFICIL, velocidad 4.5-5.0 (estuvo cerca)
- Reducir velocidad si precisión <50% o muchos errores"""

            response = self.model.generate_content(prompt)
            text = response.text
            
            # Parse JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                data = json.loads(text[start:end])
                nivel = data.get('nivel_recomendado', 'intermedio')
                razon = data.get('razonamiento_breve', '')
                velocidad = data.get('velocidad_ajustada', 4.5)
                
                print(f"[GEMINI DIFICIL] → {nivel.upper()} | Velocidad: {velocidad} | {razon}")
                
                # Guardar velocidad para aplicarla después
                self._velocidad_ajustada = velocidad
                
                return nivel
            else:
                raise ValueError("No JSON en respuesta")
                
        except Exception as e:
            print(f"[GEMINI ERROR] {e} - Fallback a lógica simple")
            # Fallback: análisis simple sin IA
            porcentaje = (aciertos / meta * 100) if meta > 0 else 0
            if porcentaje < 30:
                return "facil"
            elif porcentaje < 60:
                return "intermedio"
            else:
                return "dificil"
    
    def _plan_nivel_sin_ia(self, nivel, razonamiento=None):
        """
        IA decide nivel inicial basado en ÚLTIMO resultado y errores
        Ahorra tokens usando lógica simple SIN LLM
        """
        ultima_sesion, _ = PaseoService.get_ultima_sesion(user_id)
        
        if not ultima_sesion:
            print("[PASEO IA] Primera vez → FACIL")
            return "facil"
        
        nivel_anterior = ultima_sesion['nivel']
        resultado = ultima_sesion['resultado']
        aciertos = ultima_sesion.get('aciertos', 0)
        meta = ultima_sesion.get('meta', 5)
        
        # Después del tutorial → FACIL
        if nivel_anterior == 'tutorial':
            print("[PASEO IA] Después de tutorial → FACIL")
            return "facil"
        
        # Si ganó, subir de nivel
        if resultado == 'victoria':
            if nivel_anterior == 'facil':
                print("[PASEO IA] Victoria en FACIL → INTERMEDIO")
                return "intermedio"
            elif nivel_anterior == 'intermedio':
                print("[PASEO IA] Victoria en INTERMEDIO → DIFICIL")
                return "dificil"
            else:  # Ya está en DIFICIL
                print("[PASEO IA] Victoria en DIFICIL → Mantiene DIFICIL")
                return "dificil"
        
        # Si perdió, analizar qué tan mal le fue
        else:
            # Calcular porcentaje de aciertos
            porcentaje_aciertos = (aciertos / meta * 100) if meta > 0 else 0
            
            # INTERMEDIO perdido → Baja a FACIL (siempre)
            if nivel_anterior == 'intermedio':
                print(f"[PASEO IA] Derrota en INTERMEDIO ({aciertos}/{meta}) → FACIL")
                return "facil"
            
            # DIFICIL perdido → Analizar qué tan mal
            elif nivel_anterior == 'dificil':
                if porcentaje_aciertos < 30:  # Muy mal (menos del 30%)
                    print(f"[PASEO IA] Derrota severa en DIFICIL ({aciertos}/{meta}, {porcentaje_aciertos:.0f}%) → FACIL")
                    return "facil"
                elif porcentaje_aciertos < 60:  # Regular (30-60%)
                    print(f"[PASEO IA] Derrota en DIFICIL ({aciertos}/{meta}, {porcentaje_aciertos:.0f}%) → INTERMEDIO")
                    return "intermedio"
                else:  # Estuvo cerca (60%+)
                    print(f"[PASEO IA] Derrota cercana en DIFICIL ({aciertos}/{meta}, {porcentaje_aciertos:.0f}%) → Mantiene DIFICIL")
                    return "dificil"
            
            # FACIL perdido → Mantiene FACIL
            else:
                print(f"[PASEO IA] Derrota en FACIL ({aciertos}/{meta}) → Mantiene FACIL")
                return "facil"
    
    def _plan_nivel_sin_ia(self, nivel, razonamiento=None):
        """
        Genera plan de sesión - Usa velocidad ajustada si Gemini la decidió
        """
        configs = {
            'tutorial': {
                'duracion': 60,
                'meta_aciertos': 5,
                'velocidad': 2.0,
                'intervalo': 3.0,
                'colores_count': 1
            },
            'facil': {
                'duracion': 60,
                'meta_aciertos': 5,
                'velocidad': 3.0,
                'intervalo': 2.0,
                'colores_count': 1
            },
            'intermedio': {
                'duracion': 90,
                'meta_aciertos': 8,
                'velocidad': 4.0,
                'intervalo': 1.5,
                'colores_count': 2
            },
            'dificil': {
                'duracion': 120,
                'meta_aciertos': 7,
                'velocidad': 5.0,  # Puede ser ajustada por Gemini
                'intervalo': 1.0,
                'colores_count': 3
            }
        }
        
        config = configs.get(nivel, configs['facil'])
        
        # ✅ Si Gemini ajustó la velocidad, usarla (para cualquier nivel que decidió)
        if hasattr(self, '_velocidad_ajustada'):
            velocidad_final = self._velocidad_ajustada
            print(f"[PLAN] Gemini ajustó velocidad para {nivel.upper()}: {velocidad_final}")
            delattr(self, '_velocidad_ajustada')
        else:
            velocidad_final = config['velocidad']
        
        # Elegir colores aleatorios
        colores_disponibles = ['rojo', 'azul', 'amarillo']
        if config['colores_count'] == 1:
            color = random.choice(colores_disponibles)
            colores_activos = color
            color_correcto = color
        elif config['colores_count'] == 2:
            colores = random.sample(colores_disponibles, 2)
            colores_activos = ','.join(colores)
            color_correcto = random.choice(colores)
        else:  # 3 colores
            colores_activos = 'rojo,azul,amarillo'
            color_correcto = random.choice(colores_disponibles)
        
        return {
            'duracion_estimada': config['duracion'],
            'nivel_dificultad': nivel,
            'meta_aciertos': config['meta_aciertos'],
            'colores_activos': colores_activos,
            'color_correcto': color_correcto,
            'velocidad_esferas': velocidad_final,  # ✅ Usa velocidad ajustada
            'intervalo_spawn': config['intervalo'],
            'objetivo_sesion': self._generar_objetivo_con_meta(nivel, color_correcto, config['meta_aciertos']),
            'razonamiento': razonamiento or f'Nivel {nivel.upper()} - Meta: {config["meta_aciertos"]} aciertos'
        }
    
    def _generar_objetivo_con_meta(self, nivel: str, color: str, meta: int) -> str:
        """Genera texto de objetivo CON meta de aciertos"""
        # Convertir color a plural correcto
        if color == 'rojo':
            color_texto = 'ROJAS'
        elif color == 'azul':
            color_texto = 'AZULES'
        elif color == 'amarillo':
            color_texto = 'AMARILLAS'
        else:
            color_texto = color.upper() + 'S'
        
        if nivel == 'tutorial':
            return '🎓 TUTORIAL: Aprende los controles'
        elif nivel == 'facil':
            return f'🎯 Meta: {meta} esferas {color_texto}'
        elif nivel == 'intermedio':
            return f'🎯 Meta: {meta} {color_texto}, esquiva otras'
        else:  # dificil
            return f'🎯 Meta: {meta} {color_texto} entre 3 colores'
