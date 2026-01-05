# 🧪 Pruebas de Carga - Backend Gemini API

## 📋 Descripción

Módulo de pruebas para medir la capacidad del backend con la API KEY de Gemini:
- ✅ Cuántos adultos mayores pueden jugar AL MISMO TIEMPO
- ✅ Cuántas sesiones soporta la API por día
- ✅ Tiempos de respuesta bajo carga
- ✅ Pruebas REALES (no simulaciones)

## 🚀 Cómo Usar

### 1️⃣ Iniciar el Backend

```powershell
cd app
python app.py
```

El backend debe estar corriendo en `http://localhost:5000`

### 2️⃣ Ejecutar las Pruebas

En otra terminal:

```powershell
cd tests
python test_load_gemini.py
```

### 3️⃣ Seleccionar Tipo de Prueba

El programa mostrará un menú:

```
1. 🚀 Prueba de concurrencia (usuarios simultáneos)
2. 📈 Prueba de límite diario (sesiones consecutivas)
3. 🔥 Prueba de estrés completa (ambas)
4. ❌ Salir
```

## 📊 Tipos de Pruebas

### 🚀 Prueba de Concurrencia

Simula N usuarios jugando al mismo tiempo:
- Crea usuarios reales en la base de datos
- Cada usuario juega múltiples sesiones
- Mide tiempos de respuesta bajo carga
- Detecta errores de concurrencia

**Recomendado:** 5-20 usuarios, 3-10 sesiones cada uno

**Ejemplo:**
```
¿Cuántos usuarios simultáneos? 10
¿Cuántas sesiones por usuario? 5
```
Esto creará 10 usuarios y cada uno jugará 5 sesiones en paralelo (50 sesiones totales).

### 📈 Prueba de Límite Diario

Ejecuta sesiones consecutivas para medir el límite de la API KEY:
- Un solo usuario juega muchas sesiones seguidas
- Detecta cuando se alcanza el rate limit
- Mide cuántas peticiones soporta por día

**Recomendado:** 50-200 sesiones

**Ejemplo:**
```
¿Cuántas sesiones consecutivas? 100
```

### 🔥 Prueba de Estrés Completa

Ejecuta ambas pruebas en secuencia:
1. **Fase 1:** 10 usuarios concurrentes, 5 sesiones cada uno
2. **Fase 2:** 100 sesiones consecutivas

## 📈 Resultados

Los resultados se muestran en consola y se guardan en un archivo JSON:

```
📊 RESULTADOS DE LA PRUEBA
═══════════════════════════════════════════════════════

⏱️  TIEMPO:
  • Inicio:        2026-01-03 14:30:00
  • Fin:           2026-01-03 14:35:23
  • Duración:      323.45 segundos

👥 USUARIOS:
  • Creados:       10

🎮 SESIONES:
  • Total:         50
  • Exitosas:      48 (96.0%)
  • Fallidas:      2 (4.0%)

❌ ERRORES:
  • Concurrencia:  1
  • API KEY:       1

⚡ TIEMPOS DE RESPUESTA:
  • Promedio:      2.34s
  • Mínimo:        1.12s
  • Máximo:        8.45s
  • Mediana:       2.01s

💾 Resultados guardados en: test_results_20260103_143523.json
```

## 🎮 Qué Prueba Cada Sesión

### Abecedario
1. GET `/abecedario/next-challenge/{user_id}` - Usa Gemini para generar palabra
2. POST `/abecedario/session` - Guarda la sesión jugada

### Paseo
1. POST `/paseo/start-session` - Puede usar Gemini para decidir nivel
2. POST `/paseo/save-session` - Guarda la sesión jugada

## ⚠️ Límites Conocidos de Gemini API

Según la documentación de Google:
- **Free tier:** 15 RPM (requests per minute), 1,500 RPD (requests per day)
- **Paid tier:** Mayor límite según el plan

Las pruebas te ayudarán a identificar estos límites en tu caso específico.

## 📝 Archivo de Resultados (JSON)

Se genera un archivo `test_results_YYYYMMDD_HHMMSS.json` con:
- Usuarios creados
- Sesiones exitosas/fallidas
- Errores por tipo
- Tiempos de respuesta (lista completa)
- Hora de inicio/fin

## 🔧 Requisitos

```bash
pip install requests
```

O instalar todas las dependencias:
```bash
pip install -r requirements.txt
```

## 💡 Consejos

1. **Primera vez:** Empieza con pruebas pequeñas (5 usuarios, 3 sesiones)
2. **Monitoreo:** Observa los logs del backend en paralelo
3. **Base de datos:** Los usuarios de prueba se quedan en la BD, puedes limpiarlos después
4. **Incrementar carga:** Ve aumentando gradualmente para encontrar el límite real

## 🧹 Limpiar Usuarios de Prueba

Después de las pruebas, puedes eliminar los usuarios creados:

```sql
DELETE FROM users WHERE nombre LIKE '%_test_%';
DELETE FROM abecedario_sessions WHERE user_id IN (SELECT id FROM users WHERE nombre LIKE '%_test_%');
DELETE FROM paseo_sessions WHERE user_id IN (SELECT id FROM users WHERE nombre LIKE '%_test_%');
```

O desde Python:
```python
# Agregar al final de test_load_gemini.py si deseas auto-limpieza
def limpiar_usuarios_prueba():
    # Implementar limpieza automática
    pass
```

## 📞 Contacto

Si encuentras algún problema o necesitas ajustar las pruebas, contacta al equipo de desarrollo.

---

**Última actualización:** Enero 2026
