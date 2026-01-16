import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db, app

with app.app_context():
    # Usar text() para SQL raw
    from sqlalchemy import text
    
    result1 = db.session.execute(text("UPDATE train_game_sessions SET train_speed = 3.0 WHERE train_speed IS NULL"))
    result2 = db.session.execute(text("UPDATE train_game_sessions SET color_count = 3 WHERE color_count IS NULL"))
    result3 = db.session.execute(text("UPDATE train_game_sessions SET spawn_rate = 5.0 WHERE spawn_rate IS NULL"))
    result4 = db.session.execute(text("UPDATE train_game_sessions SET completion_status = 'completed' WHERE completion_status IS NULL"))
    
    db.session.commit()
    
    print("Datos de train_game_sessions actualizados correctamente")
    
    # Verificar
    result = db.session.execute(text("SELECT session_id, user_id, train_speed, color_count, correct_routing, wrong_routing FROM train_game_sessions"))
    print("\nSesiones actuales:")
    for row in result:
        print(f"  Session {row[0]}: user={row[1]}, speed={row[2]}, colors={row[3]}, correct={row[4]}, wrong={row[5]}")
