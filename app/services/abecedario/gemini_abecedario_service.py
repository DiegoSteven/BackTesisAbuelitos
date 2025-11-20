import os
import json
import google.generativeai as genai
from services.abecedario.abecedario_service import AbecedarioService

class GeminiService:
    """
    Servicio simple para generar palabras adaptativas con Gemini AI
    Maneja progresión por niveles: facil -> intermedio -> dificil
    """
    
    # Configuración de niveles
    NIVELES = {
        'facil': {
            'palabras_requeridas': 5,  # Debe completar 5 palabras fáciles para avanzar
            'longitud': '3-4',
            'distractoras': '0-1',
            'descripcion': 'Palabras muy comunes de uso diario'
        },
        'intermedio': {
            'palabras_requeridas': 5,  # 5 palabras intermedias para avanzar
            'longitud': '4-6',
            'distractoras': '1-2',
            'descripcion': 'Palabras cotidianas con ligera complejidad'
        },
        'dificil': {
            'palabras_requeridas': 5,  # 5 palabras difíciles
            'longitud': '5-7',
            'distractoras': '0-1',
            'descripcion': 'Palabras más complejas pero conocidas'
        }
    }
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en el archivo .env")
        
        # Configurar API - usar gemini-2.5-flash (último modelo estable)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_next_challenge(self, user_id):
        """Genera desafío adaptativo"""
        print(f"\n[GEMINI] ==== Generando desafío para user_id: {user_id} ====")
        
        try:
            stats, error = AbecedarioService.get_performance_stats(user_id, limit=10)
            if error:
                return None, error
            
            # Agregar user_id a stats
            stats['user_id'] = user_id
            
            nivel_actual = self._determinar_nivel(stats, user_id)
            
            # Calcular progreso en el nivel actual
            completadas_nivel = self._contar_completadas_en_nivel(user_id, nivel_actual)
            
            prompt = self._build_prompt(stats, nivel_actual)
            response = self.model.generate_content(prompt)
            
            challenge = self._parse_response(response.text)
            challenge['nivel_dificultad'] = nivel_actual
            challenge['progreso_nivel'] = {
                'palabras_completadas': completadas_nivel,
                'palabras_requeridas': 5,
                'porcentaje': (completadas_nivel / 5 * 100)
            }
            
            print(f"[GEMINI] Desafío generado: {challenge['palabra_objetivo']} - Nivel: {nivel_actual.upper()} ({completadas_nivel}/5)\n")
            
            return challenge, None
            
        except Exception as e:
            print(f"[GEMINI ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    def _determinar_nivel(self, stats, user_id=None):
        """
        Determina nivel basado SOLO en el nivel de la última sesión + progreso
        REGLA SIMPLE: 
        - Empieza en FACIL
        - Completa 5 palabras en FACIL → sube a INTERMEDIO
        - Completa 5 palabras en INTERMEDIO → sube a DIFICIL
        - 8+ errores en una sesión → baja un nivel
        """
        total_sesiones = stats.get('total_sesiones', 0)
        sesion_reciente_dificil = stats.get('sesion_reciente_dificil', False)
        
        # Usuario nuevo: FACIL
        if total_sesiones == 0:
            print(f"[NIVEL] Usuario nuevo -> FACIL")
            return 'facil'
        
        # Obtener nivel de la última sesión
        from models.abecedario import Abecedario
        ultima_sesion = Abecedario.query.filter_by(
            user_id=stats.get('user_id')
        ).order_by(Abecedario.created_at.desc()).first()
        
        nivel_anterior = ultima_sesion.nivel_jugado if ultima_sesion and ultima_sesion.nivel_jugado else 'facil'
        
        # REGLA 1: Si hubo sesión con 8+ errores, BAJA de nivel
        if sesion_reciente_dificil:
            if nivel_anterior == 'dificil':
                print(f"[NIVEL] Sesión difícil detectada -> BAJA de DIFICIL a INTERMEDIO")
                return 'intermedio'
            elif nivel_anterior == 'intermedio':
                print(f"[NIVEL] Sesión difícil detectada -> BAJA de INTERMEDIO a FACIL")
                return 'facil'
            else:
                print(f"[NIVEL] Sesión difícil detectada -> MANTIENE FACIL")
                return 'facil'
        
        # REGLA 2: Contar palabras completadas desde último cambio
        completadas_en_nivel = self._contar_completadas_en_nivel(stats.get('user_id'), nivel_anterior)
        
        print(f"[NIVEL] Nivel anterior: {nivel_anterior.upper()}, Completadas: {completadas_en_nivel}/5")
        
        # REGLA 3: Si completó 5, sube de nivel
        if completadas_en_nivel >= 5:
            if nivel_anterior == 'facil':
                print(f"[NIVEL] 5/5 completadas -> SUBE de FACIL a INTERMEDIO")
                return 'intermedio'
            elif nivel_anterior == 'intermedio':
                print(f"[NIVEL] 5/5 completadas -> SUBE de INTERMEDIO a DIFICIL")
                return 'dificil'
            else:
                print(f"[NIVEL] Permanece en DIFICIL (nivel máximo)")
                return 'dificil'
        
        # REGLA 4: Si no completó 5, mantiene nivel
        print(f"[NIVEL] Mantiene nivel {nivel_anterior.upper()}")
        return nivel_anterior
    
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
    
    def _build_prompt(self, stats, nivel):
        """Construye el prompt para Gemini"""
        config = self.NIVELES[nivel]
        
        # Obtener historial de palabras usadas (últimas 10)
        historial = stats.get('historial', [])
        palabras_usadas = [s['palabra'] for s in historial[:10] if 'palabra' in s]
        palabras_evitar = ', '.join(palabras_usadas) if palabras_usadas else 'ninguna'
        
        prompt = f"""Eres un terapeuta cognitivo. Genera UNA palabra en español para un juego de memoria.

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
- Palabra común del día a día (NO rebuscada)
- Apropiada para adultos mayores
- TODAS LAS LETRAS EN MAYÚSCULAS (pueden tener acentos y ñ)
- Letras distractoras también en MAYÚSCULAS
- NO REPETIR ninguna de las palabras ya usadas arriba
- Pista clara sin revelar la palabra
- Formato JSON válido

Devuelve SOLO este JSON:
{{
  "palabra_objetivo": "JARDÍN",
  "letras_distractoras": ["L", "M"],
  "pista_contextual": "Una pista útil y amigable"
}}

IMPORTANTE: "palabra_objetivo" debe estar COMPLETAMENTE en MAYÚSCULAS (CAFÉ, NIÑO, ÁRBOL, etc.) y ser DIFERENTE a las palabras ya usadas."""
        
        return prompt
    
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
