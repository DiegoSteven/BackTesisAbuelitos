# 📡 API Endpoints - Backend Abuelitos

Referencia completa de todos los endpoints disponibles en el backend.

**Base URL:** `http://localhost:5000`

---

## 👤 USUARIOS

### 1. Listar Usuarios
```http
GET /users
```
**Descripción:** Obtiene la lista de todos los usuarios registrados

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "nombre": "TestUser",
      "edad": 70,
      "genero": "M"
    }
  ]
}
```

---

### 2. Registrar Usuario
```http
POST /register
```
**Descripción:** Crea un nuevo usuario en el sistema

**Request Body:**
```json
{
  "nombre": "TestUser",
  "password": "test123",
  "edad": 70,
  "genero": "M"
}
```

**Response:**
```json
{
  "message": "Usuario registrado exitosamente"
}
```

---

### 3. Login
```http
POST /login
```
**Descripción:** Autentica un usuario existente

**Request Body:**
```json
{
  "nombre": "TestUser",
  "password": "test123"
}
```

**Response:**
```json
{
  "message": "Login exitoso",
  "user_id": 1
}
```

---

## 🔤 JUEGO ABECEDARIO

### 4. Guardar Sesión de Abecedario
```http
POST /abecedario/session
```
**Descripción:** Guarda los resultados de una sesión del juego del abecedario

**Request Body:**
```json
{
  "user_id": 1,
  "letter": "A",
  "correct": true,
  "time_taken": 5.2
}
```

---

### 5. Obtener Siguiente Desafío
```http
GET /abecedario/next-challenge/{user_id}
```
**Descripción:** Obtiene la siguiente letra/desafío para el usuario

**Ejemplo:** `GET /abecedario/next-challenge/1`

**Response:**
```json
{
  "next_letter": "B",
  "difficulty": "medium"
}
```

---

### 6. Estadísticas de Abecedario
```http
GET /abecedario/stats/{user_id}
```
**Descripción:** Obtiene estadísticas de rendimiento del usuario en el abecedario

**Ejemplo:** `GET /abecedario/stats/1`

---

### 7. Resumen Diario de Abecedario
```http
GET /abecedario/daily-summary/{user_id}
```
**Descripción:** Obtiene el resumen del progreso diario del usuario

**Ejemplo:** `GET /abecedario/daily-summary/1`

---

### 8. Historial de Abecedario
```http
GET /abecedario/history/{user_id}
```
**Descripción:** Obtiene el historial completo de sesiones del usuario

**Ejemplo:** `GET /abecedario/history/1`

---

### 9. Reporte de Evolución
```http
GET /abecedario/evolution/{user_id}
```
**Descripción:** Obtiene un reporte de la evolución del usuario a lo largo del tiempo

**Ejemplo:** `GET /abecedario/evolution/1`

---

## 🧠 JUEGO DE MEMORIA

### 10. Obtener Configuración del Juego
```http
GET /memory-game/config/{user_id}
```
**Descripción:** Obtiene la configuración actual adaptativa del juego de memoria para el usuario

**Ejemplo:** `GET /memory-game/config/1`

**Response:**
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

**Cuándo usar:** Al iniciar el juego para obtener los parámetros (cuántos pares, tiempo límite, etc.)

---

### 11. Enviar Resultados de Sesión
```http
POST /memory-game/submit-results
```
**Descripción:** Envía los resultados de una sesión completada y recibe análisis de IA con nueva configuración adaptada

**Request Body:**
```json
{
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
}
```

**Response:**
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

**Cuándo usar:** Al terminar una partida (completada, abandonada, o tiempo agotado)

---

### 12. Obtener Estadísticas del Jugador
```http
GET /memory-game/stats/{user_id}
```
**Descripción:** Obtiene estadísticas acumuladas del jugador en el juego de memoria

**Ejemplo:** `GET /memory-game/stats/1`

**Response:**
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

**Cuándo usar:** Para mostrar progreso/estadísticas del jugador (pantalla de perfil, menú)

---

## 📚 DOCUMENTACIÓN

### 13. Swagger UI (Documentación Interactiva)
```http
GET /api/docs
```
**Descripción:** Interfaz interactiva Swagger para explorar y probar la API

**URL:** `http://localhost:5000/api/docs`

---

## 📊 Resumen por Juego

### 🔤 Abecedario (6 endpoints)
1. `POST /abecedario/session` - Guardar sesión
2. `GET /abecedario/next-challenge/{user_id}` - Siguiente desafío
3. `GET /abecedario/stats/{user_id}` - Estadísticas
4. `GET /abecedario/daily-summary/{user_id}` - Resumen diario
5. `GET /abecedario/history/{user_id}` - Historial
6. `GET /abecedario/evolution/{user_id}` - Evolución

### 🧠 Memory Game (3 endpoints)
1. `GET /memory-game/config/{user_id}` - 🎮 Configuración adaptativa
2. `POST /memory-game/submit-results` - 📊 Enviar resultados + IA
3. `GET /memory-game/stats/{user_id}` - 📈 Estadísticas

### 👤 Usuarios (3 endpoints)
1. `GET /users` - Listar
2. `POST /register` - Registrar
3. `POST /login` - Autenticar

---

## 🔑 Campos Importantes

### Memory Game - completion_status
- `"completed"` - Juego completado exitosamente
- `"abandoned"` - Jugador abandonó
- `"timeout"` - Se acabó el tiempo

### Memory Game - adjustment_decision
- `"increase_difficulty"` - Score ≥ 8.0 → Sube nivel
- `"keep_same"` - Score 5.0-7.9 → Mantiene nivel  
- `"decrease_difficulty"` - Score < 5.0 → Baja nivel

### Memory Game - difficulty_label
- `"tutorial"` - 3 pares, 2x3, 60s
- `"easy"` - 4 pares, 2x4, 90s
- `"medium"` - 6 pares, 3x4, 120s
- `"hard"` - 8 pares, 4x4, 180s

---

## 🧪 Ejemplos de Prueba (PowerShell)

### Registrar Usuario
```powershell
$body = @{ nombre = "TestUser"; password = "test123"; edad = 70; genero = "M" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/register" -Method Post -ContentType "application/json" -Body $body
```

### Obtener Config de Memory Game
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/config/1" -Method Get
```

### Enviar Resultados
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
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:5000/memory-game/submit-results" -Method Post -ContentType "application/json" -Body $body
```

---

## 📋 Total de Endpoints

**Total:** 13 endpoints  
- Usuarios: 3
- Abecedario: 6  
- Memory Game: 3
- Documentación: 1

---

## 🔗 Enlaces Útiles

- **Backend Local:** http://localhost:5000
- **Swagger Docs:** http://localhost:5000/api/docs
- **Logs:** Ver terminal donde corre `python app/app.py`

---

**Estado:** ✅ Todos los endpoints funcionando  
**Última actualización:** 2025-12-15
