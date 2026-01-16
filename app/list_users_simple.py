"""
Script para listar usuarios
"""
from config.database import db, app
from models.user import User

def list_users():
    with app.app_context():
        # Obtener todos los usuarios
        users = User.query.all()
        
        print("=" * 80)
        print("USUARIOS EN LA BASE DE DATOS")
        print("=" * 80)
        
        if not users:
            print("No hay usuarios en la base de datos.")
            return
        
        print(f"\n{'ID':<5} {'Nombre':<30} {'Edad':<6} {'Género':<10}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<5} {user.nombre:<30} {user.edad:<6} {user.genero:<10}")
        
        print("\n" + "=" * 80)
        print(f"Total de usuarios: {len(users)}")
        print("=" * 80)
        print("\nNOTA: Las contraseñas están hasheadas en la base de datos.")
        print("Para probar el sistema, usa el nombre de usuario y la contraseña original")
        print("o ejecuta el script reset_passwords.py para cambiarlas a '123'")

if __name__ == '__main__':
    list_users()
