# Mejoras en la Adaptabilidad del Juego Abecedario

## Fecha: 2026-01-18

## Problema Identificado
El juego de Abecedario no evaluaba adecuadamente las sesiones de cada usuario, a diferencia de otros juegos como Paseo, Memory y Train. Solo contaba palabras completadas sin analizar el desempeño real.

## Solución Implementada

### 1. Sistema de Análisis Mejorado (`analizar_necesidad_bajar_nivel`)

**Antes:**
- Solo contaba si el usuario falló 4 de 5 palabras
- No consideraba otros factores de rendimiento
- Retornaba solo un booleano

**Ahora:**
- Analiza múltiples métricas de rendimiento:
  - **Precisión**: Porcentaje de palabras completadas
  - **Errores promedio**: Cantidad de errores por sesión
  - **Tiempo promedio**: Tiempo de resolución
  - **Uso de pistas**: Dependencia de ayudas

- Retorna un diccionario completo:
  ```python
  {
      'debe_bajar': bool,
      'razon': str,  # Explicación detallada
      'precision': float  # Porcentaje de éxito
  }
  ```

- **Criterios de Frustración** (similar a Paseo):
  1. Precisión < 40% → Bajar nivel
  2. Promedio errores > 5 y precisión < 60% → Bajar nivel
  3. Tiempos altos (>60s) y precisión < 50% → Bajar nivel
  4. Exceso de pistas (>10 en 5 sesiones) y precisión < 70% → Bajar nivel

### 2. Determinación de Nivel Optimizada (`determinar_nivel_optimo`)

**Nuevas Reglas:**

1. **Usuario nuevo** → FACIL
2. **Nuevo día** → FACIL (reseteo completo para comparar evolución)
3. **Análisis de rendimiento reciente** → Si desempeño bajo, BAJA nivel
   - En DIFICIL con precisión < 30% → Baja directo a FACIL (frustración severa)
   - En DIFICIL con precisión 30-70% → Baja a INTERMEDIO
   - En INTERMEDIO con bajo rendimiento → Baja a FACIL
4. **5 palabras completadas con >70% precisión** → SUBE de nivel
5. **5 palabras completadas con <70% precisión** → MANTIENE nivel (necesita mejorar)
6. **Caso contrario** → MANTIENE nivel actual

### 3. Servicio Gemini Mejorado

**Cambios en `generate_next_challenge`:**
- Ahora obtiene y muestra precisión reciente y razonamiento del nivel
- Incluye métricas de rendimiento en la metadata del desafío
- Logging mejorado con información detallada

**Cambios en `_build_prompt`:**
- Prompt adaptativo que considera la precisión reciente del usuario
- Instrucciones específicas para Gemini:
  - Si precisión < 50%: Palabras MÁS COMUNES
  - Si precisión 50-80%: Palabras comunes con ligera complejidad
  - Si precisión > 80%: Palabras conocidas más desafiantes

### 4. Metadata Enriquecida en Desafíos

Ahora cada desafío incluye:
```python
{
    'palabra_objetivo': '...',
    'letras_distractoras': [...],
    'pista_contextual': '...',
    'nivel_dificultad': 'facil|intermedio|dificil',
    'cambio_nivel': bool,
    'nivel_anterior': '...',
    'progreso_nivel': {
        'palabras_completadas': int,
        'palabras_requeridas': 5,
        'porcentaje': float
    },
    'metricas_rendimiento': {  # NUEVO
        'precision_reciente': float,
        'razonamiento': str,
        'tasa_exito_general': float
    }
}
```

## Comparación con Otros Juegos

### Paseo
- Analiza victoria/derrota
- Usa precisión y errores
- Gemini solo en DIFICIL
✅ **Abecedario ahora sigue el mismo patrón**

### Memory/Train
- Evaluación por sesión
- Métricas de precisión
- Adaptación dinámica
✅ **Abecedario ahora tiene evaluación similar**

## Beneficios

1. **Adaptación más inteligente**: El juego ahora responde mejor al rendimiento real del usuario
2. **Prevención de frustración**: Detecta múltiples señales de dificultad, no solo fallos
3. **Progresión más justa**: Requiere buena precisión (>70%) para subir de nivel
4. **Información detallada**: Logs más claros para debugging y análisis
5. **Consistencia**: Ahora todos los juegos usan un sistema similar de adaptación

## Archivos Modificados

1. `app/services/abecedario/abecedario_service.py`
   - `analizar_necesidad_bajar_nivel()` (mejorado)
   - `determinar_nivel_optimo()` (mejorado)

2. `app/services/abecedario/gemini_abecedario_service.py`
   - `generate_next_challenge()` (mejorado)
   - `_build_prompt()` (mejorado)

## Ejemplo de Logs Mejorados

```
[ANÁLISIS] Últimas 5 sesiones:
  - Precisión: 40.0% (2/5)
  - Promedio errores: 7.2
  - Promedio tiempo: 45.3s
  - Pistas usadas: 8

[NIVEL] Muchos errores (7.2 promedio) y baja precisión (40%)
[NIVEL] BAJA de INTERMEDIO → FACIL

[GEMINI] 📊 Análisis de rendimiento:
  - Precisión reciente: 40.0%
  - Estado: Muchos errores y baja precisión

[GEMINI] ✅ Desafío generado: 'CASA' - Nivel: FACIL (0/5)
[GEMINI] 📈 Precisión reciente: 40.0%
[GEMINI] 🔄 CAMBIO DE NIVEL: INTERMEDIO → FACIL
```

## Testing Recomendado

1. Probar con usuario nuevo (debe empezar en FACIL)
2. Simular 5 palabras exitosas con >70% precisión (debe subir)
3. Simular  sesiones con <40% precisión (debe bajar)
4. Verificar que nuevo día resetea a FACIL
5. Comprobar que Unity recibe las nuevas métricas de rendimiento

## Notas

- El sistema ahora es más similar a Paseo, Memory y Train
- Los niveles FACIL e INTERMEDIO siguen usando palabras locales (sin costo de API)
- Solo el nivel DIFICIL usa Gemini AI
- La precisión mínima para subir de nivel (70%) puede ajustarse si es necesario
