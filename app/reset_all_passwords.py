"""
Script para ampliar el campo password y resetear contraseñas a '123'
"""
from config.database import db, app
from sqlalchemy import text
from werkzeug.security import generate_password_hash

def reset_all_passwords():
    with app.app_context():
        with db.engine.connect() as conn:
            # 1. Ampliar el campo password si es necesario
            print("📝 Ampliando campo password a 200 caracteres...")
            try:
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN password TYPE VARCHAR(200)'))
                conn.commit()
                print("✅ Campo password ampliado correctamente")
            except Exception as e:
                print(f"ℹ️  Campo ya tiene el tamaño adecuado: {e}")
            
            # 2. Obtener todos los usuarios
            result = conn.execute(text('SELECT id, nombre FROM "user"'))
            users = result.fetchall()
            
            if not users:
                print("⚠️  No hay usuarios en la base de datos")
                return
            
            print(f"\n🔄 Reseteando contraseñas para {len(users)} usuarios...")
            print("=" * 80)
            
            # 3. Generar nueva contraseña hasheada
            new_password = generate_password_hash('123')
            
            # 4. Actualizar cada usuario
            for user_id, nombre in users:
                conn.execute(
                    text('UPDATE "user" SET password = :pwd WHERE id = :uid'),
                    {"pwd": new_password, "uid": user_id}
                )
                print(f"  ✓ {nombre} (ID: {user_id})")
            
            conn.commit()
            
            print("=" * 80)
            print("✅ TODAS LAS CONTRASEÑAS HAN SIDO RESETEADAS A: 123")
            print("=" * 80)
            print("\nCredenciales de acceso:")
            print("-" * 80)
            
            # 5. Mostrar lista final
            result = conn.execute(text('SELECT id, nombre, edad, genero FROM "user"'))
            users = result.fetchall()
            
            for user_id, nombre, edad, genero in users:
                print(f"\n  ID: {user_id}")
                print(f"  Nombre: {nombre}")
                print(f"  Contraseña: 123")
                print(f"  Edad: {edad} | Género: {genero}")

if __name__ == '__main__':
    reset_all_passwords()
