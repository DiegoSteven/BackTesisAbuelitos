"""Consultar registros del usuario ID 19"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db, app
from sqlalchemy import text

USER_ID = 19

with app.app_context():
    print(f"=== Registros del usuario ID {USER_ID} ===\n")
    
    # Train Game Sessions
    result = db.session.execute(text(f"SELECT COUNT(*) FROM train_game_sessions WHERE user_id = {USER_ID}"))
    count = result.fetchone()[0]
    print(f"Train Game Sessions: {count}")
    
    # Train Game Configs
    result = db.session.execute(text(f"SELECT COUNT(*) FROM train_game_configs WHERE user_id = {USER_ID}"))
    count = result.fetchone()[0]
    print(f"Train Game Configs: {count}")
    
    # Memory Game Sessions
    result = db.session.execute(text(f"SELECT COUNT(*) FROM memory_game_sessions WHERE user_id = {USER_ID}"))
    count = result.fetchone()[0]
    print(f"Memory Game Sessions: {count}")
    
    # Memory Game Configs
    result = db.session.execute(text(f"SELECT COUNT(*) FROM memory_game_configs WHERE user_id = {USER_ID}"))
    count = result.fetchone()[0]
    print(f"Memory Game Configs: {count}")
    
    # Abecedario (word_game_session)
    result = db.session.execute(text(f"SELECT COUNT(*) FROM word_game_session WHERE user_id = {USER_ID}"))
    count = result.fetchone()[0]
    print(f"Abecedario Sessions: {count}")
    
    # Paseo (paseo_session)
    result = db.session.execute(text(f"SELECT COUNT(*) FROM paseo_session WHERE user_id = {USER_ID}"))
    count = result.fetchone()[0]
    print(f"Paseo Sessions: {count}")
    
    print("\n=== Fin de la consulta ===")
