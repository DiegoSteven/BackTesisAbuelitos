"""Query user pedritococo"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db, app
from models.user import User

with app.app_context():
    user = User.query.filter_by(nombre='pedritococo').first()
    if user:
        print(f"User found: {user.nombre}")
        print(f"ID: {user.id}")
        print(f"Password Hash: {user.password}")
    else:
        print("User 'pedritococo' not found.")
