"""

Servicio de lÃ³gica de negocio para el juego de memoria

"""

from datetime import datetime

from config.database import db

from models.memory_game import MemoryGameSession, MemoryGameConfig

from .ai_adapter_service import AIAdapterService



class MemoryGameService:

    def __init__(self):

        self.ai_adapter = AIAdapterService()

    

    def get_user_config(self, user_id: int) -> dict:

        """

        Obtiene la configuraciÃ³n actual del usuario.

        Si no existe, crea una con valores por defecto.

        """

        config = MemoryGameConfig.query.filter_by(user_id=user_id).first()

        

        if not config:

            # Crear configuraciÃ³n por defecto

            config = MemoryGameConfig(user_id=user_id)

            db.session.add(config)

            db.session.commit()

            is_first_time = True

        else:

            is_first_time = False

        

        return {

            'user_id': user_id,

            'current_config': config.to_dict(),

            'is_first_time': is_first_time,

            'last_updated': config.last_updated.isoformat()

        }

    

    def save_session_and_analyze(self, user_id: int, session_data: dict) -> dict:

        """

        Guarda la sesiÃ³n y usa IA para generar nueva configuraciÃ³n

        """

        # 1. Obtener configuraciÃ³n actual

        current_config = MemoryGameConfig.query.filter_by(user_id=user_id).first()

        if not current_config:

            current_config = MemoryGameConfig(user_id=user_id)

            db.session.add(current_config)

            db.session.commit()

        

        # 2. Guardar sesiÃ³n

        session = MemoryGameSession(

            user_id=user_id,

            difficulty_level=current_config.difficulty_label,

            total_pairs=session_data.get('total_pairs'),

            grid_size=current_config.grid_size,

            total_flips=session_data.get('total_flips'),

            pairs_found=session_data.get('pairs_found'),

            elapsed_time_seconds=session_data.get('elapsed_time'),

            completion_status=session_data.get('completion_status'),

            accuracy_percentage=session_data.get('accuracy'),

            finished_at=datetime.utcnow()

        )

        

        # Calcular memory score simple

        session.memory_score = self._calculate_memory_score(session_data)

        

        db.session.add(session)

        db.session.commit()

        

        # 3. Analizar con IA y obtener nueva configuraciÃ³n

        ai_analysis = self.ai_adapter.analyze_and_recommend(

            session_data, 

            current_config.difficulty_label

        )

        

        # 4. Actualizar configuraciÃ³n del usuario

        new_config = ai_analysis['next_session_config']

        current_config.total_pairs = new_config['total_pairs']

        current_config.grid_size = new_config['grid_size']

        current_config.time_limit = new_config['time_limit']

        current_config.memorization_time = new_config['memorization_time']

        current_config.difficulty_label = new_config['difficulty_label']

        

        db.session.commit()

        

        return {

            'session_saved': True,

            'session_id': session.session_id,

            'ai_analysis': ai_analysis

        }

    

    def _calculate_memory_score(self, session_data: dict) -> float:

        """

        Calcula un score de memoria (0-10)

        """

        if session_data.get('completion_status') != 'completed':

            return 0.0

        

        accuracy = session_data.get('accuracy', 0)

        return min(accuracy / 10, 10)

    

    def get_user_stats(self, user_id: int) -> dict:

        """

        Obtiene estadÃ­sticas del usuario

        """

        sessions = MemoryGameSession.query.filter_by(user_id=user_id).all()

        

        if not sessions:

            return {

                'total_sessions': 0,

                'completed_sessions': 0,

                'average_accuracy': 0,

                'best_time': None

            }

        

        completed = [s for s in sessions if s.completion_status == 'completed']

        

        return {

            'total_sessions': len(sessions),

            'completed_sessions': len(completed),

            'average_accuracy': sum(s.accuracy_percentage or 0 for s in completed) / len(completed) if completed else 0,

            'best_time': min(s.elapsed_time_seconds for s in completed) if completed else None,

            'recent_sessions': [s.to_dict() for s in sessions[-5:]]

        }
    def reset_user_progress(self, user_id: int) -> dict:
        """
        Resetea el progreso del usuario eliminando sesiones y configuración
        """
        # Borrar sesiones
        sessions_deleted = MemoryGameSession.query.filter_by(user_id=user_id).delete()
        
        # Borrar configuración
        config_deleted = MemoryGameConfig.query.filter_by(user_id=user_id).delete()
        
        # Commit
        db.session.commit()
        
        return {
            'sessions_deleted': sessions_deleted,
            'config_deleted': config_deleted,
            'message': f'Usuario {user_id} reseteado a nivel tutorial'
        }

