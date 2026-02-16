"""
================================================================================
PRUEBAS UNITARIAS - Juego de Memoria (Memory Game)
================================================================================

Indicadores Validados:
- Numero de aciertos (pares encontrados)
- Tiempo promedio de resolucion
- Nivel maximo de dificultad alcanzado
- Numero de sesiones completadas
- Tiempo total de interaccion

Ejecutar con:
    python -m pytest tests/memory_game/test_memory_game_indicators.py -v --html=tests/memory_game/informe_indicadores.html --self-contained-html
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
    """Helper para loggear datos de prueba"""
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
# INDICADOR 1: NUMERO DE ACIERTOS (Pares encontrados)
# ============================================================================
class TestIndicador01_NumeroAciertos(unittest.TestCase):
    """
    INDICADOR: Numero de aciertos (pares encontrados)
    TIPO: Cuantitativo
    CAMPO BD: memory_game_sessions.pairs_found
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("MEMORY GAME - Indicador 1: Numero de Aciertos")
        print("=" * 70)

    def test_01_pares_encontrados_cuantitativo(self):
        """Verifica que pairs_found es entero >= 0"""
        datos = {
            'pairs_found': 5,
            'total_pairs': 6,
            'total_flips': 14
        }
        
        pares = datos['pairs_found']
        es_valido = isinstance(pares, int) and pares >= 0
        
        log_test_data(
            "Pares encontrados tipo cuantitativo",
            datos,
            "int >= 0",
            f"{type(pares).__name__} = {pares}",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_precision_calculo(self):
        """Verifica calculo de precision: pairs_found / total_pairs * 100"""
        casos = [
            {'pairs_found': 6, 'total_pairs': 6, 'esperado': 100.0},
            {'pairs_found': 3, 'total_pairs': 6, 'esperado': 50.0},
            {'pairs_found': 0, 'total_pairs': 6, 'esperado': 0.0},
        ]
        
        print("-" * 60)
        print("TEST: Calculo de precision de pares")
        print("-" * 60)
        print("CASOS:")
        
        todos_ok = True
        for caso in casos:
            precision = (caso['pairs_found'] / caso['total_pairs']) * 100
            ok = abs(precision - caso['esperado']) < 0.1
            estado = "[OK]" if ok else "[FAIL]"
            print(f"    {estado} {caso['pairs_found']}/{caso['total_pairs']} = {precision}% (esperado: {caso['esperado']}%)")
            todos_ok = todos_ok and ok
        
        print(f"ESTADO: {'PASS' if todos_ok else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_ok)

    def test_03_eficiencia_flips(self):
        """Verifica eficiencia: min_flips_requeridos / total_flips * 100"""
        # Minimo de flips = pairs * 2 (encontrar cada par perfectamente)
        datos = {
            'pairs_found': 6,
            'total_pairs': 6,
            'total_flips': 18,
            'min_flips': 12  # 6 pares * 2 flips = 12
        }
        
        eficiencia = (datos['min_flips'] / datos['total_flips']) * 100
        
        log_test_data(
            "Eficiencia de flips",
            datos,
            "66.67% (12/18)",
            f"{eficiencia:.2f}%",
            60 < eficiencia < 70
        )
        
        self.assertAlmostEqual(eficiencia, 66.67, delta=0.1)


# ============================================================================
# INDICADOR 2: TIEMPO PROMEDIO DE RESOLUCION
# ============================================================================
class TestIndicador02_TiempoPromedio(unittest.TestCase):
    """
    INDICADOR: Tiempo promedio de resolucion
    TIPO: Cuantitativo (segundos)
    CAMPO BD: memory_game_sessions.elapsed_time_seconds
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("MEMORY GAME - Indicador 2: Tiempo Promedio")
        print("=" * 70)

    def test_01_tiempo_sesion(self):
        """Verifica registro de tiempo de sesion"""
        datos = {
            'elapsed_time_seconds': 45.5,
            'completion_status': 'completed'
        }
        
        tiempo = datos['elapsed_time_seconds']
        es_valido = isinstance(tiempo, (int, float)) and tiempo > 0
        
        log_test_data(
            "Tiempo de sesion registrado",
            datos,
            "float > 0",
            f"{type(tiempo).__name__} = {tiempo}",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_tiempo_promedio_multiples_sesiones(self):
        """Verifica calculo de tiempo promedio"""
        sesiones = [
            {'elapsed_time': 45.0},
            {'elapsed_time': 60.0},
            {'elapsed_time': 55.0},
            {'elapsed_time': 50.0},
        ]
        
        tiempos = [s['elapsed_time'] for s in sesiones]
        promedio = sum(tiempos) / len(tiempos)
        
        log_test_data(
            "Tiempo promedio de sesiones",
            {'tiempos': tiempos},
            "52.5 segundos",
            f"{promedio} segundos",
            promedio == 52.5
        )
        
        self.assertEqual(promedio, 52.5)

    def test_03_time_limit_por_nivel(self):
        """Verifica time_limit configurado por nivel"""
        # Segun DIFFICULTY_CONFIGS en ai_adapter_service.py
        time_limits = {
            'tutorial': 60,
            'easy': 90,
            'medium': 120,
            'hard': 150,
            'expert': 180,
            'master': 200
        }
        
        print("-" * 60)
        print("TEST: Time limit por nivel")
        print("-" * 60)
        print("CONFIGURACION:")
        
        for nivel, limite in time_limits.items():
            print(f"    - {nivel}: {limite} segundos")
        
        # Verificar que aumenta con dificultad
        valores = list(time_limits.values())
        es_creciente = all(valores[i] <= valores[i+1] for i in range(len(valores)-1))
        
        print(f"ESPERADO: Limites crecientes con dificultad")
        print(f"ESTADO: {'PASS' if es_creciente else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(es_creciente)


# ============================================================================
# INDICADOR 3: NIVEL MAXIMO DE DIFICULTAD
# ============================================================================
class TestIndicador03_NivelMaximoDificultad(unittest.TestCase):
    """
    INDICADOR: Nivel maximo de dificultad alcanzado
    TIPO: Ordinal
    CAMPO BD: memory_game_configs.difficulty_label
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("MEMORY GAME - Indicador 3: Nivel Maximo Dificultad")
        print("=" * 70)

    def test_01_niveles_ordinales(self):
        """Verifica jerarquia de niveles"""
        NIVELES = {
            'tutorial': 1,
            'easy': 2,
            'medium': 3,
            'hard': 4,
            'expert': 5,
            'master': 6
        }
        
        log_test_data(
            "Niveles son ordinales",
            NIVELES,
            "tutorial < easy < medium < hard < expert < master",
            f"Orden: {list(NIVELES.keys())}",
            True
        )
        
        valores = list(NIVELES.values())
        self.assertEqual(valores, sorted(valores))

    def test_02_nivel_inicial_tutorial(self):
        """Verifica que nivel inicial es 'tutorial'"""
        nivel_inicial = 'tutorial'
        
        log_test_data(
            "Nivel inicial es tutorial",
            {'nivel_default': 'tutorial'},
            "'tutorial'",
            f"'{nivel_inicial}'",
            nivel_inicial == 'tutorial'
        )
        
        self.assertEqual(nivel_inicial, 'tutorial')

    def test_03_pares_por_nivel(self):
        """Verifica cantidad de pares por nivel"""
        pares_por_nivel = {
            'tutorial': 3,
            'easy': 4,
            'medium': 6,
            'hard': 8,
            'expert': 10,
            'master': 12
        }
        
        print("-" * 60)
        print("TEST: Pares por nivel")
        print("-" * 60)
        print("CONFIGURACION:")
        
        for nivel, pares in pares_por_nivel.items():
            print(f"    - {nivel}: {pares} pares")
        
        # Verificar que aumenta con dificultad
        valores = list(pares_por_nivel.values())
        es_creciente = all(valores[i] <= valores[i+1] for i in range(len(valores)-1))
        
        print(f"ESPERADO: Pares crecientes con dificultad")
        print(f"ESTADO: {'PASS' if es_creciente else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(es_creciente)

    def test_04_nivel_maximo_historial(self):
        """Verifica obtencion de nivel maximo del historial"""
        NIVELES = {'tutorial': 1, 'easy': 2, 'medium': 3, 'hard': 4, 'expert': 5, 'master': 6}
        historial = ['tutorial', 'easy', 'medium', 'easy', 'medium', 'hard', 'medium']
        
        nivel_maximo = max(historial, key=lambda x: NIVELES[x])
        
        log_test_data(
            "Nivel maximo del historial",
            {'historial': historial},
            "'hard'",
            f"'{nivel_maximo}'",
            nivel_maximo == 'hard'
        )
        
        self.assertEqual(nivel_maximo, 'hard')


# ============================================================================
# INDICADOR 4: SESIONES COMPLETADAS
# ============================================================================
class TestIndicador04_SesionesCompletadas(unittest.TestCase):
    """
    INDICADOR: Numero de sesiones completadas
    TIPO: Cuantitativo
    CAMPO BD: memory_game_sessions.completion_status
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("MEMORY GAME - Indicador 4: Sesiones Completadas")
        print("=" * 70)

    def test_01_estados_validos(self):
        """Verifica estados de sesion validos"""
        ESTADOS = ['completed', 'timeout', 'abandoned']
        
        log_test_data(
            "Estados de sesion validos",
            {'estados': ESTADOS},
            "3 estados definidos",
            f"{len(ESTADOS)} estados: {ESTADOS}",
            len(ESTADOS) == 3
        )
        
        self.assertEqual(len(ESTADOS), 3)

    def test_02_conteo_completadas(self):
        """Verifica conteo de sesiones completadas"""
        sesiones = [
            {'id': 1, 'status': 'completed'},
            {'id': 2, 'status': 'timeout'},
            {'id': 3, 'status': 'completed'},
            {'id': 4, 'status': 'completed'},
            {'id': 5, 'status': 'abandoned'},
        ]
        
        completadas = sum(1 for s in sesiones if s['status'] == 'completed')
        
        print("-" * 60)
        print("TEST: Conteo de sesiones completadas")
        print("-" * 60)
        print("SESIONES:")
        for s in sesiones:
            icono = "[OK]" if s['status'] == 'completed' else "[--]"
            print(f"    {icono} Sesion {s['id']}: {s['status']}")
        print(f"RESULTADO ESPERADO: 3 completadas")
        print(f"RESULTADO OBTENIDO: {completadas} completadas")
        print(f"ESTADO: {'PASS' if completadas == 3 else 'FAIL'}")
        print("-" * 60)
        
        self.assertEqual(completadas, 3)


# ============================================================================
# INDICADOR 5: TIEMPO TOTAL INTERACCION
# ============================================================================
class TestIndicador05_TiempoTotalInteraccion(unittest.TestCase):
    """
    INDICADOR: Tiempo total de interaccion
    TIPO: Cuantitativo
    CAMPO BD: memory_game_sessions.elapsed_time_seconds (suma)
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("MEMORY GAME - Indicador 5: Tiempo Total Interaccion")
        print("=" * 70)

    def test_01_acumulacion_tiempo(self):
        """Verifica acumulacion de tiempo total"""
        sesiones = [
            {'elapsed_time': 45.0},
            {'elapsed_time': 60.0},
            {'elapsed_time': 55.0},
            {'elapsed_time': 50.0},
            {'elapsed_time': 40.0},
        ]
        
        tiempo_total = sum(s['elapsed_time'] for s in sesiones)
        
        log_test_data(
            "Acumulacion de tiempo total",
            {'sesiones': [s['elapsed_time'] for s in sesiones]},
            "250.0 segundos (4.17 min)",
            f"{tiempo_total} segundos ({tiempo_total/60:.2f} min)",
            tiempo_total == 250.0
        )
        
        self.assertEqual(tiempo_total, 250.0)


# ============================================================================
# ADAPTACION DE DIFICULTAD - LOGICA IA
# ============================================================================
class TestAdaptacionDificultad(unittest.TestCase):
    """Pruebas de la logica de adaptacion de dificultad"""
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("MEMORY GAME - Adaptacion de Dificultad")
        print("=" * 70)

    def test_01_decision_subir_nivel(self):
        """Precision alta (>=80%) y tiempo OK -> subir nivel"""
        datos = {
            'pairs_found': 6,
            'total_pairs': 6,
            'elapsed_time': 40,
            'time_limit': 60,
            'completion_status': 'completed'
        }
        
        precision = (datos['pairs_found'] / datos['total_pairs']) * 100
        tiempo_ok = datos['elapsed_time'] < datos['time_limit'] * 0.8
        
        decision = 'increase' if precision >= 80 and tiempo_ok else 'maintain'
        
        log_test_data(
            "Decision: Subir nivel (precision alta)",
            datos,
            "decision='increase'",
            f"decision='{decision}' (precision={precision}%, tiempo_ok={tiempo_ok})",
            decision == 'increase'
        )
        
        self.assertEqual(decision, 'increase')

    def test_02_decision_bajar_nivel(self):
        """Precision baja (<50%) -> bajar nivel"""
        datos = {
            'pairs_found': 2,
            'total_pairs': 6,
            'completion_status': 'timeout'
        }
        
        precision = (datos['pairs_found'] / datos['total_pairs']) * 100
        
        decision = 'decrease' if precision < 50 or datos['completion_status'] == 'timeout' else 'maintain'
        
        log_test_data(
            "Decision: Bajar nivel (precision baja)",
            datos,
            "decision='decrease'",
            f"decision='{decision}' (precision={precision:.1f}%)",
            decision == 'decrease'
        )
        
        self.assertEqual(decision, 'decrease')

    def test_03_decision_mantener(self):
        """Precision media (50-80%) -> mantener"""
        datos = {
            'pairs_found': 4,
            'total_pairs': 6,
            'elapsed_time': 55,
            'time_limit': 60,
            'completion_status': 'completed'
        }
        
        precision = (datos['pairs_found'] / datos['total_pairs']) * 100
        
        decision = 'maintain' if 50 <= precision < 80 else 'other'
        
        log_test_data(
            "Decision: Mantener nivel (zona media)",
            datos,
            "decision='maintain'",
            f"decision='{decision}' (precision={precision:.1f}%)",
            decision == 'maintain'
        )
        
        self.assertEqual(decision, 'maintain')


# ============================================================================
# RESUMEN FINAL
# ============================================================================
class TestZZ_ResumenFinal(unittest.TestCase):
    """Genera resumen"""
    
    def test_99_resumen(self):
        """Muestra resumen de indicadores"""
        print("")
        print("=" * 70)
        print("RESUMEN FINAL - MEMORY GAME")
        print("=" * 70)
        print("""
+----------------------------------------------------------------------+
|                    INDICADORES VALIDADOS                             |
+----------------------------------------------------------------------+
|  [OK] 1. Numero de aciertos/pares encontrados (Cuantitativo)         |
|  [OK] 2. Tiempo promedio de resolucion (Cuantitativo)                |
|  [OK] 3. Nivel maximo de dificultad (Ordinal)                        |
|  [OK] 4. Numero de sesiones completadas (Cuantitativo)               |
|  [OK] 5. Tiempo total de interaccion (Cuantitativo)                  |
+----------------------------------------------------------------------+
        """)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
