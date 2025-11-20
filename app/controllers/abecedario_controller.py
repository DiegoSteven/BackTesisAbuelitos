from flask import jsonify, request
from services.abecedario.abecedario_service import AbecedarioService
from services.abecedario.gemini_abecedario_service import GeminiService
from datetime import datetime, date

class AbecedarioController:
    
    gemini_service = GeminiService()
    
    @staticmethod
    def save_session():
        """
        Guarda una sesión completada con métricas
        POST /abecedario/session
        Body: user_id, palabra_objetivo, tiempo_resolucion, cantidad_errores, 
              pistas_usadas, completado, nivel_dificultad
        """
        data = request.get_json()
        
        required_fields = ['user_id', 'palabra_objetivo', 'tiempo_resolucion', 
                          'cantidad_errores', 'pistas_usadas', 'completado', 'nivel_dificultad']
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            return jsonify({
                'error': f'Faltan campos requeridos: {missing}',
                'campos_recibidos': list(data.keys())
            }), 400
        
        session, error = AbecedarioService.save_session(data['user_id'], data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Sesión guardada exitosamente',
            'session': session.to_dict()
        }), 201
    
    @staticmethod
    def get_next_challenge(user_id):
        """
        Obtiene el siguiente desafío generado por IA
        GET /abecedario/next-challenge/<user_id>
        """
        print(f"\n{'='*50}")
        print(f"[CONTROLLER] Solicitando desafío para user_id: {user_id}")
        print(f"{'='*50}")
        
        try:
            challenge, error = AbecedarioController.gemini_service.generate_next_challenge(user_id)
            
            if error:
                print(f"[CONTROLLER ERROR] {error}")
                return jsonify({'error': error}), 400
            
            print(f"[CONTROLLER SUCCESS] Desafío generado exitosamente")
            print(f"Palabra: {challenge.get('palabra_objetivo', 'N/A')}")
            print(f"Nivel: {challenge.get('nivel_dificultad', 'N/A')}")
            print(f"{'='*50}\n")
            
            return jsonify({
                'challenge': challenge,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            print(f"[CONTROLLER EXCEPTION] {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def get_performance_stats(user_id):
        """
        Obtiene estadísticas de rendimiento del usuario
        GET /abecedario/stats/<user_id>
        """
        try:
            stats, error = AbecedarioService.get_performance_stats(user_id)
            
            if error:
                return jsonify({'error': error}), 400
            
            return jsonify({
                'stats': stats
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def get_daily_summary(user_id):
        """
        Obtiene resumen del día actual
        GET /abecedario/daily-summary/<user_id>
        Query params: fecha (opcional, formato YYYY-MM-DD)
        """
        try:
            fecha_str = request.args.get('fecha')
            fecha = None
            
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
            
            summary, error = AbecedarioService.get_daily_summary(user_id, fecha)
            
            if error:
                return jsonify({'error': error}), 400
            
            return jsonify(summary), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def get_history(user_id):
        """
        Obtiene historial de sesiones
        GET /abecedario/history/<user_id>
        Query params: fecha_inicio, fecha_fin (opcional)
        """
        try:
            fecha_inicio_str = request.args.get('fecha_inicio')
            fecha_fin_str = request.args.get('fecha_fin')
            
            if fecha_inicio_str and fecha_fin_str:
                try:
                    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                    
                    sesiones, error = AbecedarioService.get_sessions_by_date_range(
                        user_id, fecha_inicio, fecha_fin
                    )
                except ValueError:
                    return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
            else:
                # Si no hay rango, obtener últimas 20 sesiones
                from models.abecedario import Abecedario
                sesiones = Abecedario.query.filter_by(
                    user_id=user_id
                ).order_by(Abecedario.created_at.desc()).limit(20).all()
                error = None
            
            if error:
                return jsonify({'error': error}), 400
            
            return jsonify({
                'sesiones': Abecedario.to_collection_dict(sesiones),
                'total': len(sesiones)
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def get_evolution_report(user_id):
        """
        Obtiene reporte de evolución agrupado por fecha y nivel
        GET /abecedario/evolution/<user_id>
        """
        try:
            report, error = AbecedarioService.get_evolution_report(user_id)
            
            if error:
                return jsonify({'error': error}), 400
            
            return jsonify(report), 200
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
