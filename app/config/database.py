from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Cargar variables de entorno PRIMERO
load_dotenv()

import os

# Get the directory where database.py is located
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_folder = os.path.join(base_dir, 'static')

app = Flask(__name__, static_folder=static_folder, static_url_path='/static')

# Configurar DB según entorno
if os.environ.get('FLASK_ENV') == 'testing':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
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