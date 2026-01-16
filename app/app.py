from flask import Flask, send_from_directory
from config.database import db, app
from controllers.user_controller import UserController
from controllers.abecedario_controller import AbecedarioController
from controllers.paseo_controller import paseo_bp
from controllers.admin_controller import AdminController
from controllers.memory_game_controller import MemoryGameController
from controllers.train_game_controller import train_game_bp
from flask_swagger_ui import get_swaggerui_blueprint

# Import models to ensure they are registered with SQLAlchemy
from models.user import User
from models.abecedario import Abecedario
from models.paseo import PaseoSession
from models.memory_game import MemoryGameSession, MemoryGameConfig
from models.train_game import TrainGameSession, TrainGameConfig

# Create the database tables
# Create the database tables moved to main block

# Swagger UI Configuration
SWAGGER_URL = '/api/docs'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API Abuelitos - Juegos Cognitivos"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Register Paseo blueprint
app.register_blueprint(paseo_bp, url_prefix='/paseo')

# Register Train Game blueprint
app.register_blueprint(train_game_bp, url_prefix='/train-game')

# Ruta para servir el archivo swagger.json
@app.route('/swagger.json')
def swagger_spec():
    import os
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory, 'swagger.json')

# User Routes
app.add_url_rule('/users', 'get_users', UserController.get_all, methods=['GET'])
app.add_url_rule('/register', 'register', UserController.register, methods=['POST'])
app.add_url_rule('/login', 'login', UserController.login, methods=['POST'])

# Abecedario Routes
app.add_url_rule('/abecedario/session', 'save_abecedario_session', AbecedarioController.save_session, methods=['POST'])
app.add_url_rule('/abecedario/next-challenge/<int:user_id>', 'get_next_challenge', AbecedarioController.get_next_challenge, methods=['GET'])
app.add_url_rule('/abecedario/stats/<int:user_id>', 'get_abecedario_stats', AbecedarioController.get_performance_stats, methods=['GET'])
app.add_url_rule('/abecedario/daily-summary/<int:user_id>', 'get_daily_summary', AbecedarioController.get_daily_summary, methods=['GET'])
app.add_url_rule('/abecedario/history/<int:user_id>', 'get_abecedario_history', AbecedarioController.get_history, methods=['GET'])
app.add_url_rule('/abecedario/evolution/<int:user_id>', 'get_evolution_report', AbecedarioController.get_evolution_report, methods=['GET'])
app.add_url_rule('/abecedario/final-stats/<int:user_id>', 'get_final_stats', AbecedarioController.get_final_stats, methods=['GET'])

# Memory Game Routes
app.add_url_rule('/memory-game/config/<int:user_id>', 'get_memory_config', MemoryGameController.get_config, methods=['GET'])
app.add_url_rule('/memory-game/submit-results', 'submit_memory_results', MemoryGameController.submit_results, methods=['POST'])
app.add_url_rule('/memory-game/stats/<int:user_id>', 'get_memory_stats', MemoryGameController.get_stats, methods=['GET'])
app.add_url_rule('/memory-game/reset/<int:user_id>', 'reset_memory_progress', MemoryGameController.reset_progress, methods=['DELETE'])

# Admin Routes
app.add_url_rule('/admin/memory-sessions', 'admin_memory_sessions', AdminController.get_memory_sessions, methods=['GET'])
app.add_url_rule('/admin/abecedario-sessions', 'admin_abecedario_sessions', AdminController.get_abecedario_sessions, methods=['GET'])
app.add_url_rule('/admin/paseo-sessions', 'admin_paseo_sessions', AdminController.get_paseo_sessions, methods=['GET'])
app.add_url_rule('/admin/memory-configs', 'admin_memory_configs', AdminController.get_memory_configs, methods=['GET'])
app.add_url_rule('/admin/stats', 'admin_stats', AdminController.get_admin_stats, methods=['GET'])
app.add_url_rule('/admin/user-stats/<int:user_id>', 'admin_user_stats', AdminController.get_user_stats_all_games, methods=['GET'])
app.add_url_rule('/admin/user-memory-sessions/<int:user_id>', 'admin_user_memory_sessions', AdminController.get_user_memory_sessions, methods=['GET'])
app.add_url_rule('/admin/user-abecedario-sessions/<int:user_id>', 'admin_user_abecedario_sessions', AdminController.get_user_abecedario_sessions, methods=['GET'])
app.add_url_rule('/admin/user-paseo-sessions/<int:user_id>', 'admin_user_paseo_sessions', AdminController.get_user_paseo_sessions, methods=['GET'])
app.add_url_rule('/admin/train-sessions', 'admin_train_sessions', AdminController.get_train_sessions, methods=['GET'])
app.add_url_rule('/admin/user-train-sessions/<int:user_id>', 'admin_user_train_sessions', AdminController.get_user_train_sessions, methods=['GET'])
app.add_url_rule('/admin/train-configs', 'admin_train_configs', AdminController.get_train_configs, methods=['GET'])

# Ruta para servir el dashboard
@app.route('/admin')
def admin_dashboard():
    import os
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_from_directory(directory, 'admin_dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
