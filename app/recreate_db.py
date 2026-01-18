"""
Script para recrear la base de datos desde cero
"""
from config.database import db, app
from models.user import User
from models.abecedario import Abecedario
from models.paseo import PaseoSession
from models.memory_game import MemoryGameSession, MemoryGameConfig
from models.train_game import TrainGameSession
from sqlalchemy import text

def recreate_database():
    with app.app_context():
        # Eliminar todas las tablas existentes usando CASCADE para manejar dependencias
        # Primero obtenemos todas las tablas
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Eliminando {len(tables)} tablas...")
        # Eliminar cada tabla con CASCADE
        with db.engine.connect() as conn:
            for table in tables:
                try:
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    conn.commit()
                    print(f"  ✅ Tabla '{table}' eliminada")
                except Exception as e:
                    print(f"  ⚠️  Error eliminando '{table}': {e}")
        
        print("Tablas eliminadas exitosamente")
        
        # Crear todas las tablas nuevamente
        db.create_all()
        print("Tablas creadas exitosamente")
        
        # Verificar que las tablas se crearon
        print("\nTablas en la base de datos:")
        for table_name in db.metadata.tables.keys():
            print(f"  ✅ {table_name}")

if __name__ == "__main__":
    recreate_database()