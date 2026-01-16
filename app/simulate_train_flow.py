import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def print_step(step):
    print(f"\n{'='*50}")
    print(f"🚀 {step}")
    print(f"{'='*50}")

def simulate_flow():
    # 1. LOGIN
    print_step("PASO 1: Iniciar Sesión")
    login_payload = {
        "nombre": "PruebaTren",
        "password": "Tren123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_payload)
        if response.status_code != 200:
            print(f"❌ Error en login: {response.text}")
            return
        
        data = response.json()
        user = data['user']
        user_id = user['id']
        print(f"✅ Login exitoso. Usuario: {user['nombre']} (ID: {user_id})")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return

    # 2. OBTENER CONFIGURACIÓN INICIAL
    print_step("PASO 2: Obtener Configuración Inicial")
    response = requests.get(f"{BASE_URL}/train-game/config/{user_id}")
    if response.status_code == 200:
        config = response.json()['data']['current_config']
        print(f"✅ Configuración recibida:")
        print(json.dumps(config, indent=2))
    else:
        print(f"❌ Error obteniendo config: {response.text}")
        return

    # 3. JUGAR PARTIDA (SIMULACIÓN)
    # Simulamos una partida perfecta para forzar a la IA a subir la dificultad
    print_step("PASO 3: Simular Partida (Perfecta)")
    print("Simulando juego... (Enviando resultados)")
    
    results_payload = {
        "user_id": user_id,
        "session_data": {
            "correct_routing": 15,
            "wrong_routing": 0,
            "crash_count": 0,
            "total_spawned": 15,
            "completion_status": "completed",
            # Datos extra que podría usar la IA
            "train_speed": config['train_speed'],
            "color_count": config['color_count'],
            "spawn_rate": config['spawn_rate']
        }
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/train-game/submit-results", json=results_payload)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resultados enviados en {elapsed:.2f}s")
        print("🤖 Respuesta de la IA:")
        print(json.dumps(data, indent=2))
        
        if data.get('data', {}).get('ai_generated'):
            print("✨ ¡La IA Generativa (Gemini) procesó esta solicitud!")
    else:
        print(f"❌ Error enviando resultados: {response.text}")
        return

    # 4. VERIFICAR HISTORIAL
    print_step("PASO 4: Verificar Historial en Admin")
    response = requests.get(f"{BASE_URL}/admin/user-train-sessions/{user_id}")
    if response.status_code == 200:
        sessions = response.json()['sessions']
        print(f"✅ Historial recuperado. Total sesiones: {len(sessions)}")
        if sessions:
            last_session = sessions[0]
            print("📄 Última sesión registrada:")
            print(json.dumps(last_session, indent=2))
    else:
        print(f"❌ Error obteniendo historial: {response.text}")

if __name__ == "__main__":
    simulate_flow()
