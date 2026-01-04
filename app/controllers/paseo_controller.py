from flask import Blueprint, request, jsonify
from services.paseo.paseo_service import PaseoService
from services.paseo.gemini_paseo_service import GeminiPaseoService

paseo_bp = Blueprint('paseo', __name__, url_prefix='/paseo')
gemini_service = GeminiPaseoService()

@paseo_bp.route('/start-session', methods=['POST'])
def start_session():
    """
    Inicia sesión - Solo para PRIMERA vez (decide si TUTORIAL o nivel con IA)
    Después de eso, usar /get-next-level
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({'success': False, 'error': 'user_id requerido'}), 400
        
        user_id = data['user_id']
        
        # Obtener última sesión
        ultima_sesion, _ = PaseoService.get_ultima_sesion(user_id)
        
        # Decidir nivel inicial
        if not ultima_sesion:
            # Usuario NUEVO → TUTORIAL
            nivel = "tutorial"
            print(f"[PASEO] Usuario nuevo → TUTORIAL")
        else:
            # Ya jugó antes → IA decide basado en rendimiento
            nivel = gemini_service.decidir_nivel_inicial(user_id)
            print(f"[PASEO] IA decide nivel: {nivel}")
        
        # Generar plan SIN IA
        plan = gemini_service._plan_nivel_sin_ia(nivel)
        
        meta = plan.get('meta_aciertos', 5)
        print(f"[PASEO] Sesión planificada user {user_id}: {nivel.upper()}, meta: {meta} aciertos")
        
        return jsonify({
            'success': True,
            'plan': plan
        }), 200
        
    except Exception as e:
        print(f"[PASEO API ERROR] start_session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@paseo_bp.route('/get-next-level', methods=['POST'])
def get_next_level():
    """Devuelve siguiente nivel SIN IA - solo lógica simple"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id requerido'}), 400
        
        # Obtener última sesión
        ultima_sesion, error = PaseoService.get_ultima_sesion(user_id)
        
        if error:
            return jsonify({'success': False, 'error': error}), 500
        
        # Decidir siguiente nivel SIN IA
        if not ultima_sesion:
            siguiente_nivel = "tutorial"
        elif ultima_sesion['nivel'] == 'tutorial':
            siguiente_nivel = "facil"
        elif ultima_sesion['nivel'] == 'facil' and ultima_sesion['resultado'] == 'victoria':
            siguiente_nivel = "intermedio"
        elif ultima_sesion['nivel'] == 'intermedio' and ultima_sesion['resultado'] == 'victoria':
            siguiente_nivel = "dificil"
        else:
            siguiente_nivel = ultima_sesion['nivel']
        
        # Generar plan sin IA
        plan = gemini_service._plan_nivel_sin_ia(siguiente_nivel)
        
        print(f"[PASEO] Siguiente nivel SIN IA: {siguiente_nivel}")
        return jsonify({'success': True, 'plan': plan}), 200
        
    except Exception as e:
        print(f"[PASEO API ERROR] get_next_level: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@paseo_bp.route('/save-session', methods=['POST'])
def save_session():
    """
    Guarda nivel jugado (FACIL/INTERMEDIO/DIFICIL/TUTORIAL)
    Simplificado siguiendo patrón de Abecedario
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({'success': False, 'error': 'user_id requerido'}), 400
        
        user_id = data['user_id']
        
        # Guardar sesión
        sesion, error = PaseoService.save_session(user_id, data)
        
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        return jsonify({
            'success': True,
            'message': f"Nivel {data.get('nivel_dificultad')} guardado",
            'cambio_nivel': sesion.cambio_nivel
        }), 200
        
    except Exception as e:
        print(f"[PASEO API ERROR] save_session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@paseo_bp.route('/report-metrics', methods=['POST'])
def report_metrics():
    """Guarda métricas intermedias (cada 30s) - Solo para monitoreo"""
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({'success': False, 'error': 'user_id requerido'}), 400
        
        # Solo confirmar recepción - no guardamos métricas intermedias
        return jsonify({
            'success': True,
            'requiere_ajuste': False
        }), 200
        
    except Exception as e:
        print(f"[PASEO API ERROR] report_metrics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@paseo_bp.route('/evolution/<int:user_id>', methods=['GET'])
def get_evolution(user_id):
    """
    Obtiene reporte de evolución agrupado por fecha y nivel
    GET /paseo/evolution/<user_id>
    """
    try:
        from models.paseo import PaseoSession
        from datetime import date
        
        # Obtener todas las sesiones del usuario ordenadas por fecha
        sesiones = PaseoSession.query.filter_by(
            user_id=user_id
        ).order_by(
            PaseoSession.fecha_juego.asc(),
            PaseoSession.created_at.asc()
        ).all()
        
        if not sesiones:
            return jsonify({
                'message': 'Sin datos',
                'evolucion_por_fecha': []
            }), 200
        
        # Agrupar por FECHA
        evolucion_por_fecha = {}
        
        for sesion in sesiones:
            fecha_str = sesion.fecha_juego.isoformat()
            nivel = sesion.nivel_dificultad or 'tutorial'
            
            # Crear estructura por fecha
            if fecha_str not in evolucion_por_fecha:
                evolucion_por_fecha[fecha_str] = {
                    'fecha': fecha_str,
                    'niveles': {},
                    'resumen_dia': {
                        'total_sesiones': 0,
                        'victorias': 0,
                        'derrotas': 0,
                        'precision_promedio': 0
                    }
                }
            
            # Crear estructura por nivel
            if nivel not in evolucion_por_fecha[fecha_str]['niveles']:
                evolucion_por_fecha[fecha_str]['niveles'][nivel] = {
                    'nivel': nivel.upper(),
                    'total_sesiones': 0,
                    'victorias': 0,
                    'derrotas': 0,
                    'aciertos_totales': 0,
                    'errores_totales': 0,
                    'precision_promedio': 0
                }
            
            nivel_data = evolucion_por_fecha[fecha_str]['niveles'][nivel]
            
            # Agregar métricas
            nivel_data['total_sesiones'] += 1
            nivel_data['aciertos_totales'] += sesion.esferas_rojas_atrapadas or 0
            nivel_data['errores_totales'] += (sesion.esferas_azules_atrapadas or 0) + (sesion.esferas_perdidas or 0)
            
            if sesion.resultado == 'victoria':
                nivel_data['victorias'] += 1
                evolucion_por_fecha[fecha_str]['resumen_dia']['victorias'] += 1
            else:
                nivel_data['derrotas'] += 1
                evolucion_por_fecha[fecha_str]['resumen_dia']['derrotas'] += 1
            
            evolucion_por_fecha[fecha_str]['resumen_dia']['total_sesiones'] += 1
        
        # Calcular promedios
        for fecha_str in evolucion_por_fecha:
            total_precision_dia = 0
            count_dia = 0
            
            for nivel in evolucion_por_fecha[fecha_str]['niveles']:
                nivel_data = evolucion_por_fecha[fecha_str]['niveles'][nivel]
                
                # Precision por nivel
                total_aciertos = nivel_data['aciertos_totales']
                total_errores = nivel_data['errores_totales']
                total_esferas = total_aciertos + total_errores
                
                if total_esferas > 0:
                    precision = (total_aciertos / total_esferas) * 100
                    nivel_data['precision_promedio'] = round(precision, 2)
                    total_precision_dia += precision
                    count_dia += 1
            
            # Precisión promedio del día
            if count_dia > 0:
                evolucion_por_fecha[fecha_str]['resumen_dia']['precision_promedio'] = round(
                    total_precision_dia / count_dia, 2
                )
        
        # Convertir a lista ordenada (más reciente primero)
        resultado = []
        for fecha_str in sorted(evolucion_por_fecha.keys(), reverse=True):
            fecha_data = evolucion_por_fecha[fecha_str]
            
            # Convertir niveles a lista
            niveles_lista = []
            for nivel_key in ['tutorial', 'facil', 'intermedio', 'dificil']:
                if nivel_key in fecha_data['niveles']:
                    niveles_lista.append(fecha_data['niveles'][nivel_key])
            
            resultado.append({
                'fecha': fecha_data['fecha'],
                'resumen_dia': fecha_data['resumen_dia'],
                'niveles': niveles_lista
            })
        
        return jsonify({
            'total_sesiones': len(sesiones),
            'evolucion_por_fecha': resultado
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@paseo_bp.route('/final-stats/<int:user_id>', methods=['GET'])
def get_final_stats(user_id):
    """
    Obtiene estadísticas finales del día para mostrar al completar el juego
    GET /paseo/final-stats/<user_id>
    Query params: fecha (opcional, formato YYYY-MM-DD)
    
    Retorna: precisión, total_errores, total_aciertos
    """
    try:
        from datetime import datetime
        
        fecha_str = request.args.get('fecha')
        fecha = None
        
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        stats, error = PaseoService.get_final_stats(user_id, fecha)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(stats), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
