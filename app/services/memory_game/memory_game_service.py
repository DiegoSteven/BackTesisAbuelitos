"""

Servicio de lógica de negocio para el juego de memoria

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

        Obtiene la configuración actual del usuario.

        Si no existe, crea una con valores por defecto.

        """

        config = MemoryGameConfig.query.filter_by(user_id=user_id).first()

        

        if not config:

            # Crear configuración por defecto

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

        Guarda la sesión y usa IA para generar nueva configuración

        """

        # 1. Obtener configuración actual

        current_config = MemoryGameConfig.query.filter_by(user_id=user_id).first()

        if not current_config:

            current_config = MemoryGameConfig(user_id=user_id)

            db.session.add(current_config)

            db.session.commit()

        

        # 2. Guardar sesión

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

        

        # 3. Analizar con IA y obtener nueva configuración

        ai_result = self.ai_adapter.analyze_and_recommend(

            user_id, 

            current_config,

            session

        )

        

        # 4. Guardar métricas de IA en la sesión (para seguimiento del terapeuta)

        ai_analysis = ai_result['ai_analysis']

        assessment = ai_analysis.get('performance_assessment', {})

        

        session.ai_adjustment_decision = ai_analysis.get('adjustment_decision')

        session.ai_reason = ai_analysis.get('reason')

        session.ai_memory_assessment = assessment.get('memory_retention')

        session.ai_speed_assessment = assessment.get('speed')

        session.ai_accuracy_assessment = assessment.get('accuracy')

        session.ai_overall_score = assessment.get('overall_score')

        

        # 5. Actualizar configuración del usuario

        new_config_data = ai_analysis['next_session_config']
        ai_decision = ai_analysis.get('adjustment_decision', 'maintain')

        

        # ✅ CORRECCIÓN: Usar .get() o acceso directo seguro

        current_config.difficulty_label = new_config_data.get('difficulty_label', current_config.difficulty_label)

        current_config.total_pairs = new_config_data.get('total_pairs', current_config.total_pairs)

        current_config.grid_size = new_config_data.get('grid_size', '2x3')

        current_config.time_limit = new_config_data.get('time_limit', 60)

        current_config.memorization_time = new_config_data.get('memorization_time', 5)

        
        # 6. Actualizar contador de sesiones consecutivas en MAINTAIN
        if ai_decision == 'maintain':
            current_config.consecutive_maintains = getattr(current_config, 'consecutive_maintains', 0) + 1
        else:
            # Si sube o baja de nivel, resetear el contador
            current_config.consecutive_maintains = 0

        

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

        Obtiene estadísticas del usuario

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
