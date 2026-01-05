# 🧪 Pruebas para API de Juego de Memoria

Este archivo contiene ejemplos de pruebas para los endpoints del juego de memoria.

## 📍 Endpoints Disponibles

### 1. Obtener Configuración del Usuario
**Endpoint:** `GET /memory-game/config/{user_id}`

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/memory-game/config/1
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "current_config": {
      "total_pairs": 3,
      "grid_size": "2x3",
      "time_limit": 60,
      "memorization_time": 5,
      "difficulty_label": "tutorial"
    },
    "is_first_time": true,
    "last_updated": "2025-12-15T20:00:00"
  }
}
```

---

### 2. Enviar Resultados de Sesión
**Endpoint:** `POST /memory-game/submit-results`

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/memory-game/submit-results \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "session_data": {
      "completion_status": "completed",
      "total_flips": 12,
      "pairs_found": 3,
      "total_pairs": 3,
      "elapsed_time": 45.5,
      "time_limit": 60,
      "accuracy": 75.0
    }
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "session_saved": true,
    "session_id": 1,
    "ai_analysis": {
      "performance_assessment": {
        "overall_score": 6.5,
        "memory_retention": "good",
        "speed": "good",
        "accuracy": "good"
      },
      "adjustment_decision": "keep_same",
      "next_session_config": {
        "total_pairs": 3,
        "grid_size": "2x3",
        "time_limit": 60,
        "memorization_time": 5,
        "difficulty_label": "tutorial"
      },
      "reason": "Buen desempeño (score 6.5/10). Mantener nivel actual.",
      "adjustment_summary": {
        "changed_fields": [],
        "previous_difficulty": "tutorial",
        "new_difficulty": "tutorial"
      }
    }
  },
  "timestamp": "2025-12-15T20:00:00Z"
}
```

---

### 3. Obtener Estadísticas del Usuario
**Endpoint:** `GET /memory-game/stats/{user_id}`

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/memory-game/stats/1
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "total_sessions": 5,
    "completed_sessions": 4,
    "average_accuracy": 78.5,
    "best_time": 35.2,
    "recent_sessions": [
      {
        "session_id": 1,
        "difficulty_level": "tutorial",
        "total_pairs": 3,
        "accuracy": 75.0,
        "elapsed_time": 45.5,
        "completion_status": "completed"
      }
    ]
  }
}
```

---

## 🧪 Pruebas con PowerShell

### 1. Obtener Configuración
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/config/1" -Method Get
```

### 2. Enviar Resultados
```powershell
$body = @{
    user_id = 1
    session_data = @{
        completion_status = "completed"
        total_flips = 12
        pairs_found = 3
        total_pairs = 3
        elapsed_time = 45.5
        time_limit = 60
        accuracy = 75.0
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/memory-game/submit-results" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### 3. Obtener Estadísticas
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/stats/1" -Method Get
```

---

## 📊 Escenarios de Prueba

### Escenario 1: Usuario Nuevo (Primera Vez)
1. Hacer GET a `/memory-game/config/1`
2. Debería devolver configuración tutorial con `is_first_time: true`

### Escenario 2: Completar Sesión con Buen Desempeño (Score >= 8)
1. POST a `/memory-game/submit-results` con accuracy > 80% y tiempo rápido
2. Verificar que `adjustment_decision` sea `"increase_difficulty"`
3. Verificar que `new_difficulty` haya subido (ej: tutorial → easy)

### Escenario 3: Completar Sesión con Mal Desempeño (Score < 5)
1. POST con accuracy baja o tiempo excedido
2. Verificar que `adjustment_decision` sea `"decrease_difficulty"`

### Escenario 4: Verificar Estadísticas
1. Completar varias sesiones
2. GET a `/memory-game/stats/1`
3. Verificar que los promedios sean correctos

---

## ✅ Checklist de Implementación Completada

- [x] Modelo `MemoryGameSession`
- [x] Modelo `MemoryGameConfig`
- [x] Servicio `AIAdapterService`
- [x] Servicio `MemoryGameService`
- [x] Controlador `MemoryGameController`
- [x] Rutas registradas en `app.py`
- [x] Servidor Flask corriendo
- [ ] Tablas creadas en base de datos (automático al iniciar)
- [ ] Pruebas de endpoints realizadas

---

## 🔧 Próximos Pasos

1. **Probar cada endpoint** usando las pruebas de PowerShell arriba
2. **Verificar que las tablas se crearon** en la base de datos PostgreSQL
3. **Integrar con Unity** usando los mismos endpoints
4. **Agregar endpoints a Swagger** (opcional)

## 🐛 Troubleshooting

### Error: "No such column: user_id"
- Las tablas se crean automáticamente al iniciar Flask
- Si persiste, verifica que Docker esté corriendo con PostgreSQL

### Error: "Foreign key constraint"
- Asegúrate que existe un usuario con id=1 en la tabla users
- Crear usuario de prueba con: `POST /register`

### Error 500 en submit-results
- Verifica que todos los campos requeridos estén en `session_data`
- Campos obligatorios: `completion_status`, `elapsed_time`, `time_limit`, `accuracy`
