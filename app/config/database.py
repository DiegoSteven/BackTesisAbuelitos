from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fazt:fastpassword@localhost:5433/abuelitosBack'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Permite todas las origins en desarrollo
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)