# 🎮 Unity Integration - Quick Start

## 3 Archivos C# Necesarios

### 1️⃣ `MemoryGameAPI.cs` - Clases de Datos
Contiene todas las clases para serializar/deserializar JSON

### 2️⃣ `MemoryGameService.cs` - Cliente HTTP  
Contiene 3 métodos:
- `GetUserConfig()` - Obtener configuración
- `SubmitResults()` - Enviar resultados  
- `GetUserStats()` - Ver estadísticas

### 3️⃣ `MemoryGameManager.cs` - Controlador del Juego
Orquesta todo el flujo del juego

---

## 🔄 Flujo Simple

```
INICIO DEL JUEGO:
├─ 1. GetUserConfig(userId)
│  └─ Backend devuelve: { total_pairs: 3, grid_size: "2x3", time_limit: 60, ... }
│
├─ 2. SetupGame(config)
│  ├─ Crear grid según config.grid_size
│  ├─ Generar config.total_pairs pares de cartas
│  └─ Configurar timer de config.time_limit segundos
│
├─ 3. Mostrar cartas config.memorization_time segundos
│
├─ 4. JUGAR
│  ├─ Jugador voltea cartas → totalFlips++
│  ├─ Encuentra par → pairsFound++
│  └─ Todos los pares → OnGameCompleted()
│
└─ 5. SubmitResults({ accuracy, time, flips, ... })
   └─ Backend devuelve análisis IA:
      {
        "ai_score": 8.5,
        "decision": "increase_difficulty",
        "new_config": { total_pairs: 4, grid_size: "2x4", ... },
        "reason": "Excelente desempeño..."
      }

REPETIR desde paso 2 con nueva configuración
```

---

## 💡 Lo Más Importante

### Al INICIAR el juego:
```csharp
// Esto obtiene la configuración adaptada para este usuario
StartCoroutine(apiService.GetUserConfig(userId, OnConfigReceived, OnError));

void OnConfigReceived(ConfigResponse response) {
    GameConfig config = response.data.current_config;
    
    // Usa estos valores:
    int pares = config.total_pairs;           // Ej: 3
    string grid = config.grid_size;           // Ej: "2x3"
    int tiempo = config.time_limit;           // Ej: 60
    int memoriza = config.memorization_time;  // Ej: 5
    string dificultad = config.difficulty_label; // Ej: "tutorial"
}
```

### Al TERMINAR el juego:
```csharp
// Calcula la accuracy
int optimalFlips = totalPairs * 2;  // Lo ideal
float accuracy = (float)optimalFlips / totalFlips * 100f;

// Crea el request
SubmitRequest request = new SubmitRequest {
    user_id = userId,
    session_data = new SessionData {
        completion_status = "completed",  // o "abandoned", "timeout"
        total_flips = totalFlips,         // Cuántas veces volteó cartas
        pairs_found = pairsFound,         // Cuántos pares encontró
        total_pairs = totalPairs,         // Cuántos pares había
        elapsed_time = elapsedTime,       // Tiempo que tardó
        time_limit = timeLimit,           // Límite que tenía
        accuracy = accuracy               // % de eficiencia
    }
};

// Envía al servidor
StartCoroutine(apiService.SubmitResults(request, OnResultsSubmitted, OnError));

void OnResultsSubmitted(SubmitResponse response) {
    AIAnalysis ai = response.data.ai_analysis;
    
    // Muestra al jugador:
    Debug.Log($"Tu score: {ai.performance_assessment.overall_score}/10");
    Debug.Log($"Decisión IA: {ai.adjustment_decision}");
    Debug.Log($"Nueva dificultad: {ai.next_session_config.difficulty_label}");
    Debug.Log($"Razón: {ai.reason}");
    
    // Actualiza para la próxima partida
    currentConfig = ai.next_session_config;
}
```

---

## 🎯 Ejemplo Mínimo Funcional

```csharp
using UnityEngine;

public class SimpleMemoryGame : MonoBehaviour
{
    private MemoryGameService api;
    private int userId = 1;
    private GameConfig currentConfig;
    
    void Start()
    {
        api = gameObject.AddComponent<MemoryGameService>();
        
        // Paso 1: Obtener configuración
        StartCoroutine(api.GetUserConfig(userId, 
            response => {
                currentConfig = response.data.current_config;
                Debug.Log($"Juega con {currentConfig.total_pairs} pares!");
                
                // Aquí: crear tu juego con currentConfig
                StartGame();
            },
            error => Debug.LogError(error)
        ));
    }
    
    void StartGame()
    {
        // Tu código de juego aquí...
    }
    
    void OnGameFinished(int flips, int pairsFound, float time)
    {
        // Paso 2: Enviar resultados
        float accuracy = (currentConfig.total_pairs * 2f) / flips * 100f;
        
        SubmitRequest request = new SubmitRequest {
            user_id = userId,
            session_data = new SessionData {
                completion_status = "completed",
                total_flips = flips,
                pairs_found = pairsFound,
                total_pairs = currentConfig.total_pairs,
                elapsed_time = time,
                time_limit = currentConfig.time_limit,
                accuracy = accuracy
            }
        };
        
        StartCoroutine(api.SubmitResults(request,
            response => {
                var ai = response.data.ai_analysis;
                Debug.Log($"IA dice: {ai.reason}");
                
                // Actualizar para próxima partida
                currentConfig = ai.next_session_config;
            },
            error => Debug.LogError(error)
        ));
    }
}
```

---

## ✅ Checklist de Integración

- [ ] Backend corriendo (`python app/app.py`)
- [ ] Copiar 3 archivos C# al proyecto Unity
- [ ] Crear GameObject "GameManager" 
- [ ] Agregar componente `MemoryGameManager`
- [ ] Configurar `userId` en el Inspector
- [ ] Implementar `GenerateCards(totalPairs)`
- [ ] Implementar `SetupTimer(timeLimit)`
- [ ] Implementar `StartMemorizationPhase(seconds)`
- [ ] Llamar `OnCardFlipped()` cuando voltee carta
- [ ] Llamar `OnPairFound()` cuando encuentre par
- [ ] Probar en Play Mode

---

## 🚀 Para Probar

1. Inicia Flask: `python app/app.py`
2. Dale Play en Unity
3. Mira la consola de Unity → verás los logs
4. Mira la consola de Flask → verás los requests

**Los logs te mostrarán TODO lo que está pasando** 📊

---

## 📖 Documentación Completa

Para código completo y detalles, ver: **`UNITY_INTEGRATION_GUIDE.md`**

---

**¡Listo para integrar!** 🎉
