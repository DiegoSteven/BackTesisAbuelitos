# 🎯 Diagramas de Casos de Uso - Guía Completa

Esta guía explica los diagramas de casos de uso del Sistema de Juegos Cognitivos.

---

## 📊 Diagramas Disponibles

### 1. **Diagrama Completo** (`casos_de_uso_completo.puml`)
Muestra todos los actores, casos de uso y sus relaciones en un solo diagrama integrado.

**Actores:**
- 👤 **Adulto Mayor**: Usuario final del sistema
- 👨‍⚕️ **Terapeuta**: Profesional que supervisa el progreso
- 🤖 **Sistema IA**: Componente automático de adaptación

**Casos de Uso Principales:**
- Seleccionar Minijuego
- Jugar Sesión
- Interactuar con Interfaz Accesible
- Recibir Dificultad Adaptada
- Registrar Desempeño
- Ajustar Dificultad con IA
- Configurar Parámetros por Juego
- Consultar Historial de Progreso
- Analizar Evolución

---

### 2. **Diagrama del Adulto Mayor** (`casos_de_uso_adulto_mayor.puml`)
Enfocado en la experiencia del usuario final.

**Historias de Usuario Relacionadas:**
- **HU1**: Selección de Minijuego
- **HU4**: Dificultad Dinámica
- **HU5**: Interfaz Accesible

**Flujo Principal:**
```
1. Usuario selecciona minijuego
2. Juega sesión cognitiva (con interfaz accesible)
3. Sistema captura métricas automáticamente
4. Sistema ajusta dificultad para próxima sesión
5. Usuario recibe feedback y dificultad adaptada
```

**Características de Accesibilidad:**
- ✓ Botones grandes (≥100x100px)
- ✓ Texto legible (≥32pt)
- ✓ Alto contraste (WCAG AAA)
- ✓ Navegación sin confusión

---

### 3. **Diagrama del Terapeuta** (`casos_de_uso_terapeuta.puml`)
Enfocado en el análisis y supervisión profesional.

**Historias de Usuario Relacionadas:**
- **HU3**: Ajuste Adaptativo mediante IA
- **HU6**: Historial de Progreso

**Casos de Uso:**
- **Consultar Historial de Usuario**: Acceder a registros de sesiones
- **Analizar Progreso Cognitivo**: Evaluar evolución temporal
- **Visualizar Estadísticas**: Ver métricas consolidadas
- **Revisar Ajustes de IA**: Supervisar adaptación automática
- **Generar Reportes**: Crear documentos de seguimiento

**Datos Disponibles:**
- Sesiones jugadas por fecha
- Métricas por sesión (aciertos, errores, tiempos)
- Tendencias de mejora o deterioro
- Niveles de dificultad alcanzados
- Efectividad de la adaptación

---

### 4. **Diagrama del Sistema** (`casos_de_uso_sistema.puml`)
Enfocado en procesos automáticos e inteligencia artificial.

**Historias de Usuario Relacionadas:**
- **HU2**: Registro de Desempeño
- **HU3**: Ajuste Adaptativo mediante IA (procesamiento)
- **HU7**: Configuración Específica por Juego

**Casos de Uso Automáticos:**
- **Registrar Desempeño**: Captura automática de métricas
- **Capturar Métricas**: Tiempo, aciertos, errores, pistas
- **Almacenar Historial**: Persistencia en almacenamiento local
- **Analizar con Modelo IA**: Procesamiento inteligente
- **Ajustar Dificultad**: Cálculo de nuevos parámetros
- **Configurar Juego Específico**: Adaptación por tipo de minijuego

**Configuraciones Específicas por Juego:**

#### 🔤 Adivinar Palabra:
- Longitud de palabra (3-7 letras)
- Cantidad de letras distractoras (0-2)
- Pistas disponibles (0-2)

#### 🚂 Tren de Colores:
- Velocidad del tren (lento/medio/rápido)
- Cantidad de colores (3-8)
- Tiempo de respuesta (3-10 segundos)

#### 🃏 Memoria con Cartas:
- Cantidad de pares (4-12)
- Tiempo de visualización (1-5 segundos)
- Complejidad visual (simple/media/alta)

#### 🔍 Búsqueda de Objetos:
- Cantidad de objetos (3-10)
- Complejidad de escena (baja/media/alta)
- Tiempo límite (30-180 segundos)

---

## 🔗 Relaciones entre Casos de Uso

### Tipos de Relaciones UML:

#### `<<include>>` (Inclusión)
El caso de uso **siempre** incluye otro caso de uso.

**Ejemplos:**
- "Jugar Sesión" **incluye** "Capturar Métricas"
- "Seleccionar Minijuego" **incluye** "Interfaz Accesible"
- "Registrar Desempeño" **incluye** "Almacenar Datos"

#### `<<extend>>` (Extensión)
El caso de uso **opcionalmente** extiende otro caso de uso.

**Ejemplos:**
- "Registrar Desempeño" **puede extenderse** con "Procesar con IA"
- "Analizar Progreso" **puede extenderse** con "Comparar Desempeño Temporal"
- "Configurar Dificultad" **puede extenderse** con "Supervisión Manual"

#### `<<trigger>>` (Disparador)
Un caso de uso dispara o inicia otro caso de uso.

**Ejemplos:**
- Usuario jugando **dispara** "Capturar Métricas"
- "Almacenar Datos" **dispara** "Analizar con IA"
- "Ajustar Dificultad" **dispara** "Configurar Juego"

---

## 👥 Actores del Sistema

### 👤 Adulto Mayor
**Rol:** Usuario final del sistema  
**Objetivos:**
- Ejercitar capacidades cognitivas
- Usar interfaz fácil e intuitiva
- Recibir retos adecuados a su nivel

**Casos de Uso:**
- Seleccionar Minijuego
- Jugar Sesión
- Interactuar con Interfaz Accesible
- Recibir Dificultad Adaptada
- Visualizar Resultados

---

### 👨‍⚕️ Terapeuta
**Rol:** Profesional de salud cognitiva  
**Objetivos:**
- Monitorear progreso de pacientes
- Identificar áreas de mejora o deterioro
- Validar efectividad del sistema

**Casos de Uso:**
- Consultar Historial
- Analizar Progreso Cognitivo
- Visualizar Estadísticas
- Revisar Ajustes de IA
- Generar Reportes

---

### 🤖 Sistema IA
**Rol:** Componente automático inteligente  
**Objetivos:**
- Adaptar dificultad automáticamente
- Personalizar experiencia
- Registrar métricas precisas

**Casos de Uso:**
- Registrar Desempeño
- Analizar con Modelo IA
- Ajustar Dificultad
- Configurar Parámetros por Juego
- Almacenar Historial

---

## 📈 Flujo General del Sistema

```
┌─────────────────────────────────────────────────────┐
│ 1. ADULTO MAYOR selecciona minijuego               │
│    └─> Con interfaz accesible (HU5)                │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 2. ADULTO MAYOR juega sesión                       │
│    └─> SISTEMA registra métricas (HU2)            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 3. SISTEMA almacena datos                          │
│    └─> Historial disponible para terapeuta (HU6)  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 4. SISTEMA IA analiza desempeño                    │
│    └─> Ajuste adaptativo (HU3)                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 5. SISTEMA configura próxima sesión               │
│    └─> Parámetros específicos por juego (HU7)     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 6. ADULTO MAYOR recibe dificultad adaptada        │
│    └─> Dificultad dinámica (HU4)                   │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Matriz de Trazabilidad

| Historia de Usuario | Actor | Caso de Uso | Diagrama |
|---------------------|-------|-------------|----------|
| HU1 | Adulto Mayor | Seleccionar Minijuego | Completo, Adulto Mayor |
| HU2 | Sistema | Registrar Desempeño | Completo, Sistema |
| HU3 | Terapeuta/Sistema | Ajustar Dificultad con IA | Completo, Terapeuta, Sistema |
| HU4 | Adulto Mayor | Recibir Dificultad Adaptada | Completo, Adulto Mayor |
| HU5 | Adulto Mayor | Interactuar con Interfaz Accesible | Completo, Adulto Mayor |
| HU6 | Terapeuta | Consultar Historial | Completo, Terapeuta |
| HU7 | Sistema | Configurar Parámetros por Juego | Completo, Sistema |

---

## 🎨 Convenciones Visuales

### Actores
- 👤 **Stick figure azul**: Actores humanos
- 🤖 **Stick figure gris**: Sistema automático

### Casos de Uso
- **Elipses**: Representan acciones o funcionalidades

### Relaciones
- **Línea sólida →**: Asociación actor-caso de uso
- **Línea punteada ..>**: Relaciones include/extend/trigger
- **`<<include>>`**: Siempre se ejecuta
- **`<<extend>>`**: Opcionalmente se ejecuta
- **`<<trigger>>`**: Dispara automáticamente

---

**Fecha de creación:** Diciembre 2025  
**Versión:** 1.0  
**Autor:** Sistema de Documentación
