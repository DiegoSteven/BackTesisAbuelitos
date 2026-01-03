# 🏗️ Arquitectura General del Sistema - Juegos Cognitivos para Adultos Mayores

## 📋 Resumen Ejecutivo

Sistema de 4 juegos cognitivos desarrollado con arquitectura en 3 capas:
- **Frontend**: Unity (C#) - Juegos interactivos
- **Backend**: Python/Flask - API REST
- **Base de Datos**: SQLite/PostgreSQL

---

## 🎮 Capa 1: Frontend - Unity (C#)

### Game Manager Principal
Controlador central que gestiona:
- Navegación entre juegos
- Estado de sesión del usuario
- Comunicación con Backend API
- Gestión de UI global

### Módulos de Juegos

#### 🚶 Juego 1: Paseo Virtual (Memoria)
- **Objetivo**: Entrenamiento de memoria espacial
- **Mecánica**: Navegación por escenarios, recordar elementos visitados
- **Endpoint**: `/api/paseo`
- **Estado**: ✅ Implementado

#### 🔤 Juego 2: Adivinar la Palabra (Razonamiento)
- **Objetivo**: Razonamiento verbal y vocabulario
- **Mecánica**: Pistas y letras incompletas para descubrir palabras
- **Endpoint**: `/api/palabra`
- **Estado**: 🔄 En desarrollo

#### 🎨 Juego 3: Tren de Colores (Atención)
- **Objetivo**: Atención y concentración
- **Mecánica**: Identificar y seleccionar colores en orden específico
- **Endpoint**: `/api/colores`
- **Estado**: 📋 Pendiente

#### 🔍 Juego 4: Recolección de Objetos (Percepción Visual)
- **Objetivo**: Percepción y atención visual
- **Mecánica**: Localizar elementos específicos en el entorno
- **Endpoint**: `/api/objetos`
- **Estado**: 📋 Pendiente

### Componentes de Comunicación

#### HTTP Client (UnityWebRequest)
- Manejo de peticiones HTTP/HTTPS
- Serialización/Deserialización JSON
- Gestión de tokens JWT
- Manejo de errores y timeout

#### UI Manager
- Interfaz de usuario unificada
- Feedback visual
- Menús y navegación
- Estadísticas y progreso

---

## 🖥️ Capa 2: Backend API - Python/Flask

### API Gateway (`app.py`)
- Punto de entrada único
- Configuración CORS
- Middleware de autenticación
- Documentación Swagger
- Manejo de errores global

### Controllers (Capa de Presentación)

| Controller | Ruta Base | Responsabilidad |
|------------|-----------|-----------------|
| `user_controller.py` | `/api/users` | Autenticación, registro, perfil |
| `paseo_controller.py` | `/api/paseo` | Gestión Juego 1 |
| `palabra_controller.py` | `/api/palabra` | Gestión Juego 2 |
| `colores_controller.py` | `/api/colores` | Gestión Juego 3 |
| `objetos_controller.py` | `/api/objetos` | Gestión Juego 4 |

### Services (Capa de Lógica de Negocio)

| Service | Funciones Principales |
|---------|----------------------|
| `user_service.py` | Validación, encriptación, generación JWT |
| `paseo_service.py` | Lógica del juego, cálculo de puntajes |
| `palabra_service.py` | Selección de palabras, validación de respuestas |
| `colores_service.py` | Generación de secuencias, validación |
| `objetos_service.py` | Generación de escenarios, detección de objetos |

### Models (Capa de Datos - ORM)

```
📦 models/
├── user.py              # Usuario, roles, permisos
├── paseo.py            # Sesiones, niveles, progreso
├── palabra.py          # Palabras, categorías, pistas
├── colores.py          # Secuencias, patrones
└── objetos.py          # Escenarios, objetos, posiciones
```

### Autenticación JWT
- Token Bearer en headers
- Expiración configurable
- Refresh tokens
- Validación en cada request protegido

---

## 💾 Capa 3: Base de Datos

### Esquema de Tablas

#### 👤 Tabla: usuarios
```sql
- id (PK)
- username
- email
- password_hash
- created_at
- last_login
- role
```

#### 📊 Tabla: progreso
```sql
- id (PK)
- user_id (FK)
- juego_tipo
- nivel_actual
- puntaje_total
- tiempo_jugado
- ultima_sesion
```

#### 🎮 Tablas de Sesiones de Juegos

**sesiones_paseo**
```sql
- id (PK)
- user_id (FK)
- nivel
- tiempo_completado
- movimientos
- elementos_recordados
- fecha_sesion
```

**sesiones_palabra**
```sql
- id (PK)
- user_id (FK)
- palabra_id (FK)
- intentos
- tiempo_resolucion
- pistas_usadas
- completado
- fecha_sesion
```

**sesiones_colores**
```sql
- id (PK)
- user_id (FK)
- secuencia_longitud
- intentos
- tiempo_completado
- errores
- fecha_sesion
```

**sesiones_objetos**
```sql
- id (PK)
- user_id (FK)
- escenario_id
- objetos_encontrados
- tiempo_total
- precision
- fecha_sesion
```

---

## 🔄 Flujo de Datos

### 1. Inicio de Sesión
```
Unity → HTTP Client → /api/users/login → Backend
Backend → Validar credenciales → Generar JWT
Backend → Unity (JWT Token)
Unity → Guardar token en memoria
```

### 2. Iniciar Juego
```
Unity → HTTP Client + JWT → /api/{juego}/start → Backend
Backend → Validar token → Crear sesión
Backend → Generar nivel/configuración
Backend → Unity (Datos del nivel)
Unity → Renderizar juego
```

### 3. Enviar Resultado
```
Unity → Calcular métricas → HTTP Client + JWT
HTTP Client → /api/{juego}/result → Backend
Backend → Validar → Service (calcular puntaje)
Service → Model → Guardar en BD
Backend → Unity (Confirmación + estadísticas)
Unity → Mostrar feedback
```

---

## 📡 Endpoints API REST

### Autenticación
- `POST /api/users/register` - Registro de usuario
- `POST /api/users/login` - Inicio de sesión
- `GET /api/users/profile` - Obtener perfil (JWT required)
- `PUT /api/users/profile` - Actualizar perfil (JWT required)

### Juego 1: Paseo Virtual
- `POST /api/paseo/start` - Iniciar nivel
- `POST /api/paseo/result` - Guardar resultado
- `GET /api/paseo/progress` - Obtener progreso
- `GET /api/paseo/history` - Historial de sesiones

### Juego 2: Adivinar la Palabra
- `POST /api/palabra/start` - Obtener palabra
- `POST /api/palabra/validate` - Validar respuesta
- `POST /api/palabra/hint` - Solicitar pista
- `GET /api/palabra/progress` - Obtener progreso

### Juego 3: Tren de Colores
- `POST /api/colores/start` - Iniciar nivel
- `POST /api/colores/validate` - Validar secuencia
- `POST /api/colores/result` - Guardar resultado
- `GET /api/colores/progress` - Obtener progreso

### Juego 4: Recolección de Objetos
- `POST /api/objetos/start` - Iniciar escenario
- `POST /api/objetos/found` - Reportar objeto encontrado
- `POST /api/objetos/result` - Finalizar y guardar
- `GET /api/objetos/progress` - Obtener progreso

### Estadísticas Globales
- `GET /api/stats/overall` - Estadísticas generales
- `GET /api/stats/game/{tipo}` - Estadísticas por juego
- `GET /api/stats/progress` - Progreso en todos los juegos

---

## 🔐 Seguridad

### Implementación
1. **Autenticación**: JWT con expiración de 24h
2. **Encriptación**: bcrypt para passwords
3. **CORS**: Configurado para dominios específicos
4. **Validación**: Schema validation en todos los endpoints
5. **Rate Limiting**: Prevención de abuso de API
6. **HTTPS**: En producción (obligatorio)

---

## 🚀 Tecnologías

### Frontend
- **Motor**: Unity 2021.3+ LTS
- **Lenguaje**: C#
- **Networking**: UnityWebRequest
- **JSON**: Newtonsoft.Json / Unity JsonUtility

### Backend
- **Framework**: Flask 2.3+
- **ORM**: SQLAlchemy
- **Auth**: PyJWT
- **Validación**: Marshmallow
- **Docs**: Swagger/OpenAPI

### Base de Datos
- **Desarrollo**: SQLite
- **Producción**: PostgreSQL (recomendado)

### DevOps
- **Containerización**: Docker
- **Orquestación**: Docker Compose
- **CI/CD**: GitHub Actions (opcional)

---

## 📊 Diagrama ASCII Simplificado

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND - UNITY (C#)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             Game Manager Principal                   │   │
│  └──────────────┬──────────────────────────────────────┘   │
│                 │                                            │
│  ┌──────────────┼────────────────────────────────────┐     │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌──────────┐      │     │
│  │  │Paseo  │ │Palabra│ │Colores│ │ Objetos  │      │     │
│  │  │Virtual│ │ (Raz) │ │(Aten) │ │(Percep)  │      │     │
│  │  └───┬───┘ └───┬───┘ └───┬───┘ └────┬─────┘      │     │
│  └──────┼─────────┼─────────┼──────────┼────────────┘     │
│         └─────────┴─────────┴──────────┘                   │
│                      │                                       │
│               ┌──────▼──────┐                               │
│               │ HTTP Client │                               │
│               │   + JWT     │                               │
│               └──────┬──────┘                               │
└───────────────────────┼──────────────────────────────────────┘
                        │ REST API (JSON)
                        │
┌───────────────────────▼──────────────────────────────────────┐
│              BACKEND - PYTHON/FLASK API                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │              API Gateway (app.py)      ◄──► JWT    │     │
│  └──┬────────┬─────────┬────────┬──────────┬─────────┘     │
│     │        │         │        │          │                │
│  ┌──▼───┐ ┌─▼───┐ ┌───▼──┐ ┌──▼────┐ ┌───▼────┐          │
│  │User  │ │Paseo│ │Palabra│ │Colores│ │Objetos │ CONTROLLERS│
│  │Ctrl  │ │Ctrl │ │Ctrl   │ │Ctrl   │ │Ctrl    │          │
│  └──┬───┘ └─┬───┘ └───┬──┘ └──┬────┘ └───┬────┘          │
│     │       │         │       │          │                │
│  ┌──▼───┐ ┌─▼───┐ ┌───▼──┐ ┌──▼────┐ ┌───▼────┐          │
│  │User  │ │Paseo│ │Palabra│ │Colores│ │Objetos │ SERVICES │
│  │Svc   │ │Svc  │ │Svc    │ │Svc    │ │Svc     │          │
│  └──┬───┘ └─┬───┘ └───┬──┘ └──┬────┘ └───┬────┘          │
│     │       │         │       │          │                │
│  └──▼───┘ ┌─▼───┐ ┌───▼──┐ ┌──▼────┐ ┌───▼────┐          │
│  │User  │ │Paseo│ │Palabra│ │Colores│ │Objetos │ MODELS   │
│  │Model │ │Model│ │Model  │ │Model  │ │Model   │ (ORM)    │
│  └──┬───┘ └─┬───┘ └───┬──┘ └──┬────┘ └───┬────┘          │
└─────┼───────┼─────────┼───────┼──────────┼────────────────┘
      │       │         │       │          │
┌─────▼───────▼─────────▼───────▼──────────▼────────────────┐
│         BASE DE DATOS - SQLite/PostgreSQL                   │
│  ┌──────────┐ ┌─────────────┐ ┌──────────────┐            │
│  │ usuarios │ │   progreso  │ │ sesiones_*   │            │
│  └──────────┘ └─────────────┘ └──────────────┘            │
│  (paseo, palabra, colores, objetos)                        │
└────────────────────────────────────────────────────────────┘
```

---

## 📈 Escalabilidad Futura

### Mejoras Propuestas
1. **Microservicios**: Separar cada juego en su propio servicio
2. **Cache**: Redis para sesiones y datos frecuentes
3. **CDN**: Para assets estáticos de Unity
4. **Load Balancer**: Para distribución de carga
5. **Analytics**: Integración con sistema de métricas
6. **Machine Learning**: Adaptación de dificultad basada en desempeño

---

## 📞 Contacto y Documentación

- **Código PlantUML**: `DiagramaArquitectura.puml`
- **API Docs**: `API_EXAMPLES.md`
- **Swagger**: http://localhost:5000/swagger

---

_Documento actualizado: 2025-12-09_
