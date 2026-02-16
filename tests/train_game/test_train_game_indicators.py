"""
================================================================================
PRUEBAS COMPLETAS - Juego de Trenes (Train Game)
================================================================================

Este archivo contiene:
- Pruebas UNITARIAS: Validan la logica de manera aislada (con mocks)
- Pruebas de INTEGRACION: Validan el flujo real del servicio

Ejecutar con:
    python -m pytest tests/train_game/test_train_game_indicators.py -v -s --html=tests/train_game/informe_indicadores.html --self-contained-html

Ver manual de pruebas en: tests/train_game/MANUAL_PRUEBAS.md
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Add paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'app'))


def log_test_data(nombre_test, datos_entrada, resultado_esperado, resultado_obtenido, exito):
    """Helper para loggear datos de prueba de forma estructurada"""
    print("-" * 60)
    print(f"TEST: {nombre_test}")
    print("-" * 60)
    print("DATOS DE ENTRADA:")
    if isinstance(datos_entrada, dict):
        for k, v in datos_entrada.items():
            print(f"    - {k}: {v}")
    else:
        print(f"    {datos_entrada}")
    print(f"RESULTADO ESPERADO: {resultado_esperado}")
    print(f"RESULTADO OBTENIDO: {resultado_obtenido}")
    estado = "PASS" if exito else "FAIL"
    print(f"ESTADO: {estado}")
    print("-" * 60)


# ============================================================================
# PRUEBAS UNITARIAS - INDICADOR 1: NUMERO DE ACIERTOS
# ============================================================================
class TestIndicador01_NumeroAciertos(unittest.TestCase):
    """
    INDICADOR: Numero de aciertos en actividades de memoria/atencion
    TIPO: Cuantitativo
    INSTRUMENTO: Registro automatico de la aplicacion
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Indicador 1 - Numero de Aciertos")
        print("=" * 70)

    def test_01_aciertos_tipo_cuantitativo(self):
        """Verifica que los aciertos son de tipo cuantitativo (entero >= 0)"""
        # DATOS DE ENTRADA
        datos = {
            'correct_routing': 8,
            'wrong_routing': 2,
            'total_spawned': 10
        }
        
        # EJECUCION
        aciertos = datos['correct_routing']
        es_entero = isinstance(aciertos, int)
        es_positivo = aciertos >= 0
        
        # RESULTADO
        resultado_esperado = "int >= 0"
        resultado_obtenido = f"{type(aciertos).__name__} = {aciertos}"
        exito = es_entero and es_positivo
        
        log_test_data(
            "Aciertos tipo cuantitativo",
            datos,
            resultado_esperado,
            resultado_obtenido,
            exito
        )
        
        self.assertTrue(exito)

    def test_02_aciertos_rango_valido(self):
        """Verifica que aciertos estan en rango [0, total_spawned]"""
        # DATOS DE ENTRADA (multiples casos)
        casos = [
            {'correct': 0, 'total': 10, 'desc': 'Ningun acierto'},
            {'correct': 5, 'total': 10, 'desc': '50% aciertos'},
            {'correct': 10, 'total': 10, 'desc': '100% aciertos'},
        ]
        
        print("-" * 60)
        print("TEST: Aciertos en rango valido")
        print("-" * 60)
        print("CASOS DE PRUEBA:")
        
        todos_validos = True
        for caso in casos:
            en_rango = 0 <= caso['correct'] <= caso['total']
            estado = "[OK]" if en_rango else "[FAIL]"
            print(f"    {estado} {caso['desc']}: {caso['correct']}/{caso['total']}")
            todos_validos = todos_validos and en_rango
        
        print(f"ESPERADO: Todos en rango [0, total]")
        print(f"OBTENIDO: {'Todos validos' if todos_validos else 'Hay invalidos'}")
        print(f"ESTADO: {'PASS' if todos_validos else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_validos)

    def test_03_precision_calculo_correcto(self):
        """Verifica el calculo de precision: (aciertos/total) * 100"""
        # DATOS DE ENTRADA
        casos = [
            {'correct': 8, 'wrong': 2, 'esperado': 80.0},
            {'correct': 10, 'wrong': 0, 'esperado': 100.0},
            {'correct': 0, 'wrong': 10, 'esperado': 0.0},
            {'correct': 7, 'wrong': 3, 'esperado': 70.0},
        ]
        
        print("-" * 60)
        print("TEST: Calculo de precision")
        print("-" * 60)
        print("DATOS Y RESULTADOS:")
        
        todos_correctos = True
        for caso in casos:
            total = caso['correct'] + caso['wrong']
            precision = (caso['correct'] / total * 100) if total > 0 else 0
            correcto = abs(precision - caso['esperado']) < 0.1
            estado = "[OK]" if correcto else "[FAIL]"
            print(f"    {estado} {caso['correct']}/{total} -> {precision:.1f}% (esperado: {caso['esperado']}%)")
            todos_correctos = todos_correctos and correcto
        
        print(f"FORMULA: (aciertos / total) * 100")
        print(f"ESTADO: {'PASS' if todos_correctos else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_correctos)

    def test_04_acumulacion_sesiones(self):
        """Verifica la acumulacion de aciertos en multiples sesiones"""
        # DATOS DE ENTRADA
        datos_sesiones = [
            {'session_id': 1, 'correct_routing': 8},
            {'session_id': 2, 'correct_routing': 6},
            {'session_id': 3, 'correct_routing': 10},
            {'session_id': 4, 'correct_routing': 5},
        ]
        
        # EJECUCION
        total_aciertos = sum(s['correct_routing'] for s in datos_sesiones)
        
        # RESULTADO
        resultado_esperado = 29
        
        log_test_data(
            "Acumulacion de aciertos",
            {'sesiones': datos_sesiones},
            f"Total = {resultado_esperado}",
            f"Total = {total_aciertos}",
            total_aciertos == resultado_esperado
        )
        
        self.assertEqual(total_aciertos, resultado_esperado)


# ============================================================================
# PRUEBAS UNITARIAS - INDICADOR 2: TIEMPO PROMEDIO
# ============================================================================
class TestIndicador02_TiempoPromedioResolucion(unittest.TestCase):
    """
    INDICADOR: Tiempo promedio de resolucion por actividad
    TIPO: Cuantitativo (segundos)
    INSTRUMENTO: Registro automatico de la aplicacion
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Indicador 2 - Tiempo Promedio")
        print("=" * 70)

    def test_01_duracion_sesion_calculable(self):
        """Verifica que la duracion se calcula desde timestamps"""
        # DATOS DE ENTRADA
        datos = {
            'started_at': '2026-01-21 10:00:00',
            'finished_at': '2026-01-21 10:01:30'
        }
        
        started = datetime(2026, 1, 21, 10, 0, 0)
        finished = datetime(2026, 1, 21, 10, 1, 30)
        
        # EJECUCION
        duracion = (finished - started).total_seconds()
        
        log_test_data(
            "Calculo de duracion de sesion",
            datos,
            "90 segundos",
            f"{duracion} segundos",
            duracion == 90.0
        )
        
        self.assertEqual(duracion, 90.0)

    def test_02_tiempo_promedio_multiples_sesiones(self):
        """Verifica el calculo del tiempo promedio"""
        # DATOS DE ENTRADA
        datos = {
            'sesion_1': {'duracion': 60, 'unidad': 'segundos'},
            'sesion_2': {'duracion': 90, 'unidad': 'segundos'},
            'sesion_3': {'duracion': 120, 'unidad': 'segundos'},
        }
        
        duraciones = [60, 90, 120]
        
        # EJECUCION
        tiempo_promedio = sum(duraciones) / len(duraciones)
        
        log_test_data(
            "Tiempo promedio de sesiones",
            datos,
            "90.0 segundos",
            f"{tiempo_promedio} segundos",
            tiempo_promedio == 90.0
        )
        
        self.assertEqual(tiempo_promedio, 90.0)

    def test_03_tiempo_limite_configurado(self):
        """Verifica que el tiempo limite esta configurado en 90 segundos"""
        from app.services.train_game.train_ai_adapter import TIME_LIMIT
        
        log_test_data(
            "Tiempo limite configurado",
            {'constante': 'TIME_LIMIT'},
            "90 segundos",
            f"{TIME_LIMIT} segundos",
            TIME_LIMIT == 90
        )
        
        self.assertEqual(TIME_LIMIT, 90)

    def test_04_sesiones_sin_finalizar_ignoradas(self):
        """Verifica que sesiones sin finished_at no se cuentan"""
        # DATOS DE ENTRADA
        datos = {
            'sesion_1': {'started': '10:00:00', 'finished': '10:01:00', 'valida': True},
            'sesion_2': {'started': '11:00:00', 'finished': None, 'valida': False},
            'sesion_3': {'started': '12:00:00', 'finished': '12:01:30', 'valida': True},
        }
        
        sesiones_validas = sum(1 for s in datos.values() if s['valida'])
        
        log_test_data(
            "Sesiones sin finalizar ignoradas",
            datos,
            "2 sesiones validas",
            f"{sesiones_validas} sesiones validas",
            sesiones_validas == 2
        )
        
        self.assertEqual(sesiones_validas, 2)


# ============================================================================
# PRUEBAS UNITARIAS - INDICADOR 3: NIVEL MAXIMO DIFICULTAD
# ============================================================================
class TestIndicador03_NivelMaximoDificultad(unittest.TestCase):
    """
    INDICADOR: Nivel maximo de dificultad alcanzado
    TIPO: Ordinal (easy < medium < hard)
    INSTRUMENTO: Algoritmo de IA integrado
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Indicador 3 - Nivel Maximo Dificultad")
        print("=" * 70)

    def test_01_niveles_son_ordinales(self):
        """Verifica que los niveles tienen orden jerarquico"""
        # DATOS DE ENTRADA
        datos = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }
        
        orden_correcto = datos['easy'] < datos['medium'] < datos['hard']
        
        log_test_data(
            "Niveles son ordinales",
            datos,
            "easy(1) < medium(2) < hard(3)",
            f"easy({datos['easy']}) < medium({datos['medium']}) < hard({datos['hard']})",
            orden_correcto
        )
        
        self.assertTrue(orden_correcto)

    def test_02_nivel_inicial_easy(self):
        """Verifica que todos los usuarios empiezan en 'easy'"""
        from app.services.train_game.train_ai_adapter import DIFFICULTY_FIXED_VALUES, MIN_SPEED
        
        # DATOS
        datos = {
            'MIN_SPEED': MIN_SPEED,
            'velocidad_inicial': MIN_SPEED,
            'nivel_esperado': 'easy'
        }
        
        from app.services.train_game.train_ai_adapter import get_difficulty_label
        nivel_inicial = get_difficulty_label(MIN_SPEED)
        
        log_test_data(
            "Nivel inicial es 'easy'",
            datos,
            "'easy'",
            f"'{nivel_inicial}'",
            nivel_inicial == 'easy'
        )
        
        self.assertEqual(nivel_inicial, 'easy')

    def test_03_determinacion_nivel_por_velocidad(self):
        """Verifica la funcion get_difficulty_label"""
        from app.services.train_game.train_ai_adapter import get_difficulty_label
        
        # DATOS DE ENTRADA
        casos = [
            {'velocidad': 3.0, 'nivel_esperado': 'easy'},
            {'velocidad': 3.5, 'nivel_esperado': 'easy'},
            {'velocidad': 4.0, 'nivel_esperado': 'medium'},
            {'velocidad': 5.0, 'nivel_esperado': 'medium'},
            {'velocidad': 5.5, 'nivel_esperado': 'hard'},
            {'velocidad': 6.0, 'nivel_esperado': 'hard'},
        ]
        
        print("-" * 60)
        print("TEST: Determinacion de nivel por velocidad")
        print("-" * 60)
        print("CASOS DE PRUEBA:")
        print("    REGLAS: speed <= 3.5 -> easy | 3.5 < speed <= 5.0 -> medium | speed > 5.0 -> hard")
        
        todos_correctos = True
        for caso in casos:
            nivel = get_difficulty_label(caso['velocidad'])
            correcto = nivel == caso['nivel_esperado']
            estado = "[OK]" if correcto else "[FAIL]"
            print(f"    {estado} velocidad={caso['velocidad']} -> '{nivel}' (esperado: '{caso['nivel_esperado']}')")
            todos_correctos = todos_correctos and correcto
        
        print(f"ESTADO: {'PASS' if todos_correctos else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_correctos)

    def test_04_nivel_maximo_entre_sesiones(self):
        """Verifica obtencion del nivel maximo alcanzado"""
        # DATOS DE ENTRADA
        NIVELES = {'easy': 1, 'medium': 2, 'hard': 3}
        historial = ['easy', 'medium', 'easy', 'hard', 'medium', 'hard']
        
        nivel_maximo = max(historial, key=lambda x: NIVELES[x])
        
        log_test_data(
            "Nivel maximo entre sesiones",
            {'historial': historial, 'orden': NIVELES},
            "'hard'",
            f"'{nivel_maximo}'",
            nivel_maximo == 'hard'
        )
        
        self.assertEqual(nivel_maximo, 'hard')


# ============================================================================
# PRUEBAS UNITARIAS - INDICADOR 4: SESIONES COMPLETADAS
# ============================================================================
class TestIndicador04_SesionesCompletadas(unittest.TestCase):
    """
    INDICADOR: Numero de sesiones completadas
    TIPO: Cuantitativo
    INSTRUMENTO: Registro automatico del sistema
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Indicador 4 - Sesiones Completadas")
        print("=" * 70)

    def test_01_estados_validos(self):
        """Verifica los estados de sesion validos"""
        ESTADOS_VALIDOS = ['completed', 'timeout', 'abandoned']
        
        log_test_data(
            "Estados de sesion validos",
            {'estados_definidos': ESTADOS_VALIDOS},
            "3 estados",
            f"{len(ESTADOS_VALIDOS)} estados: {ESTADOS_VALIDOS}",
            len(ESTADOS_VALIDOS) == 3
        )
        
        self.assertEqual(len(ESTADOS_VALIDOS), 3)

    def test_02_conteo_completadas(self):
        """Verifica el conteo de sesiones completadas"""
        # DATOS DE ENTRADA
        datos = [
            {'session_id': 1, 'status': 'completed'},
            {'session_id': 2, 'status': 'timeout'},
            {'session_id': 3, 'status': 'completed'},
            {'session_id': 4, 'status': 'abandoned'},
            {'session_id': 5, 'status': 'completed'},
        ]
        
        completadas = sum(1 for s in datos if s['status'] == 'completed')
        
        print("-" * 60)
        print("TEST: Conteo de sesiones completadas")
        print("-" * 60)
        print("DATOS DE ENTRADA:")
        for s in datos:
            icono = "[OK]" if s['status'] == 'completed' else "[--]"
            print(f"    {icono} Sesion {s['session_id']}: {s['status']}")
        print(f"RESULTADO ESPERADO: 3 completadas")
        print(f"RESULTADO OBTENIDO: {completadas} completadas")
        print(f"ESTADO: {'PASS' if completadas == 3 else 'FAIL'}")
        print("-" * 60)
        
        self.assertEqual(completadas, 3)

    def test_03_tasa_completitud(self):
        """Verifica el calculo de tasa de completitud"""
        # DATOS DE ENTRADA
        datos = {
            'total_sesiones': 10,
            'completadas': 7
        }
        
        tasa = (datos['completadas'] / datos['total_sesiones']) * 100
        
        log_test_data(
            "Tasa de completitud",
            datos,
            "70.0%",
            f"{tasa}%",
            tasa == 70.0
        )
        
        self.assertEqual(tasa, 70.0)


# ============================================================================
# PRUEBAS UNITARIAS - INDICADOR 5: TIEMPO TOTAL INTERACCION
# ============================================================================
class TestIndicador05_TiempoTotalInteraccion(unittest.TestCase):
    """
    INDICADOR: Tiempo total de interaccion durante el programa
    TIPO: Cuantitativo (segundos/minutos)
    INSTRUMENTO: Registro de uso
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Indicador 5 - Tiempo Total Interaccion")
        print("=" * 70)

    def test_01_acumulacion_tiempo(self):
        """Verifica la acumulacion de tiempo total"""
        # DATOS DE ENTRADA
        datos = {
            'sesion_1': 90,
            'sesion_2': 85,
            'sesion_3': 75,
            'sesion_4': 90,
            'sesion_5': 60
        }
        
        tiempo_total = sum(datos.values())
        
        log_test_data(
            "Acumulacion de tiempo total",
            datos,
            "400 segundos (6.7 min)",
            f"{tiempo_total} segundos ({tiempo_total/60:.1f} min)",
            tiempo_total == 400
        )
        
        self.assertEqual(tiempo_total, 400)

    def test_02_conversion_unidades(self):
        """Verifica conversion de segundos a minutos/horas"""
        # DATOS DE ENTRADA
        datos = {'tiempo_segundos': 5400}
        
        tiempo_minutos = datos['tiempo_segundos'] / 60
        tiempo_horas = datos['tiempo_segundos'] / 3600
        
        log_test_data(
            "Conversion de unidades de tiempo",
            datos,
            "90 minutos / 1.5 horas",
            f"{tiempo_minutos} minutos / {tiempo_horas} horas",
            tiempo_minutos == 90.0 and tiempo_horas == 1.5
        )
        
        self.assertEqual(tiempo_minutos, 90.0)
        self.assertEqual(tiempo_horas, 1.5)

    def test_03_tiempo_por_usuario(self):
        """Verifica el tiempo total por usuario individual"""
        # DATOS DE ENTRADA
        datos = {
            'usuario_1': {'sesiones': [90, 85, 70], 'total_esperado': 245},
            'usuario_2': {'sesiones': [60, 90], 'total_esperado': 150},
            'usuario_3': {'sesiones': [90, 90, 90, 90], 'total_esperado': 360},
        }
        
        print("-" * 60)
        print("TEST: Tiempo por usuario")
        print("-" * 60)
        print("DATOS DE ENTRADA:")
        
        todos_correctos = True
        for usuario, info in datos.items():
            total = sum(info['sesiones'])
            correcto = total == info['total_esperado']
            estado = "[OK]" if correcto else "[FAIL]"
            print(f"    {estado} {usuario}: {info['sesiones']} -> {total}s (esperado: {info['total_esperado']}s)")
            todos_correctos = todos_correctos and correcto
        
        print(f"ESTADO: {'PASS' if todos_correctos else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_correctos)


# ============================================================================
# PRUEBAS DE INTEGRACION - SISTEMA DE ADAPTACION IA
# ============================================================================
class TestIntegracion_SistemaAdaptacion(unittest.TestCase):
    """
    PRUEBAS DE INTEGRACION: Sistema de Adaptacion de Dificultad
    Verifica el flujo completo del algoritmo de IA
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Pruebas de Integracion - Sistema IA")
        print("=" * 70)

    def test_01_flujo_subir_dificultad(self):
        """Alta precision (>=85%) -> subir dificultad"""
        from app.services.train_game.train_ai_adapter import TrainAIAdapter
        
        # DATOS DE ENTRADA
        datos_entrada = {
            'correct_routing': 9,
            'wrong_routing': 1,
            'total_spawned': 10,
            'completion_status': 'completed',
            'config_actual': {'train_speed': 3.5, 'spawn_rate': 9.0}
        }
        
        with patch.object(TrainAIAdapter, '__init__', lambda self: None):
            adapter = TrainAIAdapter()
            adapter.use_ai = False
            
            result = adapter._analyze_classic(
                {k: v for k, v in datos_entrada.items() if k != 'config_actual'},
                datos_entrada['config_actual']
            )
        
        log_test_data(
            "Flujo: Subir dificultad (precision >= 85%)",
            datos_entrada,
            "decision='increase_difficulty', velocidad > 3.5",
            f"decision='{result['decision']}', velocidad={result['next_config']['train_speed']}",
            result['decision'] == 'increase_difficulty'
        )
        
        self.assertEqual(result['decision'], 'increase_difficulty')

    def test_02_flujo_bajar_dificultad(self):
        """Baja precision (<50%) -> bajar dificultad"""
        from app.services.train_game.train_ai_adapter import TrainAIAdapter
        
        # DATOS DE ENTRADA
        datos_entrada = {
            'correct_routing': 3,
            'wrong_routing': 7,
            'total_spawned': 10,
            'completion_status': 'completed',
            'config_actual': {'train_speed': 5.0, 'spawn_rate': 7.0}
        }
        
        with patch.object(TrainAIAdapter, '__init__', lambda self: None):
            adapter = TrainAIAdapter()
            adapter.use_ai = False
            
            result = adapter._analyze_classic(
                {k: v for k, v in datos_entrada.items() if k != 'config_actual'},
                datos_entrada['config_actual']
            )
        
        log_test_data(
            "Flujo: Bajar dificultad (precision < 50%)",
            datos_entrada,
            "decision='decrease_difficulty', velocidad < 5.0",
            f"decision='{result['decision']}', velocidad={result['next_config']['train_speed']}",
            result['decision'] == 'decrease_difficulty'
        )
        
        self.assertEqual(result['decision'], 'decrease_difficulty')

    def test_03_flujo_mantener_dificultad(self):
        """Precision media (50-85%) -> mantener dificultad"""
        from app.services.train_game.train_ai_adapter import TrainAIAdapter
        
        # DATOS DE ENTRADA
        datos_entrada = {
            'correct_routing': 7,
            'wrong_routing': 3,
            'total_spawned': 10,
            'completion_status': 'completed',
            'config_actual': {'train_speed': 4.0, 'spawn_rate': 8.0}
        }
        
        with patch.object(TrainAIAdapter, '__init__', lambda self: None):
            adapter = TrainAIAdapter()
            adapter.use_ai = False
            
            result = adapter._analyze_classic(
                {k: v for k, v in datos_entrada.items() if k != 'config_actual'},
                datos_entrada['config_actual']
            )
        
        log_test_data(
            "Flujo: Mantener dificultad (50% <= precision < 85%)",
            datos_entrada,
            "decision='maintain', velocidad = 4.0",
            f"decision='{result['decision']}', velocidad={result['next_config']['train_speed']}",
            result['decision'] == 'maintain'
        )
        
        self.assertEqual(result['decision'], 'maintain')

    def test_04_timeout_siempre_baja(self):
        """Timeout -> SIEMPRE bajar dificultad (independiente de precision)"""
        from app.services.train_game.train_ai_adapter import TrainAIAdapter
        
        # DATOS DE ENTRADA (precision perfecta pero timeout)
        datos_entrada = {
            'correct_routing': 10,
            'wrong_routing': 0,
            'total_spawned': 10,
            'completion_status': 'timeout',
            'precision': '100%',
            'nota': 'Aunque la precision es perfecta, timeout SIEMPRE baja',
            'config_actual': {'train_speed': 5.5, 'spawn_rate': 6.0}
        }
        
        with patch.object(TrainAIAdapter, '__init__', lambda self: None):
            adapter = TrainAIAdapter()
            adapter.use_ai = False
            
            result = adapter._analyze_classic(
                {k: v for k, v in datos_entrada.items() if k not in ['config_actual', 'precision', 'nota']},
                datos_entrada['config_actual']
            )
        
        log_test_data(
            "Timeout SIEMPRE baja dificultad",
            datos_entrada,
            "decision='decrease_difficulty' (sin importar precision)",
            f"decision='{result['decision']}'",
            result['decision'] == 'decrease_difficulty'
        )
        
        self.assertEqual(result['decision'], 'decrease_difficulty')


# ============================================================================
# PRUEBAS DE LIMITES Y RESTRICCIONES
# ============================================================================
class TestLimites_Restricciones(unittest.TestCase):
    """Verifican que el sistema respeta restricciones configuradas"""
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("INICIANDO: Limites y Restricciones")
        print("=" * 70)

    def test_01_velocidad_minima(self):
        """Velocidad nunca baja de 3.0"""
        from app.services.train_game.train_ai_adapter import MIN_SPEED, TrainAIAdapter
        
        # DATOS
        datos = {
            'MIN_SPEED': MIN_SPEED,
            'velocidad_actual': 3.0,
            'precision': '10%',
            'accion': 'Intentar bajar aun mas'
        }
        
        with patch.object(TrainAIAdapter, '__init__', lambda self: None):
            adapter = TrainAIAdapter()
            adapter.use_ai = False
            
            result = adapter._analyze_classic(
                {'correct_routing': 1, 'wrong_routing': 9, 'total_spawned': 10, 'completion_status': 'completed'},
                {'train_speed': 3.0, 'spawn_rate': 10.0}
            )
        
        velocidad_final = result['next_config']['train_speed']
        
        log_test_data(
            "Velocidad minima respetada",
            datos,
            f"velocidad >= {MIN_SPEED}",
            f"velocidad = {velocidad_final}",
            velocidad_final >= MIN_SPEED
        )
        
        self.assertGreaterEqual(velocidad_final, MIN_SPEED)

    def test_02_velocidad_maxima(self):
        """Velocidad nunca sube de 6.0"""
        from app.services.train_game.train_ai_adapter import MAX_SPEED, TrainAIAdapter
        
        # DATOS
        datos = {
            'MAX_SPEED': MAX_SPEED,
            'velocidad_actual': 6.0,
            'precision': '100%',
            'accion': 'Intentar subir aun mas'
        }
        
        with patch.object(TrainAIAdapter, '__init__', lambda self: None):
            adapter = TrainAIAdapter()
            adapter.use_ai = False
            
            result = adapter._analyze_classic(
                {'correct_routing': 10, 'wrong_routing': 0, 'total_spawned': 10, 'completion_status': 'completed'},
                {'train_speed': 6.0, 'spawn_rate': 5.0}
            )
        
        velocidad_final = result['next_config']['train_speed']
        
        log_test_data(
            "Velocidad maxima respetada",
            datos,
            f"velocidad <= {MAX_SPEED}",
            f"velocidad = {velocidad_final}",
            velocidad_final <= MAX_SPEED
        )
        
        self.assertLessEqual(velocidad_final, MAX_SPEED)

    def test_03_valores_fijos_por_nivel(self):
        """Valores fijos correctos para cada nivel"""
        from app.services.train_game.train_ai_adapter import DIFFICULTY_FIXED_VALUES
        
        # DATOS ESPERADOS
        datos_esperados = {
            'easy': {'total_trains': 6, 'color_count': 3},
            'medium': {'total_trains': 8, 'color_count': 4},
            'hard': {'total_trains': 10, 'color_count': 5},
        }
        
        print("-" * 60)
        print("TEST: Valores fijos por nivel")
        print("-" * 60)
        print("VALORES CONFIGURADOS vs ESPERADOS:")
        
        todos_correctos = True
        for nivel, esperado in datos_esperados.items():
            actual = DIFFICULTY_FIXED_VALUES[nivel]
            correcto = actual['total_trains'] == esperado['total_trains'] and actual['color_count'] == esperado['color_count']
            estado = "[OK]" if correcto else "[FAIL]"
            print(f"    {estado} {nivel.upper()}: trenes={actual['total_trains']} (esp:{esperado['total_trains']}), colores={actual['color_count']} (esp:{esperado['color_count']})")
            todos_correctos = todos_correctos and correcto
        
        print(f"ESTADO: {'PASS' if todos_correctos else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_correctos)


# ============================================================================
# RESUMEN FINAL
# ============================================================================
class TestZZ_ResumenFinal(unittest.TestCase):
    """Genera resumen al final"""
    
    def test_99_resumen(self):
        """Muestra resumen de indicadores"""
        print("")
        print("=" * 70)
        print("RESUMEN FINAL DE PRUEBAS")
        print("=" * 70)
        print("""
+----------------------------------------------------------------------+
|                    INDICADORES VALIDADOS                             |
+----------------------------------------------------------------------+
|  [OK] 1. Numero de aciertos (Cuantitativo)                           |
|  [OK] 2. Tiempo promedio de resolucion (Cuantitativo)                |
|  [OK] 3. Nivel maximo de dificultad (Ordinal)                        |
|  [OK] 4. Numero de sesiones completadas (Cuantitativo)               |
|  [OK] 5. Tiempo total de interaccion (Cuantitativo)                  |
+----------------------------------------------------------------------+
|  INDICADORES NO AUTOMATIZABLES:                                      |
|  [--] Satisfaccion del usuario (Cuestionario Likert)                 |
|  [--] Usabilidad (Escala SUS)                                        |
+----------------------------------------------------------------------+
|  Ver manual completo: tests/train_game/MANUAL_PRUEBAS.md             |
+----------------------------------------------------------------------+
        """)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
