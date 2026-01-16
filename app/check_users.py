"""
Script para verificar usuarios en la base de datos
"""
from config.database import db, app
from sqlalchemy import text

def check_users():
    with app.app_context():
        with db.engine.connect() as conn:
            # Consultar directamente la tabla user
            result = conn.execute(text('SELECT id, nombre, edad, genero FROM "user" ORDER BY id'))
            users = result.fetchall()
            
            print("=" * 80)
            print("USUARIOS EN LA BASE DE DATOS (Consulta Directa)")
            print("=" * 80)
            
            if not users:
                print("\n⚠️  No hay usuarios en la base de datos.")
                print("\nPara crear usuarios de prueba, ejecuta: python app/create_test_user.py")
                return
            
            print(f"\n{'ID':<5} {'Nombre':<30} {'Edad':<6} {'Género':<10}")
            print("-" * 80)
            
            for user in users:
                user_id, nombre, edad, genero = user
                print(f"{user_id:<5} {nombre:<30} {edad:<6} {genero:<10}")
            
            print("\n" + "=" * 80)
            print(f"✅ Total de usuarios encontrados: {len(users)}")
            print("=" * 80)
            
            # Verificar estructura del campo password
            result = conn.execute(text('SELECT id, nombre, LENGTH(password) as pwd_length FROM "user" LIMIT 5'))
            pwd_info = result.fetchall()
            
            print("\nInformación de contraseñas (primeros 5 usuarios):")
            print("-" * 80)
            for user_id, nombre, pwd_length in pwd_info:
                print(f"  ID {user_id} ({nombre}): Password length = {pwd_length} caracteres")
            
            print("\n💡 Todas las contraseñas están hasheadas con bcrypt.")
            print("   Para resetear a '123', necesitamos ajustar el tamaño del campo.")

if __name__ == '__main__':
    check_users()
