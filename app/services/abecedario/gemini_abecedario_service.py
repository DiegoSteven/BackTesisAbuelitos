import os
import json
import google.generativeai as genai
from services.abecedario.abecedario_service import AbecedarioService

class GeminiService:
    """
    Servicio OPTIMIZADO para generar palabras adaptativas con Gemini AI.
    
    ESTRATEGIA DE AHORRO:
    - Niveles FACIL e INTERMEDIO: Usa palabras predefinidas locales (JSON) → $0 + latencia 0ms
    - Nivel DIFICIL: Usa sistema de BATCH (lotes de 20 palabras) → 95% menos llamadas API
    
    RESULTADO: Ahorro del 95% en costos, soporta 40 usuarios/min con límite RPM=2
    """
    
    # 🆕 Buffer de palabras pregeneradas (cache en memoria)
    _palabra_buffer = []
    _buffer_size = 20  # Generar 20 palabras por lote
    
    # Configuración de niveles
    NIVELES = {
        'facil': {
            'palabras_requeridas': 5,
            'usa_ia': False,  # 👉 Usa JSON local
            'descripcion': 'Palabras muy comunes de uso diario'
        },
        'intermedio': {
            'palabras_requeridas': 5,
            'usa_ia': False,  # 👉 Usa JSON local
            'descripcion': 'Palabras cotidianas con ligera complejidad'
        },
        'dificil': {
            'palabras_requeridas': 5,
            'usa_ia': True,  # 👉 SOLO AQUÍ usa Gemini (en lotes)
            'longitud': '5-7',
            'distractoras': '0-1',
            'descripcion': 'Palabras más complejas pero conocidas'
        }
    }
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en el archivo .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    def generate_next_challenge(self, user_id):
        """Genera desafío adaptativo usando sistema híbrido local + IA"""
        print(f"\n[GEMINI] ==== Generando desafío para user_id: {user_id} ====\n")
        
        try:
            # PASO 1: Determinar nivel óptimo (lógica en Python, NO en Gemini)
            nivel_actual = AbecedarioService.determinar_nivel_optimo(user_id)
            print(f"[GEMINI] Nivel determinado: {nivel_actual.upper()}")
            
            # PASO 2: Verificar si hay cambio de nivel
            from models.abecedario import Abecedario
            ultima_sesion = Abecedario.query.filter_by(user_id=user_id).order_by(
                Abecedario.created_at.desc()
            ).first()
            
            nivel_anterior = ultima_sesion.nivel_jugado if ultima_sesion else None
            cambio_nivel = (nivel_anterior != nivel_actual) if nivel_anterior else True
            
            # PASO 3: Contar palabras completadas en el nivel
            completadas_nivel = self._contar_completadas_en_nivel(user_id, nivel_actual)
            
            # PASO 4: Obtener palabras usadas recientemente (evitar repetición)
            stats, _ = AbecedarioService.get_performance_stats(user_id, limit=10)
            historial = stats.get('historial', [])
            palabras_usadas = [s['palabra'] for s in historial if 'palabra' in s]
            
            # PASO 5: Generar desafío según nivel (HÍBRIDO + BATCH)
            if nivel_actual in ['facil', 'intermedio']:
                # 💾 Modo Local (JSON) - Gratis e instantáneo
                print(f"[GEMINI] Modo AHORRO: Usando palabra local para nivel {nivel_actual.upper()}")
                challenge = AbecedarioService.get_palabra_local(nivel_actual, palabras_usadas)
                
                if not challenge:
                    return None, "Error al cargar palabras predefinidas"
                    
            else:
                # 🤖 Modo IA BATCH (Gemini) - Solo para nivel DIFICIL
                print(f"[GEMINI] Modo TESIS + BATCH: Nivel {nivel_actual.upper()}")
                
                # Verificar si hay palabras en el buffer
                if not self._palabra_buffer:
                    print(f"[GEMINI BATCH] Buffer vacío, generando {self._buffer_size} palabras...")
                    self._palabra_buffer = self._generar_lote_palabras(stats, nivel_actual, palabras_usadas)
                    
                    if not self._palabra_buffer:
                        return None, "Error al generar lote de palabras"
                
                # Obtener la primera palabra del buffer
                challenge = self._palabra_buffer.pop(0)
                print(f"[GEMINI BATCH] Palabra del buffer. Quedan {len(self._palabra_buffer)} en cache.")
            
            # PASO 6: Agregar metadata del desafío
            challenge['nivel_dificultad'] = nivel_actual
            challenge['cambio_nivel'] = cambio_nivel
            challenge['nivel_anterior'] = nivel_anterior
            challenge['progreso_nivel'] = {
                'palabras_completadas': completadas_nivel,
                'palabras_requeridas': 5,
                'porcentaje': round((completadas_nivel / 5) * 100, 1)
            }
            
            print(f"[GEMINI] ✅ Desafío generado: '{challenge['palabra_objetivo']}' - Nivel: {nivel_actual.upper()} ({completadas_nivel}/5)")
            if cambio_nivel:
                print(f"[GEMINI] 🔄 CAMBIO DE NIVEL: {nivel_anterior or 'N/A'} → {nivel_actual.upper()}")
            print(f"{'='*70}\n")
            
            return challenge, None
            
        except Exception as e:
            print(f"[GEMINI ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    def _contar_completadas_en_nivel(self, user_id, nivel):
        """
        Cuenta palabras completadas DESDE el último cambio de nivel (INCLUSIVE)
        """
        from models.abecedario import Abecedario
        
        # Buscar la última sesión donde hubo cambio de nivel
        ultima_sesion_cambio = Abecedario.query.filter_by(
            user_id=user_id,
            cambio_nivel=True
        ).order_by(Abecedario.created_at.desc()).first()
        
        # Construir query: nivel actual + completadas
        query = Abecedario.query.filter_by(
            user_id=user_id,
            nivel_jugado=nivel,
            completado=True
        )
        
        # Contar DESDE el último cambio (INCLUSIVE - es decir >= no >)
        if ultima_sesion_cambio:
            query = query.filter(Abecedario.created_at >= ultima_sesion_cambio.created_at)
        
        count = query.count()
        return min(count, 5)
    
    def _build_prompt(self, stats, nivel, palabras_usadas=[]):
        """Construye el prompt para Gemini (SOLO nivel DIFICIL)"""
        config = self.NIVELES[nivel]
        
        palabras_evitar = ', '.join(palabras_usadas[:10]) if palabras_usadas else 'ninguna'
        
        prompt = f"""Eres un terapeuta cognitivo. Genera {self._buffer_size} PALABRAS DIFERENTES en español para un juego de memoria.

NIVEL ACTUAL: {nivel.upper()}
- {config['descripcion']}
- Longitud: {config['longitud']} letras
- Letras distractoras: {config['distractoras']}

RENDIMIENTO DEL USUARIO:
- Total sesiones: {stats.get('total_sesiones', 0)}
- Tasa de éxito: {stats.get('tasa_exito', 0)}%
- Promedio errores: {stats.get('promedio_errores', 0)}

PALABRAS YA USADAS (NO REPETIR): {palabras_evitar}

REGLAS ESTRICTAS:
- Palabras comunes del día a día (NO rebuscadas)
- Apropiadas para adultos mayores
- TODAS LAS LETRAS EN MAYÚSCULAS (pueden tener acentos y ñ)
- Letras distractoras también en MAYÚSCULAS
- NO REPETIR ninguna de las palabras ya usadas arriba
- Cada palabra debe tener su pista clara sin revelar la palabra
- Formato JSON válido

Devuelve SOLO este JSON con un array de {self._buffer_size} palabras:
{{
  "palabras": [
    {{
      "palabra_objetivo": "JARDÍN",
      "letras_distractoras": ["L", "M"],
      "pista_contextual": "Espacio verde con plantas"
    }},
    {{
      "palabra_objetivo": "COCINA",
      "letras_distractoras": ["T", "R"],
      "pista_contextual": "Lugar donde se prepara comida"
    }}
    ... ({self._buffer_size} palabras en total)
  ]
}}

IMPORTANTE: Todas las "palabra_objetivo" deben estar COMPLETAMENTE en MAYÚSCULAS (CAFÉ, NIÑO, ÁRBOL, etc.) y ser DIFERENTES entre sí y diferentes a las ya usadas."""
        
        return prompt
    
    def _generar_lote_palabras(self, stats, nivel, palabras_usadas=[]):
        """
        🆕 Genera un lote de 20 palabras de una sola vez (optimización batch)
        Reduce llamadas API de 20 a 1 (95% ahorro)
        """
        print(f"[GEMINI BATCH] Generando lote de {self._buffer_size} palabras para nivel {nivel.upper()}...")
        
        try:
            prompt = self._build_prompt(stats, nivel, palabras_usadas)
            response = self.model.generate_content(prompt)
            
            # Parsear respuesta JSON
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start == -1 or end <= start:
                raise ValueError("No se encontró JSON en la respuesta")
            
            data = json.loads(text[start:end])
            
            if 'palabras' not in data or not isinstance(data['palabras'], list):
                raise ValueError("Respuesta no contiene array 'palabras'")
            
            # Validar y normalizar cada palabra
            palabras_validas = []
            for item in data['palabras']:
                if all(field in item for field in ['palabra_objetivo', 'letras_distractoras', 'pista_contextual']):
                    # Forzar MAYÚSCULAS
                    item['palabra_objetivo'] = item['palabra_objetivo'].upper()
                    item['letras_distractoras'] = [letra.upper() for letra in item['letras_distractoras']]
                    palabras_validas.append(item)
            
            print(f"[GEMINI BATCH] ✅ Generadas {len(palabras_validas)} palabras válidas")
            return palabras_validas
            
        except Exception as e:
            print(f"[GEMINI BATCH ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_response(self, text):
        """Extrae el JSON de la respuesta y fuerza MAYÚSCULAS"""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start == -1 or end <= start:
                raise ValueError("No se encontró JSON en la respuesta")
            
            challenge = json.loads(text[start:end])
            
            # Validar campos requeridos
            required = ['palabra_objetivo', 'letras_distractoras', 'pista_contextual']
            if not all(field in challenge for field in required):
                raise ValueError("Faltan campos requeridos en el JSON")
            
            # FORZAR MAYÚSCULAS (manteniendo acentos y ñ)
            palabra_original = challenge['palabra_objetivo']
            palabra_mayuscula = palabra_original.upper()
            
            challenge['palabra_objetivo'] = palabra_mayuscula
            
            # Forzar mayúsculas en letras distractoras
            if challenge['letras_distractoras']:
                challenge['letras_distractoras'] = [
                    letra.upper() for letra in challenge['letras_distractoras']
                ]
            
            print(f"[PARSE] Palabra: {palabra_original} → {palabra_mayuscula}")
            
            return challenge
            
        except Exception as e:
            raise ValueError(f"Error parseando respuesta de IA: {str(e)}")
