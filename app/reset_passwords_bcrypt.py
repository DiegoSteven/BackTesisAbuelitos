"""
Script para resetear contraseñas usando bcrypt (compatible con el login)
"""
from config.database import db, app, bcrypt
from sqlalchemy import text

def reset_passwords_bcrypt():
    with app.app_context():
        with db.engine.connect() as conn:
            # 1. Obtener todos los usuarios
            result = conn.execute(text('SELECT id, nombre FROM "user"'))
            users = result.fetchall()
            
            if not users:
                print("⚠️  No hay usuarios en la base de datos")
                return
            
            print(f"🔄 Reseteando contraseñas para {len(users)} usuarios usando bcrypt...")
            print("=" * 80)
            
            # 2. Generar nueva contraseña hasheada con bcrypt
            new_password = bcrypt.generate_password_hash('123').decode('utf-8')
            
            # 3. Actualizar cada usuario
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
            
            # 4. Mostrar lista final
            result = conn.execute(text('SELECT id, nombre, edad, genero FROM "user"'))
            users = result.fetchall()
            
            for user_id, nombre, edad, genero in users:
                print(f"\n  ID: {user_id}")
                print(f"  Nombre: {nombre}")
                print(f"  Contraseña: 123")
                print(f"  Edad: {edad} | Género: {genero}")

if __name__ == '__main__':
    reset_passwords_bcrypt()
