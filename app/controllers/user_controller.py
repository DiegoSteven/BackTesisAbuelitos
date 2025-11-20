from flask import jsonify, request
from services.user_service import UserService
from models.user import User

class UserController:
    @staticmethod
    def register():
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['nombre', 'password', 'edad', 'genero']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        # Crear usuario usando el servicio
        user, error = UserService.create_user(data)
        
        if error:
            return jsonify({'error': error}), 400
            
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict()
        }), 201

    @staticmethod
    def login():
        data = request.get_json()
        
        # Validar campos requeridos
        if not data or 'nombre' not in data or 'password' not in data:
            return jsonify({'error': 'Se requiere nombre y contraseña'}), 400
        
        # Autenticar usuario usando el servicio
        user, error = UserService.authenticate_user(data['nombre'], data['password'])
        
        if error:
            return jsonify({'error': error}), 401
            
        return jsonify({
            'message': 'Login exitoso',
            'user': user.to_dict()
        }), 200
    
    @staticmethod
    def get_all():
        users, error = UserService.get_all_users()
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'users': User.to_collection_dict(users)
        }), 200

