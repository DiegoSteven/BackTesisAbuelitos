"""
Script para recrear la base de datos desde cero
"""
from config.database import db, app
from models.user import User
from models.abecedario import Abecedario

def recreate_database():
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        print("Tablas eliminadas exitosamente")
        
        # Crear todas las tablas nuevamente
        db.create_all()
        print("Tablas creadas exitosamente")
        
        # Verificar que las tablas se crearon
        print("Tablas en la base de datos:")
        for table_name in db.metadata.tables.keys():
            print(f"- {table_name}")

if __name__ == "__main__":
    recreate_database()