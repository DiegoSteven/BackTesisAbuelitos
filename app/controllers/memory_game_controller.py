"""

Controlador de endpoints para el juego de memoria

"""

from flask import request, jsonify

from services.memory_game import MemoryGameService

from datetime import datetime

import logging

import json



# Configurar logging

logging.basicConfig(

    level=logging.INFO,

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    datefmt='%Y-%m-%d %H:%M:%S'

)

logger = logging.getLogger('MemoryGameController')



service = MemoryGameService()



class MemoryGameController:

    @staticmethod

    def get_config(user_id):

        """

        GET /memory-game/config/{user_id}

        Obtiene la configuraciÃ³n actual del usuario

        """

        logger.info("="*80)

        logger.info(f"ðŸ“¥ REQUEST | GET /memory-game/config/{user_id}")

        logger.info(f"   User ID: {user_id}")

        

        try:

            data = service.get_user_config(user_id)

            

            response = {

                'success': True,

                'data': data

            }

            

            logger.info(f"ðŸ“¤ RESPONSE | Status: 200 OK")

            logger.info(f"   Config: {data['current_config']}")

            logger.info(f"   First Time: {data['is_first_time']}")

            logger.info("="*80)

            

            return jsonify(response), 200

            

        except Exception as e:

            error_response = {

                'success': False,

                'error': str(e)

            }

            

            logger.error(f"âŒ ERROR | Status: 500")

            logger.error(f"   Error: {str(e)}")

            logger.error("="*80)

            

            return jsonify(error_response), 500



    @staticmethod

    def submit_results():

        """

        POST /memory-game/submit-results

        EnvÃ­a resultados de sesiÃ³n y obtiene nueva configuraciÃ³n con anÃ¡lisis de IA

        

        Body:

        {

            "user_id": 1,

            "session_data": {

                "completion_status": "completed",

                "total_flips": 12,

                "pairs_found": 3,

                "total_pairs": 3,

                "elapsed_time": 45.5,

                "time_limit": 60,

                "accuracy": 75.0

            }

        }

        """

        logger.info("="*80)

        logger.info("ðŸ“¥ REQUEST | POST /memory-game/submit-results")

        

        try:

            data = request.get_json()

            

            logger.info(f"   Received Data:")

            logger.info(f"   {json.dumps(data, indent=6)}")

            

            user_id = data.get('user_id')

            session_data = data.get('session_data')

            

            if not user_id or not session_data:

                error_response = {

                    'success': False,

                    'error': 'Missing user_id or session_data'

                }

                

                logger.warning(f"âš ï¸  VALIDATION ERROR | Status: 400")

                logger.warning(f"   Missing required fields")

                logger.warning("="*80)

                

                return jsonify(error_response), 400

            

            logger.info(f"   Processing session for User ID: {user_id}")

            logger.info(f"   Session Status: {session_data.get('completion_status')}")

            logger.info(f"   Accuracy: {session_data.get('accuracy')}%")

            logger.info(f"   Time: {session_data.get('elapsed_time')}s / {session_data.get('time_limit')}s")

            

            result = service.save_session_and_analyze(user_id, session_data)

            

            response = {

                'success': True,

                'data': result,

                'timestamp': datetime.utcnow().isoformat() + 'Z'

            }

            

            # Log AI Analysis

            ai_analysis = result.get('ai_analysis', {})

            logger.info(f"ðŸ“¤ RESPONSE | Status: 200 OK")

            logger.info(f"   Session Saved: ID={result.get('session_id')}")

            logger.info(f"   AI Score: {ai_analysis.get('performance_assessment', {}).get('overall_score')}/10")

            logger.info(f"   Decision: {ai_analysis.get('adjustment_decision')}")

            logger.info(f"   New Difficulty: {ai_analysis.get('next_session_config', {}).get('difficulty_label')}")

            logger.info(f"   Reason: {ai_analysis.get('reason')}")

            logger.info(f"   Response Data:")

            logger.info(f"   {json.dumps(result, indent=6)}")

            logger.info("="*80)

            

            return jsonify(response), 200

            

        except Exception as e:

            error_response = {

                'success': False,

                'error': str(e)

            }

            

            logger.error(f"âŒ ERROR | Status: 500")

            logger.error(f"   Error: {str(e)}")

            logger.error(f"   Traceback:", exc_info=True)

            logger.error("="*80)

            

            return jsonify(error_response), 500



    @staticmethod

    def get_stats(user_id):

        """

        GET /memory-game/stats/{user_id}

        Obtiene estadÃ­sticas del usuario

        """

        logger.info("="*80)

        logger.info(f"ðŸ“¥ REQUEST | GET /memory-game/stats/{user_id}")

        logger.info(f"   User ID: {user_id}")

        

        try:

            stats = service.get_user_stats(user_id)

            

            response = {

                'success': True,

                'data': stats

            }

            

            logger.info(f"ðŸ“¤ RESPONSE | Status: 200 OK")

            logger.info(f"   Total Sessions: {stats.get('total_sessions')}")

            logger.info(f"   Completed: {stats.get('completed_sessions')}")

            logger.info(f"   Avg Accuracy: {stats.get('average_accuracy'):.1f}%")

            logger.info(f"   Best Time: {stats.get('best_time')}s")

            logger.info("="*80)

            

            return jsonify(response), 200

            

        except Exception as e:

            error_response = {

                'success': False,

                'error': str(e)

            }

            

            logger.error(f"âŒ ERROR | Status: 500")

            logger.error(f"   Error: {str(e)}")

            logger.error("="*80)

            

            return jsonify(error_response), 500
    @staticmethod
    def reset_progress(user_id):
        """
        DELETE /memory-game/reset/{user_id}
        Resetea el progreso del usuario (borra sesiones y configuración)
        para que vuelva a empezar desde el nivel tutorial
        """
        logger.info("="*80)
        logger.info(f" REQUEST | DELETE /memory-game/reset/{user_id}")
        logger.info(f"   User ID: {user_id}")
        logger.warning(f"     RESETEANDO PROGRESO DEL USUARIO")
        
        try:
            result = service.reset_user_progress(user_id)
            
            response = {
                'success': True,
                'data': result
            }
            
            logger.info(f" RESPONSE | Status: 200 OK")
            logger.info(f"   Sessions Deleted: {result.get('sessions_deleted')}")
            logger.info(f"   Config Deleted: {result.get('config_deleted')}")
            logger.info(f"    Usuario reseteado a nivel TUTORIAL")
            logger.info("="*80)
            
            return jsonify(response), 200
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            logger.error(f" ERROR | Status: 500")
            logger.error(f"   Error: {str(e)}")
            logger.error("="*80)
            
            return jsonify(error_response), 500

