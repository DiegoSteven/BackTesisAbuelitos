# 🎮 Guía de Integración Unity - Memory Game Backend

## 📋 Índice
1. [Setup Inicial](#setup-inicial)
2. [Clases de Datos (DTOs)](#clases-de-datos)
3. [Servicio HTTP](#servicio-http)
4. [Flujo del Juego](#flujo-del-juego)
5. [Ejemplo Completo](#ejemplo-completo)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Setup Inicial

### 1. URL del Backend
```csharp
// Constante con la URL de tu backend
private const string BASE_URL = "http://localhost:5000";
```

### 2. Dependencias Necesarias
Unity viene con `UnityWebRequest` integrado. No necesitas importar nada adicional.

---

## 📦 Clases de Datos (DTOs)

Crea un archivo **`MemoryGameAPI.cs`** en tu proyecto Unity con estas clases:

```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

[System.Serializable]
public class GameConfig
{
    public int total_pairs;
    public string grid_size;
    public int time_limit;
    public int memorization_time;
    public string difficulty_label;
}

[System.Serializable]
public class ConfigResponse
{
    public bool success;
    public ConfigData data;
}

[System.Serializable]
public class ConfigData
{
    public int user_id;
    public GameConfig current_config;
    public bool is_first_time;
    public string last_updated;
}

[System.Serializable]
public class SessionData
{
    public string completion_status;  // "completed", "abandoned", "timeout"
    public int total_flips;
    public int pairs_found;
    public int total_pairs;
    public float elapsed_time;
    public int time_limit;
    public float accuracy;
}

[System.Serializable]
public class SubmitRequest
{
    public int user_id;
    public SessionData session_data;
}

[System.Serializable]
public class PerformanceAssessment
{
    public float overall_score;
    public string memory_retention;
    public string speed;
    public string accuracy;
}

[System.Serializable]
public class AdjustmentSummary
{
    public List<string> changed_fields;
    public string previous_difficulty;
    public string new_difficulty;
}

[System.Serializable]
public class AIAnalysis
{
    public PerformanceAssessment performance_assessment;
    public string adjustment_decision;
    public GameConfig next_session_config;
    public string reason;
    public AdjustmentSummary adjustment_summary;
}

[System.Serializable]
public class SubmitResultData
{
    public bool session_saved;
    public int session_id;
    public AIAnalysis ai_analysis;
}

[System.Serializable]
public class SubmitResponse
{
    public bool success;
    public SubmitResultData data;
    public string timestamp;
}

[System.Serializable]
public class StatsData
{
    public int total_sessions;
    public int completed_sessions;
    public float average_accuracy;
    public float best_time;
    public List<SessionSummary> recent_sessions;
}

[System.Serializable]
public class SessionSummary
{
    public int session_id;
    public string difficulty_level;
    public int total_pairs;
    public float accuracy;
    public float elapsed_time;
    public string completion_status;
}

[System.Serializable]
public class StatsResponse
{
    public bool success;
    public StatsData data;
}
```

---

## 🌐 Servicio HTTP

Crea **`MemoryGameService.cs`**:

```csharp
using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class MemoryGameService : MonoBehaviour
{
    private const string BASE_URL = "http://localhost:5000";
    
    // ==================== GET CONFIG ====================
    public IEnumerator GetUserConfig(int userId, Action<ConfigResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BASE_URL}/memory-game/config/{userId}";
        
        Debug.Log($"📤 GET Request to: {url}");
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"📥 Response: {request.downloadHandler.text}");
                
                ConfigResponse response = JsonUtility.FromJson<ConfigResponse>(request.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                string error = $"Error: {request.error}\nResponse: {request.downloadHandler.text}";
                Debug.LogError($"❌ {error}");
                onError?.Invoke(error);
            }
        }
    }
    
    // ==================== SUBMIT RESULTS ====================
    public IEnumerator SubmitResults(SubmitRequest data, Action<SubmitResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BASE_URL}/memory-game/submit-results";
        string jsonData = JsonUtility.ToJson(data);
        
        Debug.Log($"📤 POST Request to: {url}");
        Debug.Log($"📦 Data: {jsonData}");
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"📥 Response: {request.downloadHandler.text}");
                
                SubmitResponse response = JsonUtility.FromJson<SubmitResponse>(request.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                string error = $"Error: {request.error}\nResponse: {request.downloadHandler.text}";
                Debug.LogError($"❌ {error}");
                onError?.Invoke(error);
            }
        }
    }
    
    // ==================== GET STATS ====================
    public IEnumerator GetUserStats(int userId, Action<StatsResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BASE_URL}/memory-game/stats/{userId}";
        
        Debug.Log($"📤 GET Request to: {url}");
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"📥 Response: {request.downloadHandler.text}");
                
                StatsResponse response = JsonUtility.FromJson<StatsResponse>(request.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                string error = $"Error: {request.error}\nResponse: {request.downloadHandler.text}";
                Debug.LogError($"❌ {error}");
                onError?.Invoke(error);
            }
        }
    }
}
```

---

## 🎮 Flujo del Juego

Crea **`MemoryGameManager.cs`** que controle el flujo completo:

```csharp
using System;
using System.Collections;
using UnityEngine;

public class MemoryGameManager : MonoBehaviour
{
    [Header("Configuration")]
    public int userId = 1; // ID del usuario
    
    [Header("References")]
    private MemoryGameService apiService;
    
    [Header("Game State")]
    private GameConfig currentConfig;
    private float startTime;
    private int totalFlips = 0;
    private int pairsFound = 0;
    
    void Awake()
    {
        // Obtener o crear el servicio API
        apiService = GetComponent<MemoryGameService>();
        if (apiService == null)
        {
            apiService = gameObject.AddComponent<MemoryGameService>();
        }
    }
    
    void Start()
    {
        // Al iniciar, obtener la configuración del servidor
        StartCoroutine(InitializeGame());
    }
    
    // ==================== PASO 1: INICIALIZAR JUEGO ====================
    IEnumerator InitializeGame()
    {
        Debug.Log("🎮 Inicializando juego...");
        
        yield return apiService.GetUserConfig(
            userId,
            OnConfigReceived,
            OnConfigError
        );
    }
    
    void OnConfigReceived(ConfigResponse response)
    {
        if (response.success)
        {
            currentConfig = response.data.current_config;
            
            Debug.Log($"✅ Configuración recibida:");
            Debug.Log($"   Dificultad: {currentConfig.difficulty_label}");
            Debug.Log($"   Pares: {currentConfig.total_pairs}");
            Debug.Log($"   Grid: {currentConfig.grid_size}");
            Debug.Log($"   Tiempo límite: {currentConfig.time_limit}s");
            Debug.Log($"   Tiempo memorización: {currentConfig.memorization_time}s");
            Debug.Log($"   Primera vez: {response.data.is_first_time}");
            
            // Configurar el juego con estos parámetros
            SetupGame(currentConfig);
            
            // Mostrar tutorial si es primera vez
            if (response.data.is_first_time)
            {
                ShowTutorial();
            }
        }
    }
    
    void OnConfigError(string error)
    {
        Debug.LogError($"❌ Error obteniendo configuración: {error}");
        // Usar configuración por defecto
        UseDefaultConfig();
    }
    
    // ==================== PASO 2: CONFIGURAR JUEGO ====================
    void SetupGame(GameConfig config)
    {
        // Aquí configuras tu juego con los parámetros recibidos
        // Ejemplo:
        
        // 1. Crear el grid según config.grid_size (ej: "2x3")
        string[] dimensions = config.grid_size.Split('x');
        int rows = int.Parse(dimensions[0]);
        int cols = int.Parse(dimensions[1]);
        
        // 2. Generar pares de cartas
        GenerateCards(config.total_pairs);
        
        // 3. Configurar timer
        SetupTimer(config.time_limit);
        
        // 4. Configurar fase de memorización
        StartMemorizationPhase(config.memorization_time);
        
        Debug.Log($"🎲 Juego configurado: Grid {rows}x{cols}, {config.total_pairs} pares");
    }
    
    // ==================== PASO 3: JUGAR ====================
    void StartMemorizationPhase(int seconds)
    {
        // Mostrar todas las cartas por X segundos
        Debug.Log($"👀 Fase de memorización: {seconds}s");
        
        // TODO: Implementar tu lógica
        // - Mostrar todas las cartas
        // - Esperar X segundos
        // - Voltear las cartas
        // - Comenzar el juego
        
        Invoke(nameof(StartGamePhase), seconds);
    }
    
    void StartGamePhase()
    {
        Debug.Log("🎮 ¡Juego iniciado!");
        startTime = Time.time;
        totalFlips = 0;
        pairsFound = 0;
    }
    
    // Llamar esto cada vez que el jugador voltee una carta
    public void OnCardFlipped()
    {
        totalFlips++;
        Debug.Log($"🃏 Carta volteada (Total: {totalFlips})");
    }
    
    // Llamar esto cada vez que se encuentre un par
    public void OnPairFound()
    {
        pairsFound++;
        Debug.Log($"✨ ¡Par encontrado! ({pairsFound}/{currentConfig.total_pairs})");
        
        // Verificar si se completó el juego
        if (pairsFound >= currentConfig.total_pairs)
        {
            OnGameCompleted();
        }
    }
    
    // ==================== PASO 4: TERMINAR JUEGO ====================
    void OnGameCompleted()
    {
        float elapsedTime = Time.time - startTime;
        
        Debug.Log("🎉 ¡Juego completado!");
        Debug.Log($"   Tiempo: {elapsedTime:F1}s");
        Debug.Log($"   Volteos: {totalFlips}");
        Debug.Log($"   Pares: {pairsFound}");
        
        // Calcular accuracy
        int optimalFlips = currentConfig.total_pairs * 2; // Cada par = 2 cartas
        float accuracy = (float)optimalFlips / totalFlips * 100f;
        accuracy = Mathf.Min(accuracy, 100f); // Max 100%
        
        // Enviar resultados al servidor
        StartCoroutine(SendResults("completed", elapsedTime, accuracy));
    }
    
    // También puedes llamar esto si abandonan o se acaba el tiempo
    public void OnGameAbandoned()
    {
        float elapsedTime = Time.time - startTime;
        StartCoroutine(SendResults("abandoned", elapsedTime, 0f));
    }
    
    public void OnGameTimeout()
    {
        float elapsedTime = currentConfig.time_limit;
        float accuracy = (float)pairsFound / currentConfig.total_pairs * 100f;
        StartCoroutine(SendResults("timeout", elapsedTime, accuracy));
    }
    
    // ==================== PASO 5: ENVIAR RESULTADOS ====================
    IEnumerator SendResults(string status, float elapsedTime, float accuracy)
    {
        SubmitRequest request = new SubmitRequest
        {
            user_id = userId,
            session_data = new SessionData
            {
                completion_status = status,
                total_flips = totalFlips,
                pairs_found = pairsFound,
                total_pairs = currentConfig.total_pairs,
                elapsed_time = elapsedTime,
                time_limit = currentConfig.time_limit,
                accuracy = accuracy
            }
        };
        
        Debug.Log("📊 Enviando resultados al servidor...");
        
        yield return apiService.SubmitResults(
            request,
            OnResultsSubmitted,
            OnSubmitError
        );
    }
    
    void OnResultsSubmitted(SubmitResponse response)
    {
        if (response.success)
        {
            AIAnalysis ai = response.data.ai_analysis;
            
            Debug.Log("✅ Resultados enviados!");
            Debug.Log($"   Session ID: {response.data.session_id}");
            Debug.Log($"   🤖 ANÁLISIS DE IA:");
            Debug.Log($"      Score: {ai.performance_assessment.overall_score}/10");
            Debug.Log($"      Retención: {ai.performance_assessment.memory_retention}");
            Debug.Log($"      Decisión: {ai.adjustment_decision}");
            Debug.Log($"      Nueva dificultad: {ai.next_session_config.difficulty_label}");
            Debug.Log($"      Razón: {ai.reason}");
            
            // Actualizar la configuración local para la próxima partida
            currentConfig = ai.next_session_config;
            
            // Mostrar feedback al usuario
            ShowAIFeedback(ai);
            
            // Preguntar si quiere jugar otra vez
            ShowPlayAgainDialog();
        }
    }
    
    void OnSubmitError(string error)
    {
        Debug.LogError($"❌ Error enviando resultados: {error}");
        // Mostrar mensaje de error al usuario
    }
    
    // ==================== HELPERS ====================
    void GenerateCards(int totalPairs)
    {
        // TODO: Tu lógica para generar y colocar las cartas
        Debug.Log($"🃏 Generando {totalPairs} pares de cartas...");
    }
    
    void SetupTimer(int seconds)
    {
        // TODO: Tu lógica del timer
        Debug.Log($"⏱️ Timer configurado: {seconds}s");
    }
    
    void ShowTutorial()
    {
        // TODO: Mostrar tutorial para nuevos jugadores
        Debug.Log("📖 Mostrando tutorial...");
    }
    
    void ShowAIFeedback(AIAnalysis ai)
    {
        // TODO: Mostrar feedback bonito en UI
        // Puedes usar ai.reason, ai.performance_assessment.overall_score, etc.
        Debug.Log("💬 Mostrando feedback de IA al jugador...");
    }
    
    void ShowPlayAgainDialog()
    {
        // TODO: Mostrar diálogo "¿Jugar otra vez?"
        Debug.Log("🔄 ¿Jugar otra vez?");
    }
    
    void UseDefaultConfig()
    {
        currentConfig = new GameConfig
        {
            total_pairs = 3,
            grid_size = "2x3",
            time_limit = 60,
            memorization_time = 5,
            difficulty_label = "tutorial"
        };
        
        SetupGame(currentConfig);
    }
    
    // ==================== BONUS: VER ESTADÍSTICAS ====================
    public void ShowUserStats()
    {
        StartCoroutine(FetchStats());
    }
    
    IEnumerator FetchStats()
    {
        yield return apiService.GetUserStats(
            userId,
            OnStatsReceived,
            OnStatsError
        );
    }
    
    void OnStatsReceived(StatsResponse response)
    {
        if (response.success)
        {
            StatsData stats = response.data;
            
            Debug.Log("📊 ESTADÍSTICAS DEL JUGADOR:");
            Debug.Log($"   Total sesiones: {stats.total_sessions}");
            Debug.Log($"   Completadas: {stats.completed_sessions}");
            Debug.Log($"   Precisión promedio: {stats.average_accuracy:F1}%");
            Debug.Log($"   Mejor tiempo: {stats.best_time:F1}s");
            
            // TODO: Mostrar en UI
        }
    }
    
    void OnStatsError(string error)
    {
        Debug.LogError($"❌ Error obteniendo stats: {error}");
    }
}
```

---

## 🚀 Uso en Unity

### Paso 1: Crear los Scripts
1. Copia **`MemoryGameAPI.cs`** (clases de datos)
2. Copia **`MemoryGameService.cs`** (servicio HTTP)
3. Copia **`MemoryGameManager.cs`** (manager del juego)

### Paso 2: Configurar la Escena
1. Crea un GameObject vacío llamado **"GameManager"**
2. Agrega el componente **`MemoryGameManager`**
3. En el Inspector, configura el **`userId`** (ej: 1)

### Paso 3: Asegúrate que el Backend esté corriendo
```bash
python app/app.py
```

### Paso 4: Play!
Al darle Play en Unity, verás en la consola:
```
🎮 Inicializando juego...
📤 GET Request to: http://localhost:5000/memory-game/config/1
📥 Response: {...}
✅ Configuración recibida:
   Dificultad: tutorial
   Pares: 3
   Grid: 2x3
   ...
```

---

## 🎯 Flujo Completo

```
1. START
   ↓
2. GetUserConfig(userId) → Recibe configuración del servidor
   ↓
3. SetupGame(config) → Configura grid, cartas, timer
   ↓
4. StartMemorizationPhase() → Muestra cartas X segundos
   ↓
5. StartGamePhase() → Jugador juega
   ↓
6. OnPairFound() × N → Detecta pares encontrados
   ↓
7. OnGameCompleted() → Calcula accuracy y tiempo
   ↓
8. SubmitResults() → Envía al servidor
   ↓
9. OnResultsSubmitted() → Recibe análisis de IA
   ↓
10. ShowAIFeedback() → Muestra al jugador
    ↓
11. ShowPlayAgainDialog() → ¿Otra partida?
    ↓ (Si acepta)
12. SetupGame(newConfig) → Usa nueva configuración adaptada
```

---

## 🐛 Troubleshooting

### ❌ Error: "Connection refused"
**Solución:** Asegúrate que Flask esté corriendo
```bash
python app/app.py
```

### ❌ Error: "CORS policy"
**Solución:** El backend ya tiene CORS habilitado, debería funcionar.

### ❌ Error: "JSON parse error"
**Solución:** Verifica que las clases C# coincidan con el JSON del backend.
Revisa los logs del backend para ver el JSON exacto.

### ⚠️ No aparece nada
**Solución:** Abre la consola de Unity (Window → General → Console) para ver los logs.

---

## 📋 Resumen

1. **Obtener Config**: Al iniciar el juego
2. **Jugar**: Con la configuración recibida
3. **Enviar Resultados**: Al terminar
4. **Recibir IA**: Nueva configuración adaptada
5. **Repetir**: Con nueva dificultad

**¡El backend se encarga de toda la adaptación automáticamente!** 🤖

---

**Next Steps:**
- Implementa la generación de cartas según `total_pairs`
- Implementa el timer con `time_limit`
- Implementa la fase de memorización con `memorization_time`
- Diseña UI para mostrar feedback de IA
- Agrega efectos visuales cuando sube/baja la dificultad

¿Necesitas ayuda con alguna parte específica? 🚀
