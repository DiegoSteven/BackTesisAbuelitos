"""Reset password for pedritococo"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db, app, bcrypt
from models.user import User

with app.app_context():
    user = User.query.filter_by(nombre='pedritococo').first()
    if user:
        new_password = "123"
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        print(f"Password for '{user.nombre}' reset to '{new_password}'")
    else:
        print("User 'pedritococo' not found.")
