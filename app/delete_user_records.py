"""Borrar registros del usuario ID 19"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db, app
from sqlalchemy import text

USER_ID = 19

with app.app_context():
    print(f"Borrando registros del usuario ID {USER_ID}...")
    
    # Borrar sesiones de Train Game
    result = db.session.execute(text(f"DELETE FROM train_game_sessions WHERE user_id = {USER_ID}"))
    print(f"  ✓ Train Game Sessions eliminadas: {result.rowcount}")
    
    # Borrar config de Train Game
    result = db.session.execute(text(f"DELETE FROM train_game_configs WHERE user_id = {USER_ID}"))
    print(f"  ✓ Train Game Configs eliminadas: {result.rowcount}")
    
    # Borrar sesiones de Memory Game
    result = db.session.execute(text(f"DELETE FROM memory_game_sessions WHERE user_id = {USER_ID}"))
    print(f"  ✓ Memory Game Sessions eliminadas: {result.rowcount}")
    
    # Borrar config de Memory Game
    result = db.session.execute(text(f"DELETE FROM memory_game_configs WHERE user_id = {USER_ID}"))
    print(f"  ✓ Memory Game Configs eliminadas: {result.rowcount}")
    
    # Borrar Abecedario (nombre correcto: word_game_session)
    result = db.session.execute(text(f"DELETE FROM word_game_session WHERE user_id = {USER_ID}"))
    print(f"  ✓ Abecedario Sessions eliminadas: {result.rowcount}")
    
    # Borrar Paseo (nombre correcto: paseo_session)
    result = db.session.execute(text(f"DELETE FROM paseo_session WHERE user_id = {USER_ID}"))
    print(f"  ✓ Paseo Sessions eliminadas: {result.rowcount}")
    
    db.session.commit()
    
    print(f"\n✓ Todos los registros del usuario {USER_ID} han sido eliminados.")
