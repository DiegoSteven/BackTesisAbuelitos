"""
Script para resetear contraseñas de usuarios a valores conocidos
"""
from config.database import db, app, bcrypt
from models.user import User

def reset_all_passwords():
    """Resetea todas las contraseñas a 'password123'"""
    with app.app_context():
        users = User.query.all()
        
        # Contraseña por defecto
        default_password = "password123"
        hashed = bcrypt.generate_password_hash(default_password).decode('utf-8')
        
        print(f"\n{'='*60}")
        print(f"RESET DE CONTRASEÑAS")
        print(f"{'='*60}")
        print(f"Contraseña por defecto: {default_password}")
        print(f"{'='*60}\n")
        
        for user in users:
            user.password = hashed
            print(f"✓ Usuario: {user.nombre} (ID: {user.id}) - Contraseña reseteada")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"Total usuarios actualizados: {len(users)}")
        print(f"{'='*60}\n")
        
        # Mostrar resumen
        print("RESUMEN DE ACCESO:")
        print("-" * 60)
        for user in users:
            print(f"Usuario: {user.nombre:15} | Password: {default_password}")
        print("-" * 60)

if __name__ == '__main__':
    reset_all_passwords()
