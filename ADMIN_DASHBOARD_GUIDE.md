# 🎯 Dashboard Administrativo + Reset de Usuario

## Implementación Completada

Se han agregado dos nuevas funcionalidades al backend:

---

## 1. 🔄 Endpoint de Reset de Usuario

### DELETE /memory-game/reset/{user_id}

**Descripción:** Resetea el progreso de un usuario eliminando todas sus sesiones y configuración. El usuario volverá al nivel tutorial.

**Request:**
```http
DELETE http://localhost:5000/memory-game/reset/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sessions_deleted": 8,
    "config_deleted": 1,
    "message": "Usuario 1 reseteado a nivel tutorial"
  }
}
```

### Uso en PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/reset/1" -Method Delete
```

### Script Python Alternativo:
También puedes usar el script `app/reset_user_progress.py`:

```bash
# Edita USER_ID en el archivo
python app/reset_user_progress.py
```

---

## 2. 📊 Dashboard Administrativo

### Acceso al Dashboard

**URL:** `http://localhost:5000/admin`

### Características

#### 📈 Estadísticas Globales
- **Total Usuarios:** Número de usuarios registrados
- **Partidas Hoy:** Sesiones jugadas hoy
- **Partidas Totales:** Todas las sesiones históricas
- **Accuracy Promedio:** Precisión promedio de todos los jugadores

#### 👥 Lista de Usuarios
- Ver todos los usuarios registrados
- ID, nombre, edad, género

#### 🧠 Sesiones de Memory Game
- Últimas 20 partidas jugadas
- Información detallada:
  - ID de sesión
  - Usuario  
  - Dificultad (tutorial/easy/medium/hard)
  - Pares encontrados/totales
  - Accuracy %
  - Tiempo
  - Estado (completed/abandoned/timeout)
  - Fecha y hora

#### ⚙️ Configuraciones Actuales
- Configuración actual de cada usuario
- Nivel de dificultad
- Parámetros: pares, grid, tiempo límite, tiempo de memorización

### Auto-Refresh
- El dashboard se actualiza automáticamente cada 30 segundos
- Botón manual "🔄 Actualizar" disponible

---

## 3. 📡 Nuevos Endpoints Administrativos

### GET /admin/memory-sessions
Obtiene las últimas 20 sesiones de Memory Game

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": 1,
      "user_id": 1,
      "difficulty_level": "medium",
      "total_pairs": 6,
      "pairs_found": 6,
      "accuracy": 100.0,
      "elapsed_time": 65.5,
      "completion_status": "completed",
      "finished_at": "2025-12-15T22:00:00"
    }
  ]
}
```

### GET /admin/memory-configs
Obtiene todas las configuraciones actuales

**Response:**
```json
{
  "success": true,
  "configs": [
    {
      "user_id": 1,
      "total_pairs": 6,
      "grid_size": "3x4",
      "time_limit": 120,
      "memorization_time": 3,
      "difficulty_label": "medium",
      "last_updated": "2025-12-15T22:00:00"
    }
  ]
}
```

### GET /admin/stats
Obtiene estadísticas globales del sistema

**Response:**
```json
{
  "success": true,
  "total_sessions": 25,
  "sessions_today": 5,
  "average_accuracy": 78.5
}
```

---

## 🚀 Cómo Usar

### 1. Reiniciar Flask
```bash
# Detener el servidor actual (CTRL+C)
python app/app.py
```

### 2. Acceder al Dashboard
Abre tu navegador en:
```
http://localhost:5000/admin
```

### 3. Resetear un Usuario
```powershell
# Opción 1: Via API
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/reset/1" -Method Delete

# Opción 2: Via Script Python
python app/reset_user_progress.py
```

---

## 📁 Archivos Creados/Modificados

### Nuevos Archivos:
1. **`app/static/admin_dashboard.html`** - Dashboard administrativo
2. **`app/controllers/admin_controller.py`** - Controlador admin
3. **`app/reset_user_progress.py`** - Script de reset

### Archivos Modificados:
1. **`app/app.py`**
   - Agregada ruta `/admin` para servir el dashboard
   - Agregadas rutas admin: `/admin/memory-sessions`, `/admin/memory-configs`, `/admin/stats`
   - Agregada ruta reset: `DELETE /memory-game/reset/{user_id}`

2. **`app/services/memory_game/memory_game_service.py`**
   - Agregado método `reset_user_progress()`

3. **`app/controllers/memory_game_controller.py`**
   - Agregado endpoint `reset_progress()`

---

## 🎨 Características del Dashboard

### Diseño Moderno
- Gradiente violeta atractivo
- Tarjetas con sombras y animaciones
- Responsive (se adapta a móvil/tablet/desktop)
- Badges de colores para estados y dificultades:
  - 🟦 Tutorial (azul)
  - 🟩 Easy (verde)
  - 🟧 Medium (naranja)
  - 🟥 Hard (rojo)

### Interactividad
- Hover effects en tarjetas y tablas
- Botón de refresh animado
- Loading states
- Empty states cuando no hay datos

### Actualización en Tiempo Real
- Auto-refresh cada 30 segundos
- Refresh manual con botón
- Animación pulse mientras carga

---

## 📊 Resumen de Endpoints Totales

**Total de Endpoints:** 17

- **Usuarios:** 3
- **Abecedario:** 6
- **Memory Game:** 4 (+ 1 DELETE nuevo)
- **Admin:** 3 (nuevos)
- **Docs:** 1

---

## ✅ Pruebas Sugeridas

### 1. Probar Reset
```powershell
# Resetear usuario 1
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/reset/1" -Method Delete

# Verificar que volvió a tutorial
Invoke-RestMethod -Uri "http://localhost:5000/memory-game/config/1" -Method Get
```

### 2. Probar Dashboard
1. Abre `http://localhost:5000/admin`
2. Ver hay que datos se muestran
3. Hacer una partida nueva
4. Presionar "Actualizar" en el dashboard
5. Verificar que aparece la nueva sesión

---

## 🔒 Notas de Seguridad

⚠️ **Importante:** Este dashboard es solo para desarrollo/demostración local.

Para producción deberías agregar:
- Autenticación (login admin)
- Autorización (verificar permisos)
- HTTPS
- Rate limiting
- Validación de inputs

---

## 📖 Documentación Relacionada

- **API Endpoints:** `API_ENDPOINTS_REFERENCE.md`
- **Ejemplos de Uso:** `API_USAGE_EXAMPLES.md`
- **Integración Unity:** `UNITY_INTEGRATION_GUIDE.md`

---

**Estado:** ✅ Implementación completa  
**Fecha:** 2025-12-15  
**Próximo paso:** Reiniciar Flask y probar el dashboard 🚀
