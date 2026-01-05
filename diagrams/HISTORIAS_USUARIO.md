# 📋 Índice de Historias de Usuario y Diagramas de Secuencia

Este documento mapea cada historia de usuario con su respectivo diagrama de secuencia.

---

## 🎯 HU1: Selección de Minijuego

**Archivo:** `HU1_seleccion_minijuego.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Adulto mayor |
| **Funcionalidad** | Quiero seleccionar de manera sencilla uno de los minijuegos para iniciar la sesión de actividad cognitiva sin dificultad. |
| **Resultado Esperado** | El usuario inicia la actividad cognitiva deseada sin confusión. |

**Componentes principales:**
- Usuario (Actor)
- Menú Principal (Unity 3D)
- Minijuego Seleccionado

---

## 📊 HU2: Registro de Desempeño

**Archivo:** `HU2_registro_desempeno.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Sistema |
| **Funcionalidad** | Quiero registrar aciertos, errores y tiempos de respuesta para disponer de métricas que permitan evaluar el rendimiento del usuario. |
| **Resultado Esperado** | Se almacenan métricas necesarias para evaluación y ajustes. |

**Componentes principales:**
- Minijuego
- Registro de Métricas (RegistroDesempeno)
- Almacenamiento Local

**Métricas capturadas:**
- ✓ Aciertos totales
- ✓ Errores totales
- ✓ Tiempos de respuesta
- ✓ Pistas utilizadas
- ✓ Estado de completitud

---

## 🧠 HU3: Ajuste Adaptativo mediante IA

**Archivo:** `HU3_ajuste_adaptativo_ia.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Terapeuta |
| **Funcionalidad** | Quiero que el sistema utilice IA para analizar el desempeño del usuario para ajustar automáticamente la dificultad de la siguiente sesión. |
| **Resultado Esperado** | La dificultad se adapta de forma personalizada al usuario. |

**Componentes principales:**
- Terapeuta (Actor)
- Integración API (IntegracionAPI)
- API de IA Externa
- Gestor de Dificultad (AjusteDificultad)

**Análisis de IA incluye:**
- Tasa de aciertos
- Tiempo promedio
- Errores frecuentes
- Progresión temporal

---

## ⚡ HU4: Dificultad Dinámica

**Archivo:** `HU4_dificultad_dinamica.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Adulto mayor |
| **Funcionalidad** | Quiero que la dificultad aumente o disminuya según mi rendimiento para mantenerme motivado sin frustrarme. |
| **Resultado Esperado** | El usuario experimenta una sesión equilibrada y adecuada a su capacidad. |

**Componentes principales:**
- Usuario (Actor)
- Minijuego
- Gestor de Sesión (ControlSesion)
- Gestor de Dificultad (AjusteDificultad)

**Escenarios de adaptación:**
- **Rendimiento ALTO** → Aumentar complejidad
- **Rendimiento BAJO** → Disminuir complejidad
- **Rendimiento NORMAL** → Mantener nivel actual

---

## 🎨 HU5: Interfaz Accesible

**Archivo:** `HU5_interfaz_accesible.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Adulto mayor |
| **Funcionalidad** | Quiero interactuar con una interfaz clara, con botones grandes y texto legible para navegar sin confusión. |
| **Resultado Esperado** | El usuario usa la aplicación de forma intuitiva y sin errores por diseño. |

**Componentes principales:**
- Usuario (Actor)
- Interfaz Unity (Menú/Minijuego)

**Características de accesibilidad:**
- ✓ Tamaño de fuente: ≥32pt
- ✓ Botones: ≥100x100px
- ✓ Contraste: WCAG AAA
- ✓ Sin elementos confusos
- ✓ Retroalimentación visual clara
- ✓ Instrucciones claras

---

## 📈 HU6: Historial de Progreso

**Archivo:** `HU6_historial_progreso.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Terapeuta |
| **Funcionalidad** | Quiero acceder al registro básico del desempeño del usuario para evaluar su evolución cognitiva. |
| **Resultado Esperado** | Se obtiene un historial que facilita el análisis del progreso. |

**Componentes principales:**
- Terapeuta (Actor)
- Sistema de Consulta
- Historial de Desempeño
- Visualizador de Datos

**Datos disponibles:**
- Fechas de sesiones
- Aciertos y errores por sesión
- Tiempos de respuesta
- Niveles alcanzados
- Tendencias de progreso

---

## ⚙️ HU7: Configuración Específica por Juego

**Archivo:** `HU7_configuracion_especifica.puml`

| Campo | Descripción |
|-------|-------------|
| **Rol** | Sistema |
| **Funcionalidad** | Quiero ajustar automáticamente los parámetros del minijuego según la respuesta de la IA para ofrecer una experiencia personalizada. |
| **Resultado Esperado** | Cada sesión inicia con configuraciones adaptadas al usuario. |

**Componentes principales:**
- API de IA
- Gestor de Dificultad (AjusteDificultad)
- Minijuego Específico

**Configuraciones por minijuego:**

### 🔤 Adivinar Palabra:
- Longitud de palabra
- Letras distractoras
- Pistas disponibles

### 🚂 Tren de Colores:
- Velocidad del tren
- Cantidad de colores
- Tiempo de respuesta

### 🃏 Memoria con Cartas:
- Cantidad de pares
- Tiempo de visualización
- Complejidad visual

### 🔍 Búsqueda de Objetos:
- Cantidad de objetos
- Complejidad de escena
- Tiempo límite

---

## 🔗 Relación entre Historias de Usuario

### Flujo Principal de Usuario:
```
HU1 (Selección) → HU5 (Interfaz Accesible) → HU2 (Registro) → 
HU4 (Dificultad Dinámica) → HU7 (Configuración Específica)
```

### Flujo de Análisis (Terapeuta):
```
HU2 (Registro) → HU6 (Historial) → HU3 (Ajuste IA)
```

### Flujo de Adaptación (Sistema):
```
HU2 (Registro) → HU3 (Ajuste IA) → HU7 (Configuración) → HU4 (Dificultad Dinámica)
```

---

## 📊 Resumen de Actores

| Actor | Historias de Usuario |
|-------|---------------------|
| **Adulto Mayor** | HU1, HU4, HU5 |
| **Terapeuta** | HU3, HU6 |
| **Sistema** | HU2, HU7 |

---

## 🎯 Componentes más Utilizados

1. **Gestor de Dificultad** - Aparece en HU3, HU4, HU7
2. **Registro de Métricas** - Aparece en HU2, relacionado con HU3, HU6
3. **Minijuego** - Aparece en HU1, HU2, HU4, HU7
4. **API de IA** - Aparece en HU3, HU7

---

## 📝 Notas para Desarrollo

- Los diagramas están diseñados para ser **concisos y enfocados**
- Cada diagrama muestra solo los componentes relevantes para esa HU
- Se incluyen notas con especificaciones técnicas cuando es necesario
- Los diagramas utilizan fragmentos `alt` para mostrar diferentes escenarios
- Todos los diagramas están en formato PlantUML editable

---

**Fecha de creación:** Diciembre 2025  
**Versión:** 1.0
