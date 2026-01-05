# 🎮 Ejemplos de Consumo de API - Juego de Memoria

Ejemplos prácticos de cómo consumir las APIs del Memory Game en diferentes escenarios.

---

## 📋 Índice
1. [Escenario 1: Primera Vez del Jugador](#escenario-1-primera-vez)
2. [Escenario 2: Jugador con Buen Desempeño](#escenario-2-buen-desempeño)
3. [Escenario 3: Jugador con Mal Desempeño](#escenario-3-mal-desempeño)
4. [Escenario 4: Ver Progreso](#escenario-4-ver-progreso)
5. [Ejemplos en Unity C#](#ejemplos-unity-c)
6. [Ejemplos en PowerShell](#ejemplos-powershell)

---

## 🎯 Escenario 1: Primera Vez del Jugador

### Flujo Completo

```
Usuario nuevo → Obtener config → Jugar → Enviar resultados → Recibir feedback
```

### 1️⃣ Obtener Configuración Inicial

**Request:**
```http
GET http://localhost:5000/memory-game/config/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "current_config": {
      "total_pairs": 3,          // ← Crear 3 pares de cartas
      "grid_size": "2x3",        // ← Grid de 2 filas x 3 columnas
      "time_limit": 60,          // ← 60 segundos para completar
      "memorization_time": 5,    // ← 5 segundos para memorizar
      "difficulty_label": "tutorial"  // ← Nivel: tutorial
    },
    "is_first_time": true,       // ← Primera vez jugando
    "last_updated": "2025-12-15T20:00:00"
  }
}
```

**En Unity:**
```csharp
// Usar estos valores para configurar el juego
int totalPairs = 3;
string gridSize = "2x3";  // Parsear: 2 filas x 3 columnas
int timeLimit = 60;       // Segundos
int memorizationTime = 5; // Segundos para mostrar cartas

// Como es primera vez, mostrar tutorial
if (isFirstTime) {
    ShowTutorial();
}
```

### 2️⃣ Jugador Completa el Juego

El jugador juega y obtiene estos resultados:
- ✅ Completó el juego
- 🃏 Volteó 10 cartas en total
- ⏱️ Tardó 48.5 segundos
- ✨ Encontró los 3 pares

**Cálculo de Accuracy:**
```csharp
int optimalFlips = 3 * 2;  // 3 pares × 2 cartas = 6 volteos óptimos
float accuracy = (6f / 10f) * 100f;  // = 60%
```

### 3️⃣ Enviar Resultados

**Request:**
```http
POST http://localhost:5000/memory-game/submit-results
Content-Type: application/json

{
  "user_id": 1,
  "session_data": {
    "completion_status": "completed",
    "total_flips": 10,
    "pairs_found": 3,
    "total_pairs": 3,
    "elapsed_time": 48.5,
    "time_limit": 60,
    "accuracy": 60.0
  }
}
```

### 4️⃣ Recibir Análisis de IA

**Response:**
```json
{
  "success": true,
  "data": {
    "session_saved": true,
    "session_id": 1,
    "ai_analysis": {
      "performance_assessment": {
        "overall_score": 5.6,           // ← Score: 5.6/10
        "memory_retention": "medium",   // ← Retención media
        "speed": "good",                // ← Buena velocidad
        "accuracy": "medium"            // ← Accuracy media
      },
      "adjustment_decision": "keep_same",  // ← Mantener nivel
      "next_session_config": {
        "total_pairs": 3,               // ← Mismos 3 pares
        "grid_size": "2x3",             // ← Mismo grid
        "time_limit": 60,
        "memorization_time": 5,
        "difficulty_label": "tutorial"   // ← Sigue en tutorial
      },
      "reason": "Buen desempeño (score 5.6/10). Mantener nivel actual.",
      "adjustment_summary": {
        "changed_fields": [],            // ← No hubo cambios
        "previous_difficulty": "tutorial",
        "new_difficulty": "tutorial"
      }
    }
  },
  "timestamp": "2025-12-15T21:45:00Z"
}
```

**En Unity - Mostrar Feedback:**
```csharp
string feedback = $@"
¡Buen trabajo! 🎉

Tu puntuación: {5.6}/10
Nivel de memoria: Medio
Velocidad: Buena

Consejo de IA:
{response.data.ai_analysis.reason}

Próxima partida: {3} pares (Tutorial)
";

ShowFeedbackDialog(feedback);
```

---

## 🚀 Escenario 2: Jugador con Buen Desempeño

### El jugador juega muy bien y la IA sube la dificultad

### 1️⃣ Obtener Config Actual

**Response:**
```json
{
  "current_config": {
    "total_pairs": 3,
    "grid_size": "2x3",
    "difficulty_label": "tutorial"
  },
  "is_first_time": false
}
```

### 2️⃣ Jugador Juega Excelente

Resultados:
- ✅ Completado
- 🃏 Solo 6 volteos (óptimo!)
- ⏱️ 28 segundos (muy rápido)
- ✨ 3 pares encontrados

```csharp
int optimalFlips = 6;
int actualFlips = 6;
float accuracy = (6f / 6f) * 100f;  // = 100% ¡Perfecto!
```

### 3️⃣ Enviar Resultados

**Request:**
```json
{
  "user_id": 1,
  "session_data": {
    "completion_status": "completed",
    "total_flips": 6,        // ← Óptimo
    "pairs_found": 3,
    "total_pairs": 3,
    "elapsed_time": 28.0,    // ← Muy rápido
    "time_limit": 60,
    "accuracy": 100.0        // ← ¡Perfecto!
  }
}
```

### 4️⃣ IA Aumenta Dificultad

**Response:**
```json
{
  "success": true,
  "data": {
    "session_saved": true,
    "session_id": 2,
    "ai_analysis": {
      "performance_assessment": {
        "overall_score": 10.0,          // ← ¡Score perfecto!
        "memory_retention": "high",     // ← Alta retención
        "speed": "high",                // ← Alta velocidad
        "accuracy": "high"              // ← Alta precisión
      },
      "adjustment_decision": "increase_difficulty",  // ← ¡SUBE!
      "next_session_config": {
        "total_pairs": 4,               // ← ⬆️ De 3 a 4 pares
        "grid_size": "2x4",             // ← ⬆️ Grid más grande
        "time_limit": 90,               // ← Más tiempo
        "memorization_time": 4,         // ← ⬇️ Menos tiempo para memorizar
        "difficulty_label": "easy"      // ← ⬆️ Nivel EASY
      },
      "reason": "Excelente desempeño (score 10.0/10). Listo para más desafío. Cambiando de tutorial a easy.",
      "adjustment_summary": {
        "changed_fields": [
          "total_pairs",      // ← Cambió
          "grid_size",        // ← Cambió
          "time_limit",       // ← Cambió
          "memorization_time" // ← Cambió
        ],
        "previous_difficulty": "tutorial",
        "new_difficulty": "easy"
      }
    }
  }
}
```

**En Unity - Animación de Nivel Subido:**
```csharp
if (ai.adjustment_decision == "increase_difficulty") 
{
    PlayLevelUpAnimation();
    
    string message = $@"
    ¡INCREÍBLE! 🌟
    
    Puntuación perfecta: 10/10
    
    🎯 Memoria: Alta
    ⚡ Velocidad: Alta
    🎯 Precisión: Alta
    
    🎉 ¡SUBISTE DE NIVEL!
    Tutorial → Easy
    
    Nueva dificultad:
    • {4} pares de cartas
    • Grid {2}x{4}
    • {90} segundos
    
    ¡Sigue así! 💪
    ";
    
    ShowCelebrationDialog(message);
}
```

---

## ⬇️ Escenario 3: Jugador con Mal Desempeño

### El jugador tiene dificultades y la IA reduce la dificultad

### 1️⃣ Config Actual (Medium)

```json
{
  "current_config": {
    "total_pairs": 6,
    "grid_size": "3x4",
    "time_limit": 120,
    "difficulty_label": "medium"
  }
}
```

### 2️⃣ Jugador con Dificultades

Resultados:
- ⏱️ Se acabó el tiempo (timeout)
- 🃏 35 volteos (muchos errores)
- ✨ Solo encontró 4 de 6 pares
- ❌ No completó

```csharp
float accuracy = (4f / 6f) * 100f;  // = 66.67% (solo 4 de 6 pares)
```

### 3️⃣ Enviar Resultados

**Request:**
```json
{
  "user_id": 1,
  "session_data": {
    "completion_status": "timeout",  // ← Se acabó el tiempo
    "total_flips": 35,               // ← Muchos volteos
    "pairs_found": 4,                // ← Solo 4 de 6
    "total_pairs": 6,
    "elapsed_time": 120.0,           // ← Tiempo completo
    "time_limit": 120,
    "accuracy": 66.67
  }
}
```

### 4️⃣ IA Reduce Dificultad

**Response:**
```json
{
  "success": true,
  "data": {
    "session_saved": true,
    "session_id": 5,
    "ai_analysis": {
      "performance_assessment": {
        "overall_score": 3.0,           // ← Score bajo
        "memory_retention": "low",      // ← Baja retención
        "speed": "low",                 // ← Lento
        "accuracy": "low"               // ← Baja precisión
      },
      "adjustment_decision": "decrease_difficulty",  // ← BAJA
      "next_session_config": {
        "total_pairs": 4,               // ← ⬇️ De 6 a 4 pares
        "grid_size": "2x4",             // ← ⬇️ Grid más pequeño
        "time_limit": 90,               // ← Menos tiempo necesario
        "memorization_time": 4,         // ← ⬆️ Más tiempo para memorizar
        "difficulty_label": "easy"      // ← ⬇️ Nivel EASY
      },
      "reason": "Desempeño bajo (score 3.0/10). Reducir dificultad. Cambiando de medium a easy.",
      "adjustment_summary": {
        "changed_fields": [
          "total_pairs",
          "grid_size",
          "time_limit",
          "memorization_time"
        ],
        "previous_difficulty": "medium",
        "new_difficulty": "easy"
      }
    }
  }
}
```

**En Unity - Mensaje Motivador:**
```csharp
if (ai.adjustment_decision == "decrease_difficulty") 
{
    string message = $@"
    ¡Sigue intentando! 💪
    
    Este nivel fue muy difícil.
    Vamos a probar algo más fácil.
    
    📊 Score: {3.0}/10
    
    Nuevo nivel: Easy
    • {4} pares (antes {6})
    • Grid {2}x{4}
    • Más tiempo para memorizar
    
    ¡Poco a poco mejorarás! 🌟
    ";
    
    ShowMotivationalDialog(message);
}
```

---

## 📊 Escenario 4: Ver Progreso del Jugador

### 1️⃣ Obtener Estadísticas

**Request:**
```http
GET http://localhost:5000/memory-game/stats/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_sessions": 8,              // ← Total de partidas
    "completed_sessions": 6,          // ← 6 completadas
    "average_accuracy": 78.5,         // ← 78.5% accuracy promedio
    "best_time": 28.0,                // ← Mejor tiempo: 28s
    "recent_sessions": [
      {
        "session_id": 8,
        "difficulty_level": "easy",
        "total_pairs": 4,
        "accuracy": 80.0,
        "elapsed_time": 55.3,
        "completion_status": "completed"
      },
      {
        "session_id": 7,
        "difficulty_level": "tutorial",
        "total_pairs": 3,
        "accuracy": 100.0,
        "elapsed_time": 28.0,
        "completion_status": "completed"
      }
      // ... más sesiones
    ]
  }
}
```

**En Unity - Pantalla de Estadísticas:**
```csharp
void ShowStats(StatsData stats) 
{
    string statsText = $@"
    📊 TUS ESTADÍSTICAS
    
    Partidas Jugadas: {stats.total_sessions}
    Completadas: {stats.completed_sessions}
    
    📈 Precisión Promedio: {stats.average_accuracy:F1}%
    ⏱️ Mejor Tiempo: {stats.best_time:F1}s
    
    ÚLTIMAS PARTIDAS:
    ";
    
    foreach (var session in stats.recent_sessions) 
    {
        string status = session.completion_status == "completed" ? "✅" : "❌";
        
        statsText += $@"
        {status} {session.difficulty_level} - {session.total_pairs} pares
           Accuracy: {session.accuracy:F0}%
           Tiempo: {session.elapsed_time:F1}s
        ";
    }
    
    DisplayStatsUI(statsText);
}
```

---

## 🎮 Ejemplos Unity C#

### Ejemplo Completo: Partida de Inicio a Fin

```csharp
using UnityEngine;
using System.Collections;

public class MemoryGameExample : MonoBehaviour
{
    private MemoryGameService api;
    private int userId = 1;
    private GameConfig currentConfig;
    private float startTime;
    private int totalFlips = 0;
    private int pairsFound = 0;
    
    void Start()
    {
        api = gameObject.AddComponent<MemoryGameService>();
        StartNewGame();
    }
    
    // ========== PASO 1: OBTENER CONFIGURACIÓN ==========
    void StartNewGame()
    {
        Debug.Log("🎮 Iniciando nueva partida...");
        
        StartCoroutine(api.GetUserConfig(userId, 
            response => {
                currentConfig = response.data.current_config;
                
                Debug.Log($"📥 Config recibida:");
                Debug.Log($"   Pares: {currentConfig.total_pairs}");
                Debug.Log($"   Grid: {currentConfig.grid_size}");
                Debug.Log($"   Dificultad: {currentConfig.difficulty_label}");
                
                SetupGameBoard();
            },
            error => {
                Debug.LogError($"❌ Error: {error}");
            }
        ));
    }
    
    // ========== PASO 2: CONFIGURAR JUEGO ==========
    void SetupGameBoard()
    {
        // Parsear grid
        string[] dims = currentConfig.grid_size.Split('x');
        int rows = int.Parse(dims[0]);
        int cols = int.Parse(dims[1]);
        
        // Crear cartas
        CreateCards(currentConfig.total_pairs, rows, cols);
        
        // Iniciar fase de memorización
        StartCoroutine(MemorizationPhase(currentConfig.memorization_time));
    }
    
    IEnumerator MemorizationPhase(int seconds)
    {
        Debug.Log($"👀 Memoriza las cartas: {seconds}s");
        
        // Mostrar todas las cartas
        ShowAllCards();
        
        // Esperar
        yield return new WaitForSeconds(seconds);
        
        // Ocultar cartas y comenzar
        HideAllCards();
        StartGameplay();
    }
    
    void StartGameplay()
    {
        Debug.Log("🎮 ¡A jugar!");
        startTime = Time.time;
        totalFlips = 0;
        pairsFound = 0;
    }
    
    // ========== PASO 3: DURANTE EL JUEGO ==========
    public void OnCardClicked()
    {
        totalFlips++;
        Debug.Log($"🃏 Carta {totalFlips}");
    }
    
    public void OnPairMatched()
    {
        pairsFound++;
        Debug.Log($"✨ Par {pairsFound}/{currentConfig.total_pairs}");
        
        if (pairsFound >= currentConfig.total_pairs) 
        {
            OnGameCompleted();
        }
    }
    
    // ========== PASO 4: FIN DEL JUEGO ==========
    void OnGameCompleted()
    {
        float elapsedTime = Time.time - startTime;
        
        Debug.Log("🎉 ¡Juego completado!");
        
        // Calcular accuracy
        int optimal = currentConfig.total_pairs * 2;
        float accuracy = (float)optimal / totalFlips * 100f;
        accuracy = Mathf.Min(accuracy, 100f);
        
        Debug.Log($"   Tiempo: {elapsedTime:F1}s");
        Debug.Log($"   Volteos: {totalFlips}");
        Debug.Log($"   Accuracy: {accuracy:F1}%");
        
        // Enviar resultados
        SubmitGameResults("completed", elapsedTime, accuracy);
    }
    
    // ========== PASO 5: ENVIAR RESULTADOS ==========
    void SubmitGameResults(string status, float time, float accuracy)
    {
        SubmitRequest request = new SubmitRequest {
            user_id = userId,
            session_data = new SessionData {
                completion_status = status,
                total_flips = totalFlips,
                pairs_found = pairsFound,
                total_pairs = currentConfig.total_pairs,
                elapsed_time = time,
                time_limit = currentConfig.time_limit,
                accuracy = accuracy
            }
        };
        
        Debug.Log("📤 Enviando resultados...");
        
        StartCoroutine(api.SubmitResults(request,
            response => {
                ShowAIFeedback(response.data.ai_analysis);
                
                // Actualizar config para próxima partida
                currentConfig = response.data.ai_analysis.next_session_config;
            },
            error => {
                Debug.LogError($"❌ Error: {error}");
            }
        ));
    }
    
    // ========== PASO 6: MOSTRAR FEEDBACK ==========
    void ShowAIFeedback(AIAnalysis ai)
    {
        Debug.Log("🤖 FEEDBACK DE IA:");
        Debug.Log($"   Score: {ai.performance_assessment.overall_score}/10");
        Debug.Log($"   Decisión: {ai.adjustment_decision}");
        Debug.Log($"   Nueva dificultad: {ai.next_session_config.difficulty_label}");
        Debug.Log($"   Razón: {ai.reason}");
        
        // Mostrar UI con el feedback
        string emotion = ai.performance_assessment.overall_score >= 8 ? "🌟" :
                        ai.performance_assessment.overall_score >= 5 ? "😊" : "💪";
        
        string message = $@"
        {emotion} {ai.reason}
        
        Tu puntuación: {ai.performance_assessment.overall_score}/10
        
        Próxima partida:
        • Nivel: {ai.next_session_config.difficulty_label}
        • Pares: {ai.next_session_config.total_pairs}
        • Grid: {ai.next_session_config.grid_size}
        ";
        
        // TODO: Mostrar en tu UI
        Debug.Log(message);
    }
    
    // ========== HELPERS ==========
    void CreateCards(int pairs, int rows, int cols) { /* Tu código */ }
    void ShowAllCards() { /* Tu código */ }
    void HideAllCards() { /* Tu código */ }
}
```

---

## 💻 Ejemplos PowerShell

### Test 1: Primera Partida

```powershell
# 1. Obtener configuración
Write-Host "`n===== OBTENIENDO CONFIGURACIÓN =====" -ForegroundColor Cyan
$config = Invoke-RestMethod -Uri "http://localhost:5000/memory-game/config/1" -Method Get
$config.data.current_config | Format-List

# 2. Jugar (simulado)
Write-Host "`n===== JUGANDO... =====" -ForegroundColor Yellow
Start-Sleep -Seconds 2

# 3. Enviar resultados
Write-Host "`n===== ENVIANDO RESULTADOS =====" -ForegroundColor Green
$body = @{
    user_id = 1
    session_data = @{
        completion_status = "completed"
        total_flips = 10
        pairs_found = 3
        total_pairs = 3
        elapsed_time = 48.5
        time_limit = 60
        accuracy = 60.0
    }
} | ConvertTo-Json -Depth 3

$result = Invoke-RestMethod -Uri "http://localhost:5000/memory-game/submit-results" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# 4. Mostrar análisis IA
Write-Host "`n===== ANÁLISIS DE IA =====" -ForegroundColor Magenta
$ai = $result.data.ai_analysis
Write-Host "Score: $($ai.performance_assessment.overall_score)/10" -ForegroundColor Yellow
Write-Host "Decisión: $($ai.adjustment_decision)" -ForegroundColor Cyan
Write-Host "Nueva dificultad: $($ai.next_session_config.difficulty_label)" -ForegroundColor Green
Write-Host "Razón: $($ai.reason)" -ForegroundColor White
```

### Test 2: Ver Estadísticas

```powershell
Write-Host "`n===== ESTADÍSTICAS DEL JUGADOR =====" -ForegroundColor Cyan

$stats = Invoke-RestMethod -Uri "http://localhost:5000/memory-game/stats/1" -Method Get

Write-Host "`nTotal partidas: $($stats.data.total_sessions)" -ForegroundColor Yellow
Write-Host "Completadas: $($stats.data.completed_sessions)" -ForegroundColor Green
Write-Host "Accuracy promedio: $($stats.data.average_accuracy.ToString('F1'))%" -ForegroundColor Cyan
Write-Host "Mejor tiempo: $($stats.data.best_time.ToString('F1'))s" -ForegroundColor Magenta

Write-Host "`n--- Últimas partidas ---" -ForegroundColor White
foreach ($session in $stats.data.recent_sessions) {
    $status = if ($session.completion_status -eq "completed") { "✅" } else { "❌" }
    Write-Host "$status $($session.difficulty_level) - Accuracy: $($session.accuracy.ToString('F0'))% - Tiempo: $($session.elapsed_time.ToString('F1'))s"
}
```

---

## 📋 Resumen de Uso

### Cuando INICIAR el juego:
```
GET /memory-game/config/{user_id}
→ Recibir configuración
→ Crear juego con esos parámetros
```

### Cuando TERMINAR el juego:
```
POST /memory-game/submit-results
→ Enviar resultados
→ Recibir análisis IA
→ Actualizar configuración local
→ Mostrar feedback al jugador
```

### Para mostrar ESTADÍSTICAS:
```
GET /memory-game/stats/{user_id}
→ Mostrar en pantalla de perfil
```

---

**¡APIs listas para usar!** 🚀  
Consulta `UNITY_INTEGRATION_GUIDE.md` para código completo de Unity.
