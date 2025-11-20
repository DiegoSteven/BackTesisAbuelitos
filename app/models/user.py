from config.database import db
from flask import jsonify

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'edad': self.edad,
            'genero': self.genero
        }

    @staticmethod
    def to_collection_dict(users):
        return [user.to_dict() for user in users]