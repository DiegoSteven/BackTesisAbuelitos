# Tests de Abecedario

## Descripción

Este directorio contiene dos tipos de pruebas para el juego de Abecedario:

### 1. `test_abecedario_gemini.py` - Prueba de Carga Concurrente

**Objetivo**: Medir el límite de usuarios concurrentes que soporta la API KEY de Gemini.

**Características**:
- Crea múltiples usuarios simultáneos
- Cada usuario juega múltiples sesiones
- Fuerza el nivel DIFICIL para máximo uso de Gemini
- Mide tiempos de respuesta y tasa de error
- Genera reporte JSON con resultados

**Uso**:
```bash
python test_abecedario_gemini.py
```

**Ejemplo de configuración**:
- Usuarios concurrentes: 20
- Sesiones por usuario: 15 (para llegar a nivel DIFICIL)

### 2. `test_abecedario_evolucion_5dias.py` - Prueba de Evolución (NUEVO)

**Objetivo**: Simular la evolución de un usuario a lo largo de 5 días para verificar el nuevo sistema de adaptación de niveles.

**Características**:
- Simula 1 usuario durante 5 días
- Permite configurar diferentes perfiles de rendimiento por día
- 8-12 palabras por día
- Muestra métricas detalladas en tiempo real
- Visualiza la evolución completa al final
- Genera reporte JSON con análisis de tendencia

**Perfiles de Rendimiento Disponibles**:

| Perfil | Precisión | Errores Promedio | Tiempo Base | Uso de Pistas |
|--------|-----------|------------------|-------------|---------------|
| `mejorando` | 85% | 1.5 | 15s | Bajo (0.3) |
| `estable_bueno` | 90% | 1.0 | 12s | Muy bajo (0.2) |
| `estable_medio` | 70% | 3.0 | 20s | Moderado (1.0) |
| `frustrado` | 30% | 6.0 | 35s | Alto (2.0) |
| `variable` | 60% | 4.0 | 22s | Moderado (1.5) |

**Uso**:
```bash
python test_abecedario_evolucion_5dias.py
```

**Escenarios de Ejemplo**:

#### Escenario 1: Usuario Mejorando 📈
```
Día 1: frustrado      -> Usuario empieza con dificultades
Día 2: estable_medio  -> Mejora gradual
Día 3: estable_medio  -> Se mantiene
Día 4: mejorando      -> Continúa mejorando
Día 5: estable_bueno  -> Alcanza buen rendimiento
```
**Resultado Esperado**: El sistema debería subir gradualmente de nivel (FACIL → INTERMEDIO → DIFICIL)

#### Escenario 2: Usuario Con Dificultades 📉
```
Día 1: estable_medio  -> Rendimiento aceptable
Día 2: estable_medio  -> Se mantiene
Día 3: frustrado      -> Empieza a tener problemas
Día 4: frustrado      -> Continúan los problemas
Día 5: frustrado      -> Frustración persistente
```
**Resultado Esperado**: El sistema debería bajar de nivel para evitar frustración

#### Escenario 3: Usuario Estable 📊
```
Día 1: estable_bueno
Día 2: estable_bueno
Día 3: estable_bueno
Día 4: estable_bueno
Día 5: estable_bueno
```
**Resultado Esperado**: El sistema debería mantener el nivel apropiado o subir gradualmente

#### Escenario 4: Usuario Inconsistente 🎲
```
Día 1: estable_bueno
Día 2: variable
Día 3: frustrado
Día 4: mejorando
Día 5: variable
```
**Resultado Esperado**: El sistema debería adaptarse a los cambios, bajando cuando detecta frustración

## Información que Muestra el Test de Evolución

### Durante el Juego:
Para cada palabra jugada muestra:
```
✅ Palabra  1 🔄
   🟢 Nivel: FACIL      | Progreso: 1/5
   📊 Precisión reciente: 80.0% - Rendimiento aceptable
   ⏱️  15.3s | ❌ 2 err | 💡 0 pistas
```

### Resumen Diario:
```
📊 RESUMEN DEL DÍA 1
──────────────────────────────────────────────────────────────────────
  Palabras jugadas:     10
  Palabras completadas: 8 (80.0%)
  Nivel inicial:        FACIL
  Nivel final:          INTERMEDIO
  Cambios de nivel:     1

  Promedios:
    • Tiempo:   15.5s
    • Errores:  2.1
    • Pistas:   0.4

  Distribución de niveles:
    • Facil        : 6 palabras
    • Intermedio   : 4 palabras
```

### Evolución Completa (5 días):
```
═══════════════════════════════════════════════════════════════════════
📈 EVOLUCIÓN COMPLETA - 5 DÍAS
═══════════════════════════════════════════════════════════════════════

Día   Nivel       Palabras  Precisión  ⏱️ Tiempo  ❌ Errores  💡 Pistas
──────────────────────────────────────────────────────────────────────
1     FAC→INT         8/10      80.0%      15.5s       2.1        0.4
2     INT→INT         9/11      81.8%      14.2s       1.8        0.3
3     INT→DIF         9/10      90.0%      13.1s       1.2        0.2
4     DIF→DIF         8/9       88.9%      12.8s       1.1        0.1
5     DIF→DIF         9/10      90.0%      12.5s       1.0        0.1

═══════════════════════════════════════════════════════════════════════
🔍 ANÁLISIS DE TENDENCIA
═══════════════════════════════════════════════════════════════════════

📊 Precisión:  80.0% → 90.0% (+10.0%)
❌ Errores:    2.1 → 1.0 (-1.1)
🎯 Nivel:      FACIL → DIFICIL

💡 CONCLUSIÓN:
   ✅ El usuario mostró una MEJORA SIGNIFICATIVA en su rendimiento
   ✅ El sistema adaptó correctamente la dificultad según su evolución
```

## Salidas JSON

Ambos tests generan archivos JSON con resultados detallados:

### `test_abecedario_YYYYMMDD_HHMMSS.json`:
```json
{
  "usuarios_creados": 20,
  "sesiones_exitosas": 237,
  "sesiones_fallidas": 63,
  "llamadas_gemini_estimadas": 37,
  "sesiones_por_nivel": {
    "facil": 100,
    "intermedio": 100,
    "dificil": 37
  },
  "tiempos_respuesta": [...],
  "hora_inicio": "2026-01-18 16:00:00",
  "hora_fin": "2026-01-18 16:05:30"
}
```

### `test_evolucion_5dias_YYYYMMDD_HHMMSS.json`:
```json
{
  "user_id": 123,
  "user_name": "evolucion_test_1737237600",
  "evolucion_diaria": [
    {
      "dia": 1,
      "total_palabras": 10,
      "palabras_completadas": 8,
      "precision": 80.0,
      "nivel_inicial": "facil",
      "nivel_final": "intermedio",
      "tiempo_promedio": 15.5,
      "errores_promedio": 2.1,
      "pistas_promedio": 0.4,
      "cambios_nivel": 1
    }
    // ... días 2-5
  ],
  "resumen": {
    "precision_inicial": 80.0,
    "precision_final": 90.0,
    "mejora_precision": 10.0,
    "errores_inicial": 2.1,
    "errores_final": 1.0,
    "nivel_inicial": "facil",
    "nivel_final": "dificil"
  }
}
```

## Requisitos

- Backend corriendo en `http://localhost:5000`
- Python 3.8+
- Paquetes: `requests`

```bash
pip install requests
```

## Notas Importantes

### Sistema de Adaptación Verificado:

El test de evolución permite verificar que el sistema:

1. ✅ **Detecta frustración** cuando:
   - Precisión < 40%
   - Muchos errores (>5 promedio) con precisión <60%
   - Tiempos muy altos (>60s) con precisión <50%
   - Exceso de pistas (>10 en 5 sesiones) con precisión <70%

2. ✅ **Sube de nivel** cuando:
   - Completa 5 palabras con >70% de precisión

3. ✅ **Resetea a FACIL** cada nuevo día para comparar evolución

4. ✅ **Mantiene nivel** cuando el rendimiento es aceptable pero no excepcional

## Interpretación de Resultados

### Signos de Buen Sistema de Adaptación:
- ✅ Usuario frustrado → Sistema baja el nivel
- ✅ Usuario mejorando → Sistema sube el nivel gradualmente
- ✅ Usuario estable → Sistema mantiene el nivel apropiado
- ✅ Precisión requerida para subir (>70%) evita promociones prematuras

### Signos de Problemas:
- ❌ Usuario con baja precisión permanece en nivel difícil
- ❌ Usuario con alta precisión no sube de nivel
- ❌ Niveles cambian demasiado rápido sin razón clara

## Ejemplos de Ejecución

### Test de Evolución - Sesión Completa
```bash
$ python test_abecedario_evolucion_5dias.py

🔧 Asegúrate de que el backend esté corriendo en http://localhost:5000
Presiona ENTER para continuar...

╔═══════════════════════════════════════════════════════════════╗
║   PRUEBA DE EVOLUCIÓN - ABECEDARIO 5 DÍAS                     ║
║   Simula el progreso de un usuario a lo largo del tiempo      ║
╚═══════════════════════════════════════════════════════════════╝

✅ Usuario creado: evolucion_test_1737237600 (ID: 45)

Día 1: mejorando
Día 2: mejorando
Día 3: estable_bueno
Día 4: estable_bueno
Día 5: estable_bueno

⚡ Iniciando simulación de 5 días...
```

## Dashboard de Verificación

Después de ejecutar el test, puedes verificar los resultados en:
1. **Dashboard Admin** → Ver usuario creado
2. **Sección Abecedario** → Ver historial por sesión → niveles → palabras
3. **Estadísticas** → Verificar nivel alcanzado y métricas

La nueva estructura jerárquica del dashboard mostrará:
```
📅 Sesión: 2026-01-18
  ├── 🟢 FACIL (5 palabras)
  ├── 🟡 INTERMEDIO (3 palabras)
  └── 🔴 DIFICIL (2 palabras)
```
