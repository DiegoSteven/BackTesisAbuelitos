from locust import HttpUser, task, between, events
import random
import json
import time

# Custom metrics tracking
class MetricsTracker:
    def __init__(self):
        self.total_sessions = 0
        self.total_time = 0
        self.total_accuracy = 0

    def log_session(self, game_type, duration, accuracy):
        self.total_sessions += 1
        self.total_time += duration
        self.total_accuracy += accuracy
        # You could fire custom events here if needed

tracker = MetricsTracker()

class WebsiteUser(HttpUser):
    wait_time = between(2, 5)
    user_id = None
    
    def on_start(self):
        """
        Register a new user for each simulated user.
        """
        random_id = random.randint(1000, 999999)
        user_data = {
            "nombre": f"TestUser_{random_id}",
            "password": "password123",
            "edad": random.randint(60, 90),
            "genero": random.choice(["M", "F"])
        }
        
        try:
            response = self.client.post("/register", json=user_data)
            if response.status_code == 201:
                self.user_id = response.json()['user']['id']
            else:
                # Fallback login
                login_response = self.client.post("/login", json={
                    "nombre": user_data['nombre'],
                    "password": user_data['password']
                })
                if login_response.status_code == 200:
                    self.user_id = login_response.json()['user']['id']
        except Exception as e:
            print(f"Error registering user: {e}")

    # --- MEMORY GAME TASKS (Weight: 3) ---
    @task(3)
    def play_memory_game(self):
        if not self.user_id: return

        # 1. Get Config
        self.client.get(f"/memory-game/config/{self.user_id}", name="/memory-game/config")
        
        # Simulate thinking/playing time
        play_time = random.uniform(30.0, 90.0)
        time.sleep(1) # Short sleep to not block thread too long, real wait is 'wait_time'

        # 2. Submit Results (Simulating "Aciertos" and "Tiempo")
        # Indicator: Funciones cognitivas (Aciertos, Tiempo, Dificultad)
        pairs = 6
        accuracy = random.uniform(60.0, 100.0)
        
        session_data = {
            "user_id": self.user_id,
            "session_data": {
                "completion_status": "completed",
                "total_flips": int(pairs * 2 * (100/accuracy)), # Derive flips from accuracy
                "pairs_found": pairs,
                "total_pairs": pairs,
                "elapsed_time": play_time,
                "time_limit": 120,
                "accuracy": accuracy
            }
        }
        
        with self.client.post("/memory-game/submit-results", json=session_data, name="/memory-game/submit-results", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Verify we got a difficulty adjustment (Indicator: Nivel máximo)
                if 'data' in data and 'ai_analysis' in data['data']:
                    response.success()
                else:
                    response.failure("Missing AI analysis in response")
            else:
                response.failure(f"Failed with status {response.status_code}")

        # 3. Get Stats (Indicator: Verify data is saved)
        self.client.get(f"/memory-game/stats/{self.user_id}", name="/memory-game/stats")

    # --- TRAIN GAME TASKS (Weight: 3) ---
    @task(3)
    def play_train_game(self):
        if not self.user_id: return

        # 1. Get Config
        self.client.get(f"/train-game/config/{self.user_id}", name="/train-game/config")

        # Simulate play
        play_time = random.uniform(45.0, 120.0)
        
        # 2. Submit Results
        # Indicator: Funciones cognitivas
        accuracy = random.uniform(50.0, 100.0)
        
        session_data = {
            "user_id": self.user_id,
            "session_data": {
                "completion_status": "completed",
                "score": int(accuracy * 10),
                "mistakes": int((100 - accuracy) / 10),
                "duration": play_time,
                "level": 1 # Simplified
            }
        }
        
        self.client.post("/train-game/submit-results", json=session_data, name="/train-game/submit-results")
        
        # 3. Get Stats
        self.client.get(f"/train-game/stats/{self.user_id}", name="/train-game/stats")

    # --- ABECEDARIO GAME TASKS (Weight: 2) ---
    @task(2)
    def play_abecedario_game(self):
        if not self.user_id: return

        # 1. Get Next Challenge
        self.client.get(f"/abecedario/next-challenge/{self.user_id}", name="/abecedario/next-challenge")

        # Simulate play
        play_time = random.uniform(20.0, 60.0)
        
        # 2. Save Session
        # Indicator: Funciones cognitivas
        session_data = {
            "user_id": self.user_id,
            "palabra_objetivo": "TEST",
            "tiempo_resolucion": play_time,
            "cantidad_errores": random.randint(0, 3),
            "pistas_usadas": random.randint(0, 2),
            "completado": True,
            "nivel_dificultad": "facil"
        }
        
        self.client.post("/abecedario/session", json=session_data, name="/abecedario/session")
        
        # 3. Get Stats
        self.client.get(f"/abecedario/stats/{self.user_id}", name="/abecedario/stats")

