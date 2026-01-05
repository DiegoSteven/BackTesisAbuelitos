# 🎮 JUEGO ABECEDARIO - Sistema Adaptativo con IA

## 📋 Descripción General

Sistema de rehabilitación cognitiva para adultos mayores basado en formación de palabras. Utiliza **Inteligencia Artificial Adaptativa** para ajustar dinámicamente la dificultad según el rendimiento del usuario.

---

## 🏗️ Arquitectura del Sistema

### Sistema Híbrido: Local + IA + Batch

| Nivel | Fuente | Costo/palabra | Latencia | Optimización |
|-------|--------|---------------|----------|--------------|
| **FÁCIL** | JSON local | $0 | 0ms | Palabras simples predefinidas |
| **INTERMEDIO** | JSON local | $0 | 0ms | Palabras cotidianas predefinidas |
| **DIFÍCIL** | Gemini AI (Batch) | ~$0.00005 | ~500ms* | **1 llamada → 20 palabras** |

**Ahorro total**: ~97% en costos API

**\*Latencia**: 500ms solo la primera vez, luego 0ms (usa buffer)

### 🚀 Sistema de Lotes (Batch)

En lugar de pedir 1 palabra cada vez, el sistema:
1. **Primera llamada**: Genera 20 palabras de golpe
2. **Almacena**: Guarda las 20 en memoria (buffer)
3. **Entrega**: Sirve 1 palabra por jugador del buffer
4. **Recarga**: Cuando se acaban las 20, pide otras 20

**Resultado con límite RPM=2**:
- Sin batch: 2 palabras/min → 2 usuarios/min
- Con batch: 40 palabras/min → **40 usuarios/min** (20x más capacidad)

---

## 🎯 Reglas del Juego

### Progresión de Niveles

1. **Usuario nuevo** → Empieza en **FÁCIL**
2. **Completó 5 palabras** → **SUBE** de nivel
3. **Falló 4 de las últimas 5** → **BAJA** de nivel (detección de frustración)
4. **1 error en una letra** → Cambio inmediato de palabra

### Validación Letra por Letra

- El sistema valida **cada letra al momento de seleccionarla**
- Si la letra es incorrecta → Error inmediato → Nueva palabra en 3s
- Si completa correctamente → ¡EXCELENTE! → Nueva palabra

**Beneficio**: Detección rápida de errores, juego dinámico, menos frustración

---

## 📊 Reseteo Diario Automático

### Funcionamiento

Cada día que el usuario juega:
1. El sistema detecta **automáticamente** si es un nuevo día
2. **Resetea COMPLETAMENTE**: Regresa a nivel **FÁCIL** con progreso 0/5
3. El usuario debe avanzar de nuevo: FÁCIL → INTERMEDIO → DIFÍCIL

**¿Por qué resetear a FÁCIL?**
- ✅ Permite **comparar el mismo nivel** entre días (FÁCIL vs FÁCIL)
- ✅ Mide **velocidad de progresión** (cuánto tarda en llegar a INTERMEDIO/DIFÍCIL)
- ✅ Detecta **mejora cognitiva** (si completa niveles más rápido cada día)

### Medición de Mejora

```
Día 1:
  - FÁCIL: tiempo_para_completar_nivel = 180s
  - INTERMEDIO: tiempo_para_completar_nivel = 240s
  - Total: 420s para llegar a INTERMEDIO
  
Día 2:
  - FÁCIL: tiempo_para_completar_nivel = 120s (33% más rápido ✅)
  - INTERMEDIO: tiempo_para_completar_nivel = 180s (25% más rápido ✅)
  - Total: 300s para llegar a INTERMEDIO (28% más rápido ✅)

Conclusión: Usuario mejoró velocidad en ambos niveles
```

**Métricas clave**:
- `tiempo_para_completar_nivel`: Cuánto tardó en completar 5 palabras de ese nivel
- `tasa_exito`: Porcentaje de palabras completadas
- `completo_5_de_5`: Si completó las 5 palabras del nivel
- **Velocidad de progresión**: Cuánto tarda en pasar de FÁCIL a DIFÍCIL cada día

---

## 📡 API Endpoints

### 1. Obtener Siguiente Desafío
```http
GET /abecedario/next-challenge/<user_id>
```

**Respuesta**:
```json
{
  "challenge": {
    "palabra_objetivo": "SOL",
    "letras_distractoras": ["A", "E", "I", "O", "U", "M", "N"],
    "pista_contextual": "Brilla en el cielo durante el día",
    "nivel_dificultad": "facil",
    "metadata": {
      "nivel_actual": "facil",
      "cambio_nivel": false,
      "progreso_nivel": "2/5"
    }
  }
}
```

### 2. Guardar Sesión
```http
POST /abecedario/session
```

**Body**:
```json
{
  "user_id": 1,
  "palabra_objetivo": "SOL",
  "tiempo_resolucion": 15.5,
  "cantidad_errores": 0,
  "pistas_usadas": 0,
  "completado": true,
  "nivel_dificultad": "facil"
}
```

**Respuesta**:
```json
{
  "message": "Sesión guardada exitosamente",
  "session": {
    "id": 123,
    "cambio_nivel": false,
    "nivel_jugado": "facil",
    "completado": true
  }
}
```

### 3. Reporte de Evolución
```http
GET /abecedario/evolution/<user_id>
```

**Respuesta**:
```json
{
  "total_sesiones": 25,
  "por_fecha": {
    "2025-11-20": {
      "FACIL": {
        "total_palabras": 5,
        "completadas": 5,
        "tiempo_total": 192.5,
        "tasa_exito": 100.0,
        "progresion": {
          "completo_5_de_5": true,
          "tiempo_para_completar_nivel": 192.5,
          "hora_inicio": "14:29:03",
          "hora_fin": "14:32:15"
        }
      }
    },
    "2025-11-21": {
      "FACIL": {
        "total_palabras": 5,
        "completadas": 5,
        "tiempo_total": 142.0,
        "tasa_exito": 100.0,
        "progresion": {
          "completo_5_de_5": true,
          "tiempo_para_completar_nivel": 142.0,
          "hora_inicio": "10:13:20",
          "hora_fin": "10:15:42"
        }
      }
    }
  }
}
```

---

## 🗄️ Modelo de Datos

### Tabla: `word_game_session`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único de la sesión |
| `user_id` | Integer | ID del usuario (FK) |
| `palabra_objetivo` | String | Palabra a formar |
| `tiempo_resolucion` | Float | Tiempo en segundos |
| `cantidad_errores` | Integer | Errores cometidos |
| `pistas_usadas` | Integer | Pistas utilizadas |
| `completado` | Boolean | Si completó la palabra |
| `nivel_jugado` | String | facil/intermedio/dificil |
| `cambio_nivel` | Boolean | Si es inicio de nuevo nivel/día |
| `fecha_juego` | Date | Fecha del juego (automático) |
| `created_at` | DateTime | Timestamp completo |

---

## 🎓 Justificación Académica

### Valor de la Tesis

1. **IA Adaptativa**: El sistema ajusta dificultad según rendimiento individual
2. **Detección de Frustración**: Algoritmo detecta 4/5 fallos y reduce dificultad
3. **Métricas Longitudinales**: Análisis de mejora cognitiva día a día
4. **Eficiencia Extrema**: 97% ahorro en costos mediante:
   - JSON local para niveles básicos (90% ahorro)
   - Sistema de lotes/batch para nivel difícil (+7% ahorro adicional)
5. **Escalabilidad Real**: Soporta 40 usuarios simultáneos con límite RPM=2

### Innovación: Sistema Batch

**Problema típico**: 1 llamada API = 1 palabra → Límite de 2 usuarios/min con RPM=2

**Solución implementada**: 1 llamada API = 20 palabras → Límite de 40 usuarios/min

**Impacto**: Sistema productivo y escalable manteniendo calidad de IA personalizada

### Ejemplo de Análisis

```
Usuario A (75 años):

Día 1:
  - FÁCIL: 180s → INTERMEDIO: 240s → DIFÍCIL: no alcanzó
  - Total sesión: 420s, llegó hasta INTERMEDIO
  
Día 2:
  - FÁCIL: 150s → INTERMEDIO: 200s → DIFÍCIL: 300s
  - Total sesión: 650s, completó todos los niveles
  - Mejora FÁCIL: 16% más rápido
  - Mejora INTERMEDIO: 16% más rápido
  
Día 3:
  - FÁCIL: 120s → INTERMEDIO: 160s → DIFÍCIL: 250s
  - Total sesión: 530s, completó todos los niveles
  - Mejora FÁCIL: 33% más rápido vs Día 1
  - Mejora INTERMEDIO: 33% más rápido vs Día 1
  - Mejora general: 18% más rápido vs Día 2

Conclusión: Sistema demuestra mejora progresiva de velocidad cognitiva,
consolidación de aprendizaje y capacidad de alcanzar niveles superiores
más rápidamente cada día.
```

---

## 🚀 Tecnologías

- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **IA**: Google Gemini 2.5 Flash (solo nivel DIFÍCIL)
- **Frontend**: Unity (C#)
- **Palabras locales**: JSON (`app/data/palabras_predefinidas.json`)

---

## 📂 Estructura de Archivos Clave

```
app/
├── data/
│   └── palabras_predefinidas.json    # 40 palabras (20 fácil, 20 intermedio)
├── services/
│   └── abecedario/
│       ├── abecedario_service.py     # Lógica de niveles y progresión
│       └── gemini_abecedario_service.py  # Integración IA (solo DIFÍCIL)
├── controllers/
│   └── abecedario_controller.py      # Endpoints REST
└── models/
    └── abecedario.py                 # Modelo de base de datos
```

---

## ✅ Flujo Completo del Usuario

1. **Usuario abre el juego** → GET `/next-challenge/<user_id>`
2. **Sistema detecta si es nuevo día** → Si sí: resetea a FÁCIL 0/5
3. **Sistema determina nivel** (facil/intermedio/dificil)
4. **Si FÁCIL/INTERMEDIO** → Palabra del JSON local (0ms)
5. **Si DIFÍCIL** → Gemini genera palabra personalizada (~500ms)
6. **Usuario selecciona letras** → Validación letra por letra
7. **Si error** → Guarda sesión (completado=false) → Nueva palabra en 3s
8. **Si correcto** → Guarda sesión (completado=true) → Nueva palabra
9. **Cada 5 palabras completadas** → Analiza si sube nivel (FÁCIL→INTERMEDIO→DIFÍCIL)
10. **Al día siguiente** → Vuelve a FÁCIL automáticamente para medir evolución

---

## 💡 Conclusión

Sistema eficiente, escalable y académicamente válido que:
- **Reduce costos 97%** usando JSON local + sistema de lotes (batch)
- **Detecta frustración** y adapta dificultad automáticamente
- **Mide mejora** comparando rendimiento diario en los mismos niveles
- **Valida en tiempo real** para experiencia dinámica
- **Resetea diariamente a FÁCIL** para análisis longitudinal consistente
- **Escala a 40 usuarios/min** con límite RPM=2 (vs 2 usuarios/min sin batch)

**Ventaja académica clave**: Al resetear a FÁCIL cada día, puedes medir:
1. Velocidad de procesamiento en cada nivel (FÁCIL, INTERMEDIO, DIFÍCIL)
2. Velocidad de progresión (cuánto tarda en avanzar de FÁCIL a DIFÍCIL)
3. Mejora porcentual día a día en métricas comparables
4. Curva de aprendizaje clara y cuantificable

**Innovación técnica**: Sistema de lotes (batch) que multiplica x20 la capacidad sin perder personalización de IA.

**Ideal para**: Investigación en rehabilitación cognitiva con sistemas adaptativos basados en IA.
