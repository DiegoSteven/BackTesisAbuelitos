"""
Script para listar usuarios y resetear todas las contraseñas a '123'
"""
from config.database import db, app
from models.user import User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def list_and_reset_passwords():
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
        
        user_list = []
        for user in users:
            print(f"{user.id:<5} {user.nombre:<30} {user.edad:<6} {user.genero:<10}")
            user_list.append({
                'id': user.id,
                'nombre': user.nombre,
                'edad': user.edad,
                'genero': user.genero
            })
        
        # Nueva contraseña hasheada
        new_password_hash = generate_password_hash('123')
        
        # Actualizar contraseñas usando SQL directo
        with db.engine.connect() as conn:
            for user_data in user_list:
                conn.execute(
                    text("UPDATE \"user\" SET password = :pwd WHERE id = :user_id"),
                    {"pwd": new_password_hash, "user_id": user_data['id']}
                )
            conn.commit()
        
        print("\n" + "=" * 80)
        print("✅ TODAS LAS CONTRASEÑAS HAN SIDO RESETEADAS A: 123")
        print("=" * 80)
        print(f"\nTotal de usuarios: {len(user_list)}")
        print("\nCredenciales de acceso:")
        print("-" * 80)
        for user_data in user_list:
            print(f"  ID: {user_data['id']}")
            print(f"  Nombre: {user_data['nombre']}")
            print(f"  Contraseña: 123")
            print(f"  Edad: {user_data['edad']} | Género: {user_data['genero']}")
            print()

if __name__ == '__main__':
    list_and_reset_passwords()
