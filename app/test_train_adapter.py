"""
Pruebas del sistema adaptativo del Train Game
Verifica que las especificaciones de BACKEND_ADAPTACION_SPECS.md funcionen correctamente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db, app
from models.user import User
from models.train_game import TrainGameSession, TrainGameConfig
from services.train_game.train_ai_adapter import TrainAIAdapter

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_adapter():
    """Prueba directa del adaptador sin base de datos"""
    adapter = TrainAIAdapter()
    
    print_separator("PRUEBA 1: Timeout (DEBE bajar dificultad)")
    
    session_timeout = {
        'correct_routing': 8,  # Buena precisión pero...
        'wrong_routing': 2,
        'total_spawned': 10,
        'completion_status': 'timeout'  # ...no completó a tiempo
    }
    config = {'train_speed': 4.5, 'color_count': 4, 'spawn_rate': 5.0}
    
    result = adapter.analyze_performance(session_timeout, config)
    print(f"Sesión: {session_timeout}")
    print(f"Config actual: {config}")
    print(f"\nResultado:")
    print(f"  Decisión: {result['decision']}")
    print(f"  Razón: {result['reason']}")
    print(f"  Nueva velocidad: {result['next_config']['train_speed']}")
    print(f"  ✓ PASS" if result['decision'] == 'decrease_difficulty' else "  ✗ FAIL")
    
    print_separator("PRUEBA 2: Alta precisión (>=85%) - DEBE subir dificultad")
    
    session_good = {
        'correct_routing': 18,  # 90% precisión
        'wrong_routing': 2,
        'total_spawned': 20,
        'completion_status': 'completed'
    }
    config = {'train_speed': 3.5, 'color_count': 3, 'spawn_rate': 6.0}
    
    result = adapter.analyze_performance(session_good, config)
    print(f"Sesión: {session_good}")
    print(f"Precisión: 90%")
    print(f"\nResultado:")
    print(f"  Decisión: {result['decision']}")
    print(f"  Razón: {result['reason']}")
    print(f"  Nueva velocidad: {result['next_config']['train_speed']}")
    expected_speed = min(3.5 + 0.3, 6.0)
    print(f"  ✓ PASS" if result['decision'] == 'increase_difficulty' and result['next_config']['train_speed'] == expected_speed else "  ✗ FAIL")
    
    print_separator("PRUEBA 3: Baja precisión (<50%) - DEBE bajar dificultad")
    
    session_bad = {
        'correct_routing': 4,  # 40% precisión
        'wrong_routing': 6,
        'total_spawned': 10,
        'completion_status': 'completed'
    }
    config = {'train_speed': 5.0, 'color_count': 4, 'spawn_rate': 5.0}
    
    result = adapter.analyze_performance(session_bad, config)
    print(f"Sesión: {session_bad}")
    print(f"Precisión: 40%")
    print(f"\nResultado:")
    print(f"  Decisión: {result['decision']}")
    print(f"  Razón: {result['reason']}")
    print(f"  Nueva velocidad: {result['next_config']['train_speed']}")
    expected_speed = max(5.0 - 0.5, 3.0)
    print(f"  ✓ PASS" if result['decision'] == 'decrease_difficulty' and result['next_config']['train_speed'] == expected_speed else "  ✗ FAIL")
    
    print_separator("PRUEBA 4: Precisión media (50-85%) - DEBE mantener")
    
    session_medium = {
        'correct_routing': 7,  # 70% precisión
        'wrong_routing': 3,
        'total_spawned': 10,
        'completion_status': 'completed'
    }
    config = {'train_speed': 4.0, 'color_count': 3, 'spawn_rate': 5.5}
    
    result = adapter.analyze_performance(session_medium, config)
    print(f"Sesión: {session_medium}")
    print(f"Precisión: 70%")
    print(f"\nResultado:")
    print(f"  Decisión: {result['decision']}")
    print(f"  Razón: {result['reason']}")
    print(f"  Nueva velocidad: {result['next_config']['train_speed']}")
    print(f"  ✓ PASS" if result['decision'] == 'maintain' and result['next_config']['train_speed'] == 4.0 else "  ✗ FAIL")
    
    print_separator("PRUEBA 5: Límite mínimo de velocidad")
    
    session_bad2 = {
        'correct_routing': 2,
        'wrong_routing': 8,
        'total_spawned': 10,
        'completion_status': 'completed'
    }
    config = {'train_speed': 3.0, 'color_count': 3, 'spawn_rate': 6.0}  # Ya en mínimo
    
    result = adapter.analyze_performance(session_bad2, config)
    print(f"Velocidad actual: 3.0 (mínimo)")
    print(f"Precisión: 20% (mala)")
    print(f"\nResultado:")
    print(f"  Nueva velocidad: {result['next_config']['train_speed']}")
    print(f"  ✓ PASS (no bajó de 3.0)" if result['next_config']['train_speed'] >= 3.0 else "  ✗ FAIL")
    
    print_separator("PRUEBA 6: Límite máximo de velocidad")
    
    session_good2 = {
        'correct_routing': 19,
        'wrong_routing': 1,
        'total_spawned': 20,
        'completion_status': 'completed'
    }
    config = {'train_speed': 6.0, 'color_count': 5, 'spawn_rate': 3.0}  # Ya en máximo
    
    result = adapter.analyze_performance(session_good2, config)
    print(f"Velocidad actual: 6.0 (máximo)")
    print(f"Precisión: 95% (excelente)")
    print(f"\nResultado:")
    print(f"  Nueva velocidad: {result['next_config']['train_speed']}")
    print(f"  ✓ PASS (no subió de 6.0)" if result['next_config']['train_speed'] <= 6.0 else "  ✗ FAIL")

def test_with_database():
    """Prueba con la base de datos usando el usuario PruebaTren"""
    with app.app_context():
        print_separator("PRUEBA CON BASE DE DATOS")
        
        user = User.query.filter_by(nombre='PruebaTren').first()
        if not user:
            print("Usuario PruebaTren no encontrado")
            return
        
        print(f"Usuario: {user.nombre} (ID: {user.id})")
        
        # Obtener sesiones existentes
        sessions = TrainGameSession.query.filter_by(user_id=user.id).all()
        print(f"Sesiones existentes: {len(sessions)}")
        
        for s in sessions[:5]:  # Mostrar primeras 5
            print(f"  - Session {s.session_id}: speed={s.train_speed}, correct={s.correct_routing}, wrong={s.wrong_routing}")
        
        # Obtener o crear configuración
        config = TrainGameConfig.query.filter_by(user_id=user.id).first()
        if config:
            print(f"\nConfig actual: speed={config.train_speed}, colors={config.color_count}")
        else:
            print("\nNo hay configuración. Se usará la inicial.")

if __name__ == '__main__':
    print("\n" + "🚂"*30)
    print("   PRUEBAS DEL SISTEMA ADAPTATIVO - TRAIN GAME")
    print("🚂"*30)
    
    test_adapter()
    test_with_database()
    
    print_separator("RESUMEN")
    print("✓ Todas las pruebas del adaptador ejecutadas")
    print("✓ Verificar resultados arriba")
