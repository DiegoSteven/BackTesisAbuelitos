# Juego de Paseo Adaptativo - Integración Unity con Backend

## 📋 Resumen del Sistema

El **Juego de Paseo Adaptativo** es un infinite runner con ajuste dinámico de dificultad basado en IA. El sistema funciona en dos fases:

1. **Fase Tutorial (1 minuto)**: Calibración inicial con parámetros fijos
2. **Fase Adaptativa (infinita)**: Ajuste continuo cada 20-30 segundos basado en métricas

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      UNITY (C# Cliente)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ GameManager  │───▶│   Spawner    │───▶│   Esfera     │    │
│  │   Paseo      │    │   Esferas    │    │  Collision   │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│         │                                                      │
│         │ Cada 20-30s                                          │
│         ▼                                                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │         Envío de Métricas a Backend                   │    │
│  │  - Esferas atrapadas (rojas/azules)                   │    │
│  │  - Esferas perdidas                                    │    │
│  │  - Tiempo de reacción promedio                        │    │
│  └──────────────────────────────────────────────────────┘    │
│         │                                                      │
└─────────┼──────────────────────────────────────────────────────┘
          │ HTTP POST
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND (Python)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌───────────────────────┐   │
│  │  paseo_controller.py │────────▶│  paseo_service.py     │   │
│  │  - start-session     │         │  - save_segment()     │   │
│  │  - report-metrics    │         │  - analyze_performance│   │
│  │  - evolution         │         │  - get_evolution()    │   │
│  └──────────────────────┘         └───────────────────────┘   │
│           │                                 │                   │
│           │                                 ▼                   │
│           │                 ┌────────────────────────────┐     │
│           │                 │ gemini_paseo_service.py    │     │
│           │                 │ - analizar_y_ajustar()     │     │
│           │                 └────────────────────────────┘     │
│           │                                 │                   │
│           │                                 ▼                   │
│           │                     ┌───────────────────┐          │
│           │                     │  Google Gemini IA │          │
│           │                     │  gemini-2.0-flash │          │
│           │                     └───────────────────┘          │
│           │                                 │                   │
│           │ ◀───────────────────────────────┘                   │
│           │ Nuevos parámetros                                  │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Respuesta JSON con ajuste:                          │     │
│  │  - velocidad_esferas                                  │     │
│  │  - intervalo_spawn                                    │     │
│  │  - colores_activos                                    │     │
│  │  - nuevo_nivel                                        │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
          │ HTTP Response JSON
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UNITY (Aplicación)                         │
│                                                                 │
│  Aplica nuevos parámetros con Lerp (transición suave):         │
│  - StartCoroutine(AplicarAjusteSuave(nuevoAjuste))             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Endpoints de la API

### Base URL
```
http://localhost:5000/paseo
```

### 1. Iniciar Sesión - `POST /start-session`

**Descripción**: Obtiene la configuración inicial para el usuario. Si es un nuevo día o usuario nuevo, devuelve configuración de Tutorial. Si ya jugó hoy, continúa desde la última configuración.

**Request Body**:
```json
{
  "user_id": 1
}
```

**Response (Tutorial)**:
```json
{
  "success": true,
  "config": {
    "fase": "tutorial",
    "nivel_dificultad": "facil",
    "velocidad_esferas": 8.0,
    "intervalo_spawn": 3.0,
    "colores_activos": "rojo",
    "mensaje": "Iniciando tutorial de calibración"
  }
}
```

**Response (Continuar Adaptativo)**:
```json
{
  "success": true,
  "config": {
    "fase": "adaptativo",
    "nivel_dificultad": "intermedio",
    "velocidad_esferas": 15.0,
    "intervalo_spawn": 2.0,
    "colores_activos": "rojo,azul",
    "mensaje": "Continuando desde última configuración"
  }
}
```

---

### 2. Reportar Métricas - `POST /report-metrics`

**Descripción**: Envía métricas de un segmento de juego (cada 20-30 segundos). El backend analiza el rendimiento y devuelve ajustes si es necesario.

**Request Body**:
```json
{
  "user_id": 1,
  "velocidad_esferas": 10.0,
  "intervalo_spawn": 2.5,
  "colores_activos": "rojo",
  "duracion_segmento": 25.5,
  "esferas_rojas_atrapadas": 8,
  "esferas_azules_atrapadas": 0,
  "esferas_perdidas": 2,
  "tiempo_reaccion_promedio": 1.2,
  "fase": "adaptativo",
  "nivel_dificultad": "facil"
}
```

**Response (Con ajuste)**:
```json
{
  "success": true,
  "segmento_guardado": true,
  "ajuste": {
    "requiere_ajuste": true,
    "nuevo_nivel": "intermedio",
    "velocidad_esferas": 12.0,
    "intervalo_spawn": 2.0,
    "colores_activos": "rojo,azul",
    "razonamiento": "Precisión alta (80%), subiendo a nivel intermedio con distractores"
  }
}
```

**Response (Sin ajuste)**:
```json
{
  "success": true,
  "segmento_guardado": true,
  "ajuste": {
    "requiere_ajuste": false,
    "mensaje": "Rendimiento dentro del rango esperado"
  }
}
```

---

### 3. Obtener Evolución - `GET /evolution/<user_id>`

**Descripción**: Devuelve el reporte de evolución diaria del usuario.

**Response**:
```json
{
  "success": true,
  "total_sesiones": 15,
  "por_fecha": {
    "2024-01-15": {
      "fecha": "2024-01-15",
      "duracion_total": 180.5,
      "precision_promedio": 75.2,
      "total_segmentos": 8,
      "fase_alcanzada": "adaptativo",
      "nivel_maximo": "intermedio",
      "rojas_totales": 45,
      "azules_totales": 5,
      "perdidas_totales": 10
    },
    "2024-01-16": {
      "fecha": "2024-01-16",
      "duracion_total": 220.0,
      "precision_promedio": 82.5,
      "total_segmentos": 10,
      "fase_alcanzada": "adaptativo",
      "nivel_maximo": "dificil",
      "rojas_totales": 60,
      "azules_totales": 3,
      "perdidas_totales": 8
    }
  }
}
```

---

### 4. Probar Ajuste (Testing) - `POST /test-adjustment`

**Descripción**: Endpoint de prueba para probar el sistema de ajuste de IA sin guardar en base de datos.

**Request Body**:
```json
{
  "precision_promedio": 85.5,
  "tiempo_reaccion_promedio": 1.1,
  "perdidas": 3,
  "total_esferas": 20,
  "nivel_actual": "facil",
  "configuracion_actual": {
    "velocidad_esferas": 10.0,
    "intervalo_spawn": 2.5,
    "colores_activos": "rojo"
  }
}
```

**Response**:
```json
{
  "success": true,
  "ajuste": {
    "requiere_ajuste": true,
    "nuevo_nivel": "intermedio",
    "velocidad_esferas": 14.0,
    "intervalo_spawn": 2.0,
    "colores_activos": "rojo,azul",
    "razonamiento": "Precisión excelente (85.5%) y reacción rápida, subiendo a nivel intermedio"
  }
}
```

---

## 🎮 Integración en Unity (C#)

### Estructura de Clases Necesarias

```csharp
using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class StartSessionRequest
{
    public int user_id;
}

[Serializable]
public class StartSessionResponse
{
    public bool success;
    public GameConfig config;
}

[Serializable]
public class GameConfig
{
    public string fase;
    public string nivel_dificultad;
    public float velocidad_esferas;
    public float intervalo_spawn;
    public string colores_activos;
    public string mensaje;
}

[Serializable]
public class ReportMetricsRequest
{
    public int user_id;
    public float velocidad_esferas;
    public float intervalo_spawn;
    public string colores_activos;
    public float duracion_segmento;
    public int esferas_rojas_atrapadas;
    public int esferas_azules_atrapadas;
    public int esferas_perdidas;
    public float tiempo_reaccion_promedio;
    public string fase;
    public string nivel_dificultad;
}

[Serializable]
public class ReportMetricsResponse
{
    public bool success;
    public bool segmento_guardado;
    public AjusteConfig ajuste;
}

[Serializable]
public class AjusteConfig
{
    public bool requiere_ajuste;
    public string nuevo_nivel;
    public float velocidad_esferas;
    public float intervalo_spawn;
    public string colores_activos;
    public string razonamiento;
    public string mensaje;
}
```

---

### Código de Integración en GameManagerPaseo.cs

```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public class GameManagerPaseo : MonoBehaviour
{
    // Configuración
    private const string BASE_URL = "http://localhost:5000/paseo";
    private const float INTERVALO_REPORTE = 25f; // 25 segundos
    
    [Header("Usuario")]
    public int userId = 1;
    
    [Header("Referencias")]
    public SpawnerEsferas spawner;
    
    [Header("Estado del Juego")]
    private GameConfig configuracionActual;
    private string faseActual = "tutorial";
    private string nivelActual = "facil";
    
    [Header("Métricas del Segmento")]
    private float tiempoInicioSegmento;
    private int esferasRojasAtrapadas;
    private int esferasAzulesAtrapadas;
    private int esferasPerdidas;
    private List<float> tiemposReaccion = new List<float>();
    
    private void Start()
    {
        IniciarSesion();
    }
    
    // ===== INICIALIZACIÓN =====
    
    private void IniciarSesion()
    {
        StartCoroutine(StartSessionCoroutine());
    }
    
    private IEnumerator StartSessionCoroutine()
    {
        string url = BASE_URL + "/start-session";
        
        StartSessionRequest request = new StartSessionRequest { user_id = userId };
        string jsonData = JsonUtility.ToJson(request);
        
        using (UnityWebRequest webRequest = UnityWebRequest.Post(url, jsonData, "application/json"))
        {
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                string response = webRequest.downloadHandler.text;
                StartSessionResponse data = JsonUtility.FromJson<StartSessionResponse>(response);
                
                if (data.success)
                {
                    configuracionActual = data.config;
                    faseActual = data.config.fase;
                    nivelActual = data.config.nivel_dificultad;
                    
                    AplicarConfiguracion(data.config);
                    
                    Debug.Log($"[PASEO] Sesión iniciada - Fase: {faseActual}, Nivel: {nivelActual}");
                    Debug.Log($"[PASEO] {data.config.mensaje}");
                    
                    // Iniciar reportes periódicos
                    IniciarReportesPeriodicos();
                }
            }
            else
            {
                Debug.LogError($"[PASEO ERROR] Start Session: {webRequest.error}");
            }
        }
    }
    
    // ===== APLICAR CONFIGURACIÓN =====
    
    private void AplicarConfiguracion(GameConfig config)
    {
        // Aplicar directamente
        spawner.velocidadEsferas = config.velocidad_esferas;
        spawner.intervaloSpawn = config.intervalo_spawn;
        
        // Configurar colores activos
        spawner.soloRojas = (config.colores_activos == "rojo");
        
        Debug.Log($"[PASEO CONFIG] Velocidad: {config.velocidad_esferas}, Intervalo: {config.intervalo_spawn}, Colores: {config.colores_activos}");
    }
    
    private void AplicarConfiguracionSuave(GameConfig config, float duracion = 2f)
    {
        StartCoroutine(AplicarAjusteSuaveCoroutine(config, duracion));
    }
    
    private IEnumerator AplicarAjusteSuaveCoroutine(GameConfig config, float duracion)
    {
        float velocidadInicial = spawner.velocidadEsferas;
        float intervaloInicial = spawner.intervaloSpawn;
        
        float velocidadFinal = config.velocidad_esferas;
        float intervaloFinal = config.intervalo_spawn;
        
        float elapsed = 0f;
        
        while (elapsed < duracion)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duracion;
            
            spawner.velocidadEsferas = Mathf.Lerp(velocidadInicial, velocidadFinal, t);
            spawner.intervaloSpawn = Mathf.Lerp(intervaloInicial, intervaloFinal, t);
            
            yield return null;
        }
        
        // Asegurar valores finales
        spawner.velocidadEsferas = velocidadFinal;
        spawner.intervaloSpawn = intervaloFinal;
        
        // Actualizar colores
        spawner.soloRojas = (config.colores_activos == "rojo");
        
        Debug.Log($"[PASEO] Ajuste suave completado - Velocidad: {velocidadFinal}, Intervalo: {intervaloFinal}");
    }
    
    // ===== REPORTES PERIÓDICOS =====
    
    private void IniciarReportesPeriodicos()
    {
        tiempoInicioSegmento = Time.time;
        ReiniciarMetricas();
        
        InvokeRepeating(nameof(EnviarReporte), INTERVALO_REPORTE, INTERVALO_REPORTE);
    }
    
    private void EnviarReporte()
    {
        StartCoroutine(ReportMetricsCoroutine());
    }
    
    private IEnumerator ReportMetricsCoroutine()
    {
        string url = BASE_URL + "/report-metrics";
        
        float duracionSegmento = Time.time - tiempoInicioSegmento;
        float tiempoReaccionPromedio = CalcularTiempoReaccionPromedio();
        
        ReportMetricsRequest request = new ReportMetricsRequest
        {
            user_id = userId,
            velocidad_esferas = spawner.velocidadEsferas,
            intervalo_spawn = spawner.intervaloSpawn,
            colores_activos = spawner.soloRojas ? "rojo" : "rojo,azul",
            duracion_segmento = duracionSegmento,
            esferas_rojas_atrapadas = esferasRojasAtrapadas,
            esferas_azules_atrapadas = esferasAzulesAtrapadas,
            esferas_perdidas = esferasPerdidas,
            tiempo_reaccion_promedio = tiempoReaccionPromedio,
            fase = faseActual,
            nivel_dificultad = nivelActual
        };
        
        string jsonData = JsonUtility.ToJson(request);
        
        using (UnityWebRequest webRequest = UnityWebRequest.Post(url, jsonData, "application/json"))
        {
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                string response = webRequest.downloadHandler.text;
                ReportMetricsResponse data = JsonUtility.FromJson<ReportMetricsResponse>(response);
                
                if (data.success && data.ajuste.requiere_ajuste)
                {
                    Debug.Log($"[PASEO AJUSTE] {data.ajuste.razonamiento}");
                    Debug.Log($"[PASEO] Nuevo nivel: {data.ajuste.nuevo_nivel}");
                    
                    // Actualizar nivel
                    nivelActual = data.ajuste.nuevo_nivel;
                    
                    // Aplicar nueva configuración con transición suave
                    GameConfig nuevaConfig = new GameConfig
                    {
                        fase = "adaptativo",
                        nivel_dificultad = data.ajuste.nuevo_nivel,
                        velocidad_esferas = data.ajuste.velocidad_esferas,
                        intervalo_spawn = data.ajuste.intervalo_spawn,
                        colores_activos = data.ajuste.colores_activos
                    };
                    
                    AplicarConfiguracionSuave(nuevaConfig, 2f);
                }
                else
                {
                    Debug.Log($"[PASEO] Sin ajustes - {data.ajuste.mensaje}");
                }
                
                // Reiniciar métricas para el siguiente segmento
                tiempoInicioSegmento = Time.time;
                ReiniciarMetricas();
            }
            else
            {
                Debug.LogError($"[PASEO ERROR] Report Metrics: {webRequest.error}");
            }
        }
    }
    
    // ===== MÉTODOS DE MÉTRICAS =====
    
    public void RegistrarEsferaRojaAtrapada(float tiempoReaccion)
    {
        esferasRojasAtrapadas++;
        tiemposReaccion.Add(tiempoReaccion);
    }
    
    public void RegistrarEsferaAzulAtrapada(float tiempoReaccion)
    {
        esferasAzulesAtrapadas++;
        tiemposReaccion.Add(tiempoReaccion);
    }
    
    public void RegistrarEsferaPerdida()
    {
        esferasPerdidas++;
    }
    
    private float CalcularTiempoReaccionPromedio()
    {
        if (tiemposReaccion.Count == 0) return 0f;
        
        float suma = 0f;
        foreach (float tiempo in tiemposReaccion)
        {
            suma += tiempo;
        }
        
        return suma / tiemposReaccion.Count;
    }
    
    private void ReiniciarMetricas()
    {
        esferasRojasAtrapadas = 0;
        esferasAzulesAtrapadas = 0;
        esferasPerdidas = 0;
        tiemposReaccion.Clear();
    }
}
```

---

### Modificaciones en EsferaColision.cs

```csharp
using UnityEngine;

public class EsferaColision : MonoBehaviour
{
    public bool esRoja = true;
    private float tiempoSpawn;
    private GameManagerPaseo gameManager;
    
    private void Start()
    {
        tiempoSpawn = Time.time;
        gameManager = FindObjectOfType<GameManagerPaseo>();
    }
    
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            float tiempoReaccion = Time.time - tiempoSpawn;
            
            if (esRoja)
            {
                // Atrapó correctamente una esfera roja
                gameManager.RegistrarEsferaRojaAtrapada(tiempoReaccion);
                Debug.Log($"[ESFERA] Roja atrapada - Reacción: {tiempoReaccion:F2}s");
            }
            else
            {
                // Error: atrapó una esfera azul (distractor)
                gameManager.RegistrarEsferaAzulAtrapada(tiempoReaccion);
                Debug.Log($"[ESFERA] Azul atrapada (error) - Reacción: {tiempoReaccion:F2}s");
            }
            
            Destroy(gameObject);
        }
        else if (other.CompareTag("DeadZone"))
        {
            if (esRoja)
            {
                // Perdió una esfera roja
                gameManager.RegistrarEsferaPerdida();
                Debug.Log("[ESFERA] Roja perdida");
            }
            
            Destroy(gameObject);
        }
    }
}
```

---

## 🧠 Lógica de Ajuste de IA (Gemini)

### Criterios de Nivel

| Nivel | Velocidad Esferas | Intervalo Spawn | Colores | Descripción |
|-------|-------------------|-----------------|---------|-------------|
| **FACIL** | 8-12 | 2.5-4.0s | Solo rojas | Calibración inicial |
| **INTERMEDIO** | 12-18 | 1.5-2.5s | Rojas + azules | Introduce distractores |
| **DIFICIL** | 18-25 | 0.8-1.5s | Rojas + azules | Máximo desafío |

### Criterios de Cambio de Nivel

**Subir a INTERMEDIO**:
- Precisión > 80% **Y** tasa_perdida < 20% **Y** tiempo_reaccion < 1.5s

**Subir a DIFICIL**:
- Precisión > 75% **Y** tasa_perdida < 25% **Y** tiempo_reaccion < 1.2s

**Bajar a FACIL**:
- Precisión < 50% **O** tasa_perdida > 50%

**Bajar a INTERMEDIO** (desde DIFICIL):
- Precisión < 60% **O** tasa_perdida > 40%

### Ajustes Graduales

Si el nivel **NO cambia**, el sistema ajusta velocidad/intervalo en incrementos pequeños:

- **Rendimiento excelente (>85%)**: Aumentar velocidad +2, reducir intervalo -0.3
- **Rendimiento bueno (70-85%)**: Cambios mínimos o mantener
- **Rendimiento bajo (<60%)**: Reducir velocidad -2, aumentar intervalo +0.3

---

## 📊 Base de Datos

### Tabla `paseo_session`

```sql
CREATE TABLE paseo_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    velocidad_esferas FLOAT NOT NULL,
    intervalo_spawn FLOAT NOT NULL,
    colores_activos VARCHAR(50) NOT NULL,
    duracion_segmento FLOAT NOT NULL,
    esferas_rojas_atrapadas INTEGER DEFAULT 0,
    esferas_azules_atrapadas INTEGER DEFAULT 0,
    esferas_perdidas INTEGER DEFAULT 0,
    precision FLOAT DEFAULT 0.0,
    tiempo_reaccion_promedio FLOAT DEFAULT 0.0,
    fase VARCHAR(20) NOT NULL,
    nivel_dificultad VARCHAR(20) NOT NULL,
    ajustado_por_ia BOOLEAN DEFAULT FALSE,
    fecha_juego DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Flujo de Ejecución

### 1. Inicio de Sesión

```
Unity: POST /start-session { user_id: 1 }
  ↓
Backend: ¿Jugó hoy?
  ├─ NO → Tutorial (velocidad: 8, intervalo: 3, solo rojas)
  └─ SÍ → ¿Terminó tutorial?
       ├─ NO → Continuar tutorial
       └─ SÍ → Modo adaptativo (última config)
  ↓
Unity: Aplicar configuración
```

### 2. Tutorial (1 minuto)

```
Unity: Juega con parámetros fijos
  ↓ Cada 25s
Unity: POST /report-metrics { fase: "tutorial", ... }
  ↓
Backend: Guardar segmento, NO ajustar
  ↓
Unity: Continuar con misma configuración
  ↓ Después de 60s
Backend: Próximo reporte → fase: "adaptativo"
```

### 3. Modo Adaptativo

```
Unity: Juega con parámetros actuales
  ↓ Cada 25s
Unity: POST /report-metrics { fase: "adaptativo", ... }
  ↓
Backend: Guardar segmento
Backend: Analizar últimos 3 segmentos
Backend: Llamar a Gemini IA
  ↓
Gemini: Analiza métricas
Gemini: Devuelve ajuste (si necesario)
  ↓
Backend: Responde con ajuste
  ↓
Unity: Aplicar nueva config con Lerp (2s)
Unity: Continuar jugando
```

---

## 🧪 Pruebas

### Probar Inicio de Sesión

```bash
curl -X POST http://localhost:5000/paseo/start-session \
-H "Content-Type: application/json" \
-d '{"user_id": 1}'
```

### Probar Reporte de Métricas

```bash
curl -X POST http://localhost:5000/paseo/report-metrics \
-H "Content-Type: application/json" \
-d '{
  "user_id": 1,
  "velocidad_esferas": 10.0,
  "intervalo_spawn": 2.5,
  "colores_activos": "rojo",
  "duracion_segmento": 25.5,
  "esferas_rojas_atrapadas": 8,
  "esferas_azules_atrapadas": 0,
  "esferas_perdidas": 2,
  "tiempo_reaccion_promedio": 1.2,
  "fase": "adaptativo",
  "nivel_dificultad": "facil"
}'
```

### Probar Ajuste de IA (Sin DB)

```bash
curl -X POST http://localhost:5000/paseo/test-adjustment \
-H "Content-Type: application/json" \
-d '{
  "precision_promedio": 85.5,
  "tiempo_reaccion_promedio": 1.1,
  "perdidas": 3,
  "total_esferas": 20,
  "nivel_actual": "facil",
  "configuracion_actual": {
    "velocidad_esferas": 10.0,
    "intervalo_spawn": 2.5,
    "colores_activos": "rojo"
  }
}'
```

---

## 📈 Optimización de Costos

- **Sin Batch**: Gemini se llama cada 20-30s por usuario = ~120 llamadas/hora/usuario
- **Batch Potencial**: Agrupar ajustes de múltiples usuarios en 1 llamada
- **Caché**: Si múltiples usuarios tienen métricas similares, reusar ajuste

---

## 🎯 Valor para la Tesis

1. **Evaluación Continua Dinámica**: Ajuste cada 20-30s vs cada sesión
2. **Adaptación Individualizada**: IA ajusta parámetros según capacidades reales
3. **Comparativa con Abecedario**: Nivel diario vs ajuste continuo
4. **Métricas Ricas**: Precisión, tiempo reacción, tasa de pérdida
5. **Escalabilidad**: Backend preparado para múltiples usuarios concurrentes

---

## ✅ Checklist de Implementación

- [x] Backend Flask
  - [x] Modelo `PaseoSession`
  - [x] Servicio `PaseoService`
  - [x] Servicio `GeminiPaseoService`
  - [x] Controlador `paseo_controller`
  - [x] Endpoints registrados
- [x] Documentación Unity
  - [x] Clases de serialización
  - [x] Código de integración `GameManagerPaseo`
  - [x] Modificaciones `EsferaColision`
- [ ] Unity Implementación
  - [ ] Crear `GameManagerPaseo` (o modificar existente)
  - [ ] Integrar HTTP requests
  - [ ] Aplicar ajustes con Lerp
  - [ ] Probar flujo completo
- [ ] Base de Datos
  - [ ] Migración `paseo_session` table
  - [ ] Probar INSERT/SELECT
- [ ] Testing
  - [ ] Probar `/start-session`
  - [ ] Probar `/report-metrics`
  - [ ] Probar `/test-adjustment`
  - [ ] Probar transición Tutorial → Adaptativo

---

## 🔧 Próximos Pasos

1. **Migración de Base de Datos**: Crear tabla `paseo_session`
2. **Probar Backend**: Ejecutar Flask y probar endpoints con curl
3. **Implementar en Unity**: Copiar código de integración
4. **Prueba End-to-End**: Usuario 1 min tutorial → modo adaptativo
5. **Métricas de Evolución**: Generar reportes con `/evolution/<user_id>`
