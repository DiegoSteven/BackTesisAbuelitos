from config.database import db, bcrypt
from models.user import User

class UserService:
    @staticmethod
    def create_user(user_data):
        try:
            # Verificar si el usuario ya existe
            if User.query.filter_by(nombre=user_data['nombre']).first():
                return None, "El usuario ya existe"

            # Hash del password
            hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
            
            # Crear nuevo usuario
            new_user = User(
                nombre=user_data['nombre'],
                password=hashed_password,
                edad=user_data['edad'],
                genero=user_data['genero']
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return new_user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def authenticate_user(nombre, password):
        try:
            user = User.query.filter_by(nombre=nombre).first()
            if user and bcrypt.check_password_hash(user.password, password):
                return user, None
            return None, "Credenciales inválidas"
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_all_users():
        try:
            users = User.query.all()
            return users, None
        except Exception as e:
            return None, str(e)
