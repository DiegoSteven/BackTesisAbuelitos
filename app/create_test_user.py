from app import app
from config.database import db, bcrypt
from models.user import User

def create_user():
    with app.app_context():
        # Check if user exists
        existing_user = User.query.filter_by(nombre="PruebaTren").first()
        if existing_user:
            print("User 'PruebaTren' already exists.")
            return

        hashed_password = bcrypt.generate_password_hash("Tren123").decode('utf-8')
        new_user = User(
            nombre="PruebaTren",
            password=hashed_password,
            edad=65,
            genero="M"
        )
        db.session.add(new_user)
        db.session.commit()
        print("User 'PruebaTren' created successfully.")

if __name__ == "__main__":
    create_user()
