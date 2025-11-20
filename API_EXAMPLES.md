
# API Endpoints de Usuario

## Registro de Usuario
```bash
POST http://localhost:5000/register
Content-Type: application/json

{
    "nombre": "usuario1",
    "password": "password123",
    "edad": 65,
    "genero": "M"
}
```

## Login
```bash
POST http://localhost:5000/login
Content-Type: application/json

{
    "nombre": "usuario1",
    "password": "password123"
}
```

## Ver Todos los Usuarios
```bash
GET http://localhost:5000/users
```

## Ejemplo de Respuesta de Registro
```json
{
    "message": "Usuario registrado exitosamente",
    "user": {
        "id": 1,
        "nombre": "usuario1",
        "edad": 65,
        "genero": "M"
    }
}
```

## Ejemplo de Respuesta de Login
```json
{
    "message": "Login exitoso",
    "user": {
        "id": 1,
        "nombre": "usuario1",
        "edad": 65,
        "genero": "M"
    }
}
```

## Ejemplo de Respuesta de Listado de Usuarios
```json
{
    "users": [
        {
            "id": 1,
            "nombre": "usuario1",
            "edad": 65,
            "genero": "M"
        },
        {
            "id": 2,
            "nombre": "usuario2",
            "edad": 70,
            "genero": "F"
        }
    ]
}
```

---

# API Endpoints del Juego Abecedario

## 1. Obtener Siguiente Desafío (Next Challenge)
**Descripción:** Genera un nuevo desafío de palabra adaptativo basado en el rendimiento del usuario.

**Endpoint:** `GET /abecedario/next-challenge/<user_id>`

**Ejemplo:**
```bash
GET http://localhost:5000/abecedario/next-challenge/1
```

**Respuesta:**
```json
{
    "challenge": {
        "palabra_objetivo": "CAFÉ",
        "letras_distractoras": ["L", "M"],
        "pista_contextual": "Bebida caliente muy popular en las mañanas",
        "nivel_dificultad": "facil",
        "progreso_nivel": {
            "palabras_completadas": 2,
            "palabras_requeridas": 5,
            "porcentaje": 40.0
        }
    },
    "timestamp": "2025-11-16T20:30:00.000000"
}
```

**Qué hace:**
- Analiza el historial de sesiones del usuario
- Determina el nivel apropiado (facil/intermedio/dificil)
- Detecta si el usuario tuvo muchos errores (≥8) y baja de nivel
- Sube de nivel después de completar 5 palabras exitosamente
- Evita repetir las últimas 10 palabras jugadas
- Genera palabras en MAYÚSCULAS con acentos (CAFÉ, NIÑO, etc.)

---

## 2. Guardar Sesión
**Descripción:** Guarda los resultados de una sesión de juego completada.

**Endpoint:** `POST /abecedario/session`

**Ejemplo:**
```bash
POST http://localhost:5000/abecedario/session
Content-Type: application/json

{
    "user_id": 1,
    "palabra_objetivo": "CAFÉ",
    "tiempo_resolucion": 45.5,
    "cantidad_errores": 2,
    "pistas_usadas": 0,
    "completado": true,
    "nivel_dificultad": "facil"
}
```

**Respuesta:**
```json
{
    "message": "Sesión guardada exitosamente",
    "session": {
        "id": 1,
        "user_id": 1,
        "palabra_objetivo": "CAFÉ",
        "longitud_palabra": 4,
        "tiempo_resolucion": 45.5,
        "cantidad_errores": 2,
        "pistas_usadas": 0,
        "completado": true,
        "created_at": "2025-11-16T20:30:00.000000",
        "fecha_juego": "2025-11-16"
    }
}
```

**Qué hace:**
- Guarda todas las métricas de la sesión (tiempo, errores, pistas)
- Detecta automáticamente si hubo cambio de nivel
- Marca la primera sesión con `cambio_nivel=True`
- Resetea el contador de progreso cuando cambia de nivel

---

## 3. Ver Estadísticas de Rendimiento
**Descripción:** Obtiene estadísticas generales del usuario.

**Endpoint:** `GET /abecedario/stats/<user_id>`

**Ejemplo:**
```bash
GET http://localhost:5000/abecedario/stats/1
```

**Respuesta:**
```json
{
    "stats": {
        "promedio_tiempo": 42.5,
        "promedio_errores": 3.2,
        "tasa_exito": 85.0,
        "total_sesiones": 10,
        "completadas": 8,
        "ultima_palabra": "CAFÉ",
        "tendencia": "mejorando",
        "sesion_reciente_dificil": false,
        "ultimas_3_errores": 2.5
    }
}
```

**Qué hace:**
- Calcula promedios de tiempo y errores
- Determina tasa de éxito (% de palabras completadas)
- Detecta tendencia (mejorando/empeorando/estable)
- Identifica si las últimas sesiones fueron difíciles (≥8 errores)

---

## 4. Ver Resumen Diario
**Descripción:** Obtiene resumen de sesiones de un día específico.

**Endpoint:** `GET /abecedario/daily-summary/<user_id>?fecha=YYYY-MM-DD`

**Ejemplo:**
```bash
GET http://localhost:5000/abecedario/daily-summary/1?fecha=2025-11-16
```

**Respuesta:**
```json
{
    "fecha": "2025-11-16",
    "total_palabras": 5,
    "palabras_completadas": 4,
    "tiempo_total": 210.5,
    "errores_totales": 12,
    "promedio_tiempo": 42.1,
    "sesiones": [
        {
            "id": 1,
            "palabra_objetivo": "CAFÉ",
            "tiempo_resolucion": 45.5,
            "cantidad_errores": 2,
            "completado": true
        }
    ]
}
```

**Qué hace:**
- Agrupa todas las sesiones de una fecha
- Si no se envía fecha, usa el día actual
- Calcula totales y promedios del día

---

## 5. Ver Historial de Sesiones
**Descripción:** Obtiene el historial de sesiones con filtro opcional por fechas.

**Endpoint:** `GET /abecedario/history/<user_id>?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD`

**Ejemplo sin filtro (últimas 20 sesiones):**
```bash
GET http://localhost:5000/abecedario/history/1
```

**Ejemplo con filtro de fechas:**
```bash
GET http://localhost:5000/abecedario/history/1?fecha_inicio=2025-11-01&fecha_fin=2025-11-16
```

**Respuesta:**
```json
{
    "sesiones": [
        {
            "id": 10,
            "user_id": 1,
            "palabra_objetivo": "JARDÍN",
            "longitud_palabra": 6,
            "tiempo_resolucion": 38.2,
            "cantidad_errores": 1,
            "pistas_usadas": 0,
            "completado": true,
            "created_at": "2025-11-16T20:30:00.000000",
            "fecha_juego": "2025-11-16"
        }
    ],
    "total": 10
}
```

**Qué hace:**
- Sin parámetros: devuelve las últimas 20 sesiones
- Con fecha_inicio y fecha_fin: filtra por rango de fechas
- Muestra todas las métricas de cada sesión

---

## 6. Ver Reporte de Evolución
**Descripción:** Obtiene reporte agrupado por fecha y nivel de dificultad.

**Endpoint:** `GET /abecedario/evolution/<user_id>`

**Ejemplo:**
```bash
GET http://localhost:5000/abecedario/evolution/1
```

**Respuesta:**
```json
{
    "total_sesiones": 15,
    "evolucion": [
        {
            "fecha": "2025-11-16",
            "nivel": "DIFICIL",
            "total_palabras": 3,
            "completadas": 2,
            "tiempo_total": 125.5,
            "errores_totales": 8,
            "pistas_usadas": 1,
            "promedio_tiempo": 41.83,
            "promedio_errores": 2.67,
            "tasa_exito": 66.67
        },
        {
            "fecha": "2025-11-16",
            "nivel": "INTERMEDIO",
            "total_palabras": 5,
            "completadas": 5,
            "tiempo_total": 200.0,
            "errores_totales": 10,
            "pistas_usadas": 0,
            "promedio_tiempo": 40.0,
            "promedio_errores": 2.0,
            "tasa_exito": 100.0
        },
        {
            "fecha": "2025-11-15",
            "nivel": "FACIL",
            "total_palabras": 7,
            "completadas": 6,
            "tiempo_total": 280.0,
            "errores_totales": 15,
            "pistas_usadas": 2,
            "promedio_tiempo": 40.0,
            "promedio_errores": 2.14,
            "tasa_exito": 85.71
        }
    ]
}
```

**Qué hace:**
- Agrupa sesiones por fecha Y nivel de dificultad
- Calcula métricas promedio para cada grupo
- Muestra tasa de éxito por nivel
- Ordena por fecha descendente (más recientes primero)
- Útil para ver la progresión del usuario a través de los niveles

---

## Sistema de Niveles Adaptativos

### Niveles:
1. **FACIL**: Palabras de 3-4 letras, 0-1 letras distractoras
2. **INTERMEDIO**: Palabras de 4-6 letras, 1-2 letras distractoras  
3. **DIFICIL**: Palabras de 5-7 letras, 0-1 letras distractoras

### Reglas de Progresión:
- **Usuario nuevo**: Empieza en nivel FACIL
- **Subir de nivel**: Completar 5 palabras exitosamente en el nivel actual
- **Bajar de nivel**: Tener 8 o más errores en una sola sesión
- **Nivel máximo**: DIFICIL (no sube más)

### Contador de Progreso:
- Se resetea automáticamente al cambiar de nivel
- Solo cuenta palabras completadas (`completado=true`)
- Cuenta desde el último cambio de nivel (inclusive)

---

## Notas Importantes

1. **Unity debe enviar `nivel_dificultad`**: El frontend debe enviar el nivel recibido de `/next-challenge` al guardar la sesión en `/session`

2. **Las tablas se crean automáticamente**: Flask con SQLAlchemy crea las tablas al iniciar (`db.create_all()`)

3. **Tabla en base de datos**: `word_game_session` (nombre de tabla legacy, pero la clase se llama `Abecedario`)

4. **Anti-repetición**: El sistema evita repetir las últimas 10 palabras jugadas

5. **Palabras en MAYÚSCULAS**: Todas las palabras generadas están en mayúsculas y pueden tener acentos (CAFÉ, NIÑO, ÁRBOL)