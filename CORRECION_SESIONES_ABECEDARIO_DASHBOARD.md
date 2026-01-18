# Corrección del Conteo de Sesiones en Dashboard - Abecedario

## Fecha: 2026-01-18

## Problema Identificado
El dashboard estaba contando cada **palabra jugada** como una sesión individual en el juego de Abecedario, lo cual es incorrecto. Los otros juegos (Paseo, Memory, Train) cuentan correctamente sus sesiones como eventos completos de juego.

### Ejemplo del Problema:
Si un usuario jugó 5 palabras en un día:
- **Antes**: Dashboard mostraba 5 sesiones ❌
- **Correcto**: Dashboard debe mostrar 1 sesión ✅

## Solución Implementada

### Definición de Sesión en Abecedario
Una **sesión de juego de Abecedario** = Todas las palabras jugadas por un usuario en un día específico

**Razón**: 
- El juego se resetea cada día (vuelve a FACIL)
- Las palabras se juegan de forma continua en una misma sesión
- Es consistente con cómo funcionan los otros juegos

### Cambios Realizados

#### 1. `AdminController.get_user_stats_all_games()`
**Ubicación**: `app/controllers/admin_controller.py` líneas 67-132

**Antes**:
```python
abecedario_sessions = Abecedario.query.filter_by(user_id=user_id).all()
abecedario_stats = {
    'total_sesiones': len(abecedario_sessions),  # ❌ Cuenta cada palabra
    'palabras_completadas': sum([1 for s in abecedario_sessions if s.completado]),
    'tiempo_promedio': sum([s.tiempo_resolucion for s in abecedario_sessions]) / len(abecedario_sessions)
}
```

**Ahora**:
```python
abecedario_palabras = Abecedario.query.filter_by(user_id=user_id).all()

# Agrupar palabras por fecha (una sesión = un día de juego)
sesiones_por_dia = {}
for palabra in abecedario_palabras:
    fecha = palabra.fecha_juego
    if fecha not in sesiones_por_dia:
        sesiones_por_dia[fecha] = {
            'palabras_totales': 0,
            'palabras_completadas': 0,
            'tiempo_total': 0
        }
    sesiones_por_dia[fecha]['palabras_totales'] += 1
    if palabra.completado:
        sesiones_por_dia[fecha]['palabras_completadas'] += 1
    sesiones_por_dia[fecha]['tiempo_total'] += palabra.tiempo_resolucion

# Calcular estadísticas
total_sesiones_abc = len(sesiones_por_dia)  # ✅ Una sesión por día
palabras_completadas_total = sum([s['palabras_completadas'] for s in sesiones_por_dia.values()])
tiempo_total = sum([s['tiempo_total'] for s in sesiones_por_dia.values()])

abecedario_stats = {
    'total_sesiones': total_sesiones_abc,  # ✅ Sesiones de juego (días jugados)
    'palabras_completadas': palabras_completadas_total,
    'tiempo_promedio': tiempo_total / total_sesiones_abc if total_sesiones_abc > 0 else 0
}
```

#### 2. `AdminController.get_admin_stats()`
**Ubicación**: `app/controllers/admin_controller.py` líneas 304-393

**Antes**:
```python
abecedario_count = Abecedario.query.count()  # ❌ Cuenta todas las palabras
```

**Ahora**:
```python
# Contar sesiones únicas (combinación de user_id + fecha_juego)
abecedario_query = db.session.query(
    Abecedario.user_id,
    Abecedario.fecha_juego
).distinct().all()
abecedario_count = len(abecedario_query)  # ✅ Sesiones únicas
```

**Para sesiones de hoy**:
```python
# Antes
count_today(Abecedario, Abecedario.created_at)  # ❌

# Ahora
abecedario_today = db.session.query(
    Abecedario.user_id
).filter(
    Abecedario.fecha_juego == today
).distinct().count()  # ✅
```

**Para historial de 7 días**:
```python
# Ahora cuenta sesiones únicas por día
abecedario_day = db.session.query(
    Abecedario.user_id
).filter(
    Abecedario.fecha_juego == day
).distinct().count()
```

## Resultados

### Dashboard ahora muestra correctamente:

| Métrica | Descripción |
|---------|-------------|
| **Total Sesiones** | Número de días que el usuario jugó Abecedario |
| **Palabras Completadas** | Total de palabras que completó exitosamente |
| **Tiempo Promedio** | Tiempo promedio por sesión de juego (por día) |

### Ejemplo Real:

**Escenario**: Usuario jugó 5 palabras el día 2026-01-18

**Dashboard muestra**:
```
Abecedario
TOTAL SESIONES: 1
COMPLETADAS: 5
TIEMPO PROMEDIO: 19.5s
```

✅ **Correcto**: 1 sesión (un día de juego) con 5 palabras completadas

## Comparación con Otros Juegos

Ahora todos los juegos son consistentes:

| Juego | Una Sesión = |
|-------|--------------|
| **Memory** | Una partida completa con N parejas |
| **Paseo** | Una partida completa (victoria/derrota) |
| **Train** | Una partida completa de enrutamiento |
| **Abecedario** | ✅ Un día de juego (todas las palabras del día) |

## Archivos Modificados

1. ✅ `app/controllers/admin_controller.py`
   - Método `get_user_stats_all_games()` - Agrupa por día
   - Método `get_admin_stats()` - Cuenta sesiones únicas (user + día)

## Testing

Para verificar que funciona correctamente:

1. **Jugar varias palabras en un día**:
   - Jugar 5 palabras de Abecedario
   - Verificar que dashboard muestra 1 sesión

2. **Jugar en días diferentes**:
   - Jugar 3 palabras en 2026-01-18
   - Jugar 5 palabras en 2026-01-19
   - Verificar que dashboard muestra 2 sesiones

3. **Múltiples usuarios**:
   - Usuario A: 5 palabras en 2026-01-18
   - Usuario B: 3 palabras en 2026-01-18
   - Stats globales deben mostrar 2 sesiones totales

## Notas Técnicas

- La agrupación usa `fecha_juego` (date) no `created_at` (datetime)
- Es consistente con la lógica de reseteo diario del juego
- No afecta el modelo de datos (no requiere migraciones)
- Solo cambia cómo se agregan/cuentan los datos en el dashboard
