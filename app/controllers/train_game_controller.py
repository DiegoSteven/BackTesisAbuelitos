from flask import Blueprint, request, jsonify
from services.train_game.train_game_service import TrainGameService
import logging
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('TrainGameController')

train_game_bp = Blueprint('train_game', __name__)
service = TrainGameService()

@train_game_bp.route('/config/<int:user_id>', methods=['GET'])
def get_config(user_id):
    """Obtiene la configuración actual para el usuario"""
    logger.info("="*80)
    logger.info(f"📥 REQUEST | GET /train-game/config/{user_id}")
    
    try:
        response = service.get_config(user_id)
        
        logger.info(f"📤 RESPONSE | Status: 200 OK")
        logger.info(f"   Config: {response['data']['current_config']}")
        logger.info("="*80)
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"❌ ERROR | Status: 500")
        logger.error(f"   Error: {str(e)}")
        logger.error("="*80)
        return jsonify({"success": False, "error": str(e)}), 500

@train_game_bp.route('/submit-results', methods=['POST'])
def submit_results():
    """Recibe resultados y devuelve análisis de IA"""
    logger.info("="*80)
    logger.info("📥 REQUEST | POST /train-game/submit-results")
    
    try:
        # Log raw data for debugging
        raw_data = request.get_data(as_text=True)
        logger.info(f"   📥 Raw Payload: {raw_data}")

        data = request.json
        logger.info(f"   Parsed JSON: {json.dumps(data)}")
        
        user_id = data.get('user_id')
        session_data = data.get('session_data')
        
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Session Data: {json.dumps(session_data)}")
        
        if not user_id or not session_data:
            logger.warning("⚠️ VALIDATION ERROR | Missing user_id or session_data")
            return jsonify({"success": False, "error": "Missing user_id or session_data"}), 400
            
        response = service.submit_results(user_id, session_data)
        
        ai_analysis = response['data']['ai_analysis']
        logger.info(f"📤 RESPONSE | Status: 200 OK")
        logger.info(f"   Decision: {ai_analysis.get('decision')}")
        logger.info(f"   Reason: {ai_analysis.get('reason')}")
        logger.info("="*80)
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"❌ ERROR | Status: 500")
        logger.error(f"   Error: {str(e)}")
        logger.error("="*80)
        return jsonify({"success": False, "error": str(e)}), 500

@train_game_bp.route('/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    """Obtiene estadísticas del usuario"""
    logger.info("="*80)
    logger.info(f"📥 REQUEST | GET /train-game/stats/{user_id}")
    
    try:
        response = service.get_stats(user_id)
        
        logger.info(f"📤 RESPONSE | Status: 200 OK")
        logger.info(f"   Stats: {response['data']}")
        logger.info("="*80)
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"❌ ERROR | Status: 500")
        logger.error(f"   Error: {str(e)}")
        logger.error("="*80)
        return jsonify({"success": False, "error": str(e)}), 500
