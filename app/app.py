from flask import Flask, send_from_directory
from config.database import db, app
from controllers.user_controller import UserController
from controllers.abecedario_controller import AbecedarioController
from flask_swagger_ui import get_swaggerui_blueprint
# Import models to ensure they are registered with SQLAlchemy
from models.user import User
from models.abecedario import Abecedario

# Create the database tables
with app.app_context():
    db.create_all()

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

if __name__ == '__main__':
    app.run(debug=True)