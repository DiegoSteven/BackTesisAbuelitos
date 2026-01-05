"""
Script para resetear el progreso de un usuario en Memory Game
"""
from sqlalchemy import create_engine, text

# Conexión directa a la base de datos
DATABASE_URL = 'postgresql://fazt:fastpassword@localhost:5433/abuelitosBack'
engine = create_engine(DATABASE_URL)

def reset_user_progress(user_id):
    """
    Borra todas las sesiones y configuración de un usuario
    para que vuelva a empezar desde cero (tutorial)
    """
    with engine.connect() as conn:
        # Borrar todas las sesiones del usuario
        result_sessions = conn.execute(
            text("DELETE FROM memory_game_sessions WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        sessions_deleted = result_sessions.rowcount
        
        # Borrar la configuración del usuario
        result_config = conn.execute(
            text("DELETE FROM memory_game_configs WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        config_deleted = result_config.rowcount
        
        # Commit
        conn.commit()
        
        print(f"✅ Usuario {user_id} reseteado:")
        print(f"   - Sesiones borradas: {sessions_deleted}")
        print(f"   - Configuración borrada: {config_deleted}")
        print(f"   - El usuario volverá a nivel TUTORIAL en la próxima partida")

if __name__ == '__main__':
    # Cambiar este número por el user_id que quieras resetear
    USER_ID = 1
    
    print(f"🔄 Reseteando usuario {USER_ID}...")
    reset_user_progress(USER_ID)
    print("🎉 ¡Listo! El usuario puede empezar de nuevo.")

