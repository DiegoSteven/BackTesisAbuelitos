# 📊 Ejemplo de Logs en Tiempo Real

## ✅ Sistema de Logging Funcionando

El sistema de logging está activo y funcionando correctamente. Aquí hay ejemplos de los logs generados durante las pruebas.

---

## 🧪 Prueba 1: POST /memory-game/submit-results

### Request Enviado:
```json
{
  "user_id": 1,
  "session_data": {
    "completion_status": "completed",
    "total_flips": 10,
    "pairs_found": 3,
    "total_pairs": 3,
    "elapsed_time": 35.0,
    "time_limit": 60,
    "accuracy": 90.0
  }
}
```

### Logs Generados (Visible en Terminal Flask):
```
================================================================================
2025-12-15 21:03:21 - MemoryGameController - INFO - 📥 REQUEST | POST /memory-game/submit-results
2025-12-15 21:03:21 - MemoryGameController - INFO -    Received Data:
2025-12-15 21:03:21 - MemoryGameController - INFO -    {
      "user_id": 1,
      "session_data": {
            "completion_status": "completed",
            "total_flips": 10,
            "pairs_found": 3,
            "total_pairs": 3,
            "elapsed_time": 35.0,
            "time_limit": 60,
            "accuracy": 90.0
      }
   }
2025-12-15 21:03:21 - MemoryGameController - INFO -    Processing session for User ID: 1
2025-12-15 21:03:21 - MemoryGameController - INFO -    Session Status: completed
2025-12-15 21:03:21 - MemoryGameController - INFO -    Accuracy: 90.0%
2025-12-15 21:03:21 - MemoryGameController - INFO -    Time: 35.0s / 60s
2025-12-15 21:03:21 - MemoryGameController - INFO - 📤 RESPONSE | Status: 200 OK
2025-12-15 21:03:21 - MemoryGameController - INFO -    Session Saved: ID=4
2025-12-15 21:03:21 - MemoryGameController - INFO -    AI Score: 9.4/10
2025-12-15 21:03:21 - MemoryGameController - INFO -    Decision: increase_difficulty
2025-12-15 21:03:21 - MemoryGameController - INFO -    New Difficulty: medium
2025-12-15 21:03:21 - MemoryGameController - INFO -    Reason: Excelente desempeño (score 9.4/10). Listo para más desafío. Cambiando de easy a medium.
2025-12-15 21:03:21 - MemoryGameController - INFO -    Response Data:
   {
      "session_saved": true,
      "session_id": 4,
      "ai_analysis": {
         "performance_assessment": {
            "overall_score": 9.4,
            "memory_retention": "high",
            "speed": "high",
            "accuracy": "high"
         },
         "adjustment_decision": "increase_difficulty",
         "next_session_config": {
            "total_pairs": 6,
            "grid_size": "3x4",
            "time_limit": 120,
            "memorization_time": 3,
            "difficulty_label": "medium"
         },
         "reason": "Excelente desempeño (score 9.4/10). Listo para más desafío. Cambiando de easy a medium.",
         "adjustment_summary": {
            "changed_fields": ["total_pairs", "grid_size", "time_limit", "memorization_time"],
            "previous_difficulty": "easy",
            "new_difficulty": "medium"
         }
      }
   }
2025-12-15 21:03:21 - werkzeug - INFO - 127.0.0.1 - - [15/Dec/2025 21:03:21] "POST /memory-game/submit-results HTTP/1.1" 200 -
================================================================================
```

### Análisis del Log:
- ✅ Request recibido correctamente
- ✅ Datos parseados: user_id=1, accuracy=90%, time=35s
- ✅ IA calculó score de **9.4/10** (excelente)
- ✅ Decisión: **increase_difficulty** (easy → medium)
- ✅ Nueva config: 6 pares, grid 3x4, 120s límite
- ✅ Response enviada con código 200

---

## 🧪 Prueba 2: GET /memory-game/config/1

### Logs Generados:
```
================================================================================
2025-12-15 21:03:41 - MemoryGameController - INFO - 📥 REQUEST | GET /memory-game/config/1
2025-12-15 21:03:41 - MemoryGameController - INFO -    User ID: 1
2025-12-15 21:03:41 - MemoryGameController - INFO - 📤 RESPONSE | Status: 200 OK
2025-12-15 21:03:41 - MemoryGameController - INFO -    Config: {
   'total_pairs': 6,
   'grid_size': '3x4',
   'time_limit': 120,
   'memorization_time': 3,
   'difficulty_label': 'medium'
}
2025-12-15 21:03:41 - MemoryGameController - INFO -    First Time: False
2025-12-15 21:03:41 - werkzeug - INFO - 127.0.0.1 - - [15/Dec/2025 21:03:41] "GET /memory-game/config/1 HTTP/1.1" 200 -
================================================================================
```

### Análisis del Log:
- ✅ Usuario 1 consultó su configuración
- ✅ Configuración actual: **medium** (6 pares, 3x4)
- ✅ Ya no es primera vez (se actualizó después del submit anterior)
- ✅ La dificultad aumentó exitosamente

---

## 🎯 Beneficios Observados

### 1. **Visibilidad Completa**
- Puedes ver exactamente qué datos recibe el backend
- Puedes ver qué responde
- Útil para debugging con Unity

### 2. **Análisis de IA Transparente**
- Score calculado visible
- Decisión explicada
- Cambios de configuración documentados

### 3. **Troubleshooting Rápido**
- Si algo falla, el log muestra dónde
- Stack traces completos en errores
- Estados intermedios visibles

### 4. **Monitoreo en Tiempo Real**
- Cada request aparece inmediatamente
- Fácil identificar con emojis (📥📤❌)
- Separadores claros entre requests

---

## 📋 Cómo Interpretar los Logs

### Símbolos:
- `📥` = Request entrante
- `📤` = Response exitosa  
- `❌` = Error ocurrido
- `⚠️` = Validación fallida
- `====...====` = Separador de eventos

### Información Clave a Buscar:
1. **User ID** - Identifica quién hace el request
2. **Session Status** - completed/abandoned/timeout
3. **AI Score** - 0-10, indica desempeño
4. **Decision** - increase/keep_same/decrease
5. **New Difficulty** - A qué nivel cambió

---

## 🚀 Estado Actual

✅ **Servidor Flask:** Corriendo en http://localhost:5000  
✅ **Logging:** Activo y funcional  
✅ **Endpoints:** Todos respondiendo correctamente  
✅ **IA Adaptativa:** Funcionando (score 9.4 → dificultad aumentada)

---

## 📌 Siguiente Paso

Estos logs te permitirán:
1. **Debuggear** la integración con Unity
2. **Verificar** que Unity envía los datos correctos
3. **Monitorear** las decisiones de la IA
4. **Validar** que las configuraciones se actualizan

**Los logs aparecen en tiempo real en la consola donde ejecutas `python app/app.py`**

---

**Documentado:** 2025-12-15 21:03
**Estado:** ✅ Logging funcionando perfectamente
