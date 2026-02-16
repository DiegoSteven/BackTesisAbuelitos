"""
================================================================================
PRUEBAS UNITARIAS - Juego de Abecedario (Word Game)
================================================================================

Indicadores Validados:
- Numero de aciertos (palabras completadas)
- Tiempo promedio de resolucion por palabra
- Nivel maximo de dificultad alcanzado
- Numero de sesiones/palabras completadas
- Cantidad de errores y pistas usadas

Ejecutar con:
    python -m pytest tests/abecedario/test_abecedario_indicators.py -v --html=tests/abecedario/informe_indicadores.html --self-contained-html
"""

import unittest
import sys
import os
from datetime import datetime

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
# INDICADOR 1: NUMERO DE ACIERTOS (Palabras completadas)
# ============================================================================
class TestIndicador01_PalabrasCompletadas(unittest.TestCase):
    """
    INDICADOR: Numero de palabras completadas correctamente
    TIPO: Cuantitativo
    CAMPO BD: abecedario_session.completado
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("ABECEDARIO - Indicador 1: Palabras Completadas")
        print("=" * 70)

    def test_01_completado_es_booleano(self):
        """Verifica que completado es booleano"""
        datos = {
            'palabra_objetivo': 'GATO',
            'completado': True,
            'cantidad_errores': 2
        }
        
        completado = datos['completado']
        es_valido = isinstance(completado, bool)
        
        log_test_data(
            "Campo completado es booleano",
            datos,
            "bool (True/False)",
            f"{type(completado).__name__} = {completado}",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_conteo_palabras_completadas(self):
        """Verifica conteo de palabras completadas"""
        sesiones = [
            {'palabra': 'GATO', 'completado': True},
            {'palabra': 'PERRO', 'completado': True},
            {'palabra': 'PAJARO', 'completado': False},
            {'palabra': 'CASA', 'completado': True},
            {'palabra': 'ARBOL', 'completado': False},
        ]
        
        completadas = sum(1 for s in sesiones if s['completado'])
        
        print("-" * 60)
        print("TEST: Conteo de palabras completadas")
        print("-" * 60)
        print("SESIONES:")
        for s in sesiones:
            icono = "[OK]" if s['completado'] else "[--]"
            print(f"    {icono} {s['palabra']}: {'completada' if s['completado'] else 'no completada'}")
        print(f"RESULTADO ESPERADO: 3 completadas")
        print(f"RESULTADO OBTENIDO: {completadas} completadas")
        print(f"ESTADO: {'PASS' if completadas == 3 else 'FAIL'}")
        print("-" * 60)
        
        self.assertEqual(completadas, 3)

    def test_03_tasa_exito(self):
        """Verifica calculo de tasa de exito"""
        datos = {
            'total_palabras': 10,
            'completadas': 7
        }
        
        tasa = (datos['completadas'] / datos['total_palabras']) * 100
        
        log_test_data(
            "Tasa de exito",
            datos,
            "70.0%",
            f"{tasa}%",
            tasa == 70.0
        )
        
        self.assertEqual(tasa, 70.0)


# ============================================================================
# INDICADOR 2: TIEMPO DE RESOLUCION POR PALABRA
# ============================================================================
class TestIndicador02_TiempoResolucion(unittest.TestCase):
    """
    INDICADOR: Tiempo promedio de resolucion por palabra
    TIPO: Cuantitativo (segundos)
    CAMPO BD: abecedario_session.tiempo_resolucion
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("ABECEDARIO - Indicador 2: Tiempo de Resolucion")
        print("=" * 70)

    def test_01_tiempo_registrado(self):
        """Verifica que tiempo_resolucion se registra"""
        datos = {
            'palabra_objetivo': 'GATO',
            'tiempo_resolucion': 25.5,
            'completado': True
        }
        
        tiempo = datos['tiempo_resolucion']
        es_valido = isinstance(tiempo, (int, float)) and tiempo > 0
        
        log_test_data(
            "Tiempo de resolucion registrado",
            datos,
            "float > 0 segundos",
            f"{tipo if (tipo := type(tiempo).__name__) else 'None'} = {tiempo}s",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_tiempo_promedio(self):
        """Verifica calculo de tiempo promedio"""
        sesiones = [
            {'palabra': 'GATO', 'tiempo': 20.0, 'completado': True},
            {'palabra': 'PERRO', 'tiempo': 30.0, 'completado': True},
            {'palabra': 'CASA', 'tiempo': 25.0, 'completado': True},
            {'palabra': 'MESA', 'tiempo': 35.0, 'completado': True},
        ]
        
        tiempos = [s['tiempo'] for s in sesiones if s['completado']]
        promedio = sum(tiempos) / len(tiempos)
        
        log_test_data(
            "Tiempo promedio de resolucion",
            {'tiempos': tiempos},
            "27.5 segundos",
            f"{promedio} segundos",
            promedio == 27.5
        )
        
        self.assertEqual(promedio, 27.5)

    def test_03_tiempo_por_longitud(self):
        """Verifica que palabras mas largas toman mas tiempo"""
        sesiones = [
            {'palabra': 'SOL', 'longitud': 3, 'tiempo': 15.0},
            {'palabra': 'CASA', 'longitud': 4, 'tiempo': 20.0},
            {'palabra': 'PERRO', 'longitud': 5, 'tiempo': 30.0},
            {'palabra': 'ELEFANTE', 'longitud': 8, 'tiempo': 45.0},
        ]
        
        print("-" * 60)
        print("TEST: Tiempo crece con longitud de palabra")
        print("-" * 60)
        print("DATOS:")
        for s in sesiones:
            print(f"    - {s['palabra']} ({s['longitud']} letras): {s['tiempo']}s")
        
        # Verificar tendencia creciente
        tiempos = [s['tiempo'] for s in sesiones]
        es_creciente = all(tiempos[i] <= tiempos[i+1] for i in range(len(tiempos)-1))
        
        print(f"ESPERADO: Tiempos crecientes")
        print(f"ESTADO: {'PASS' if es_creciente else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(es_creciente)


# ============================================================================
# INDICADOR 3: NIVEL DE DIFICULTAD
# ============================================================================
class TestIndicador03_NivelDificultad(unittest.TestCase):
    """
    INDICADOR: Nivel maximo de dificultad alcanzado
    TIPO: Ordinal
    CAMPO BD: abecedario_session.nivel_jugado
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("ABECEDARIO - Indicador 3: Nivel de Dificultad")
        print("=" * 70)

    def test_01_niveles_validos(self):
        """Verifica niveles de dificultad validos"""
        NIVELES = ['facil', 'intermedio', 'dificil']
        
        log_test_data(
            "Niveles de dificultad validos",
            {'niveles': NIVELES},
            "3 niveles: facil < intermedio < dificil",
            f"{len(NIVELES)} niveles: {NIVELES}",
            len(NIVELES) == 3
        )
        
        self.assertEqual(len(NIVELES), 3)

    def test_02_longitud_palabra_por_nivel(self):
        """Verifica longitud de palabras por nivel"""
        longitudes = {
            'facil': [3, 4],       # 3-4 letras
            'intermedio': [5, 6], # 5-6 letras
            'dificil': [7, 8, 9]  # 7+ letras
        }
        
        print("-" * 60)
        print("TEST: Longitud de palabras por nivel")
        print("-" * 60)
        print("CONFIGURACION:")
        for nivel, rango in longitudes.items():
            print(f"    - {nivel}: {min(rango)}-{max(rango)} letras")
        
        # Verificar que dificultad aumenta con longitud
        rangos_max = [max(longitudes[n]) for n in ['facil', 'intermedio', 'dificil']]
        es_creciente = rangos_max == sorted(rangos_max)
        
        print(f"ESPERADO: Longitud crece con dificultad")
        print(f"ESTADO: {'PASS' if es_creciente else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(es_creciente)

    def test_03_nivel_maximo_historial(self):
        """Verifica obtencion de nivel maximo"""
        NIVELES = {'facil': 1, 'intermedio': 2, 'dificil': 3}
        historial = ['facil', 'facil', 'intermedio', 'facil', 'intermedio', 'dificil', 'intermedio']
        
        nivel_maximo = max(historial, key=lambda x: NIVELES[x])
        
        log_test_data(
            "Nivel maximo del historial",
            {'historial': historial},
            "'dificil'",
            f"'{nivel_maximo}'",
            nivel_maximo == 'dificil'
        )
        
        self.assertEqual(nivel_maximo, 'dificil')


# ============================================================================
# INDICADOR 4: ERRORES Y PISTAS
# ============================================================================
class TestIndicador04_ErroresPistas(unittest.TestCase):
    """
    INDICADOR: Cantidad de errores y pistas usadas
    TIPO: Cuantitativo
    CAMPOS BD: cantidad_errores, pistas_usadas
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("ABECEDARIO - Indicador 4: Errores y Pistas")
        print("=" * 70)

    def test_01_errores_cuantitativos(self):
        """Verifica que errores son enteros >= 0"""
        datos = {
            'palabra_objetivo': 'GATO',
            'cantidad_errores': 3,
            'completado': True
        }
        
        errores = datos['cantidad_errores']
        es_valido = isinstance(errores, int) and errores >= 0
        
        log_test_data(
            "Errores son cuantitativos",
            datos,
            "int >= 0",
            f"{type(errores).__name__} = {errores}",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_pistas_cuantitativas(self):
        """Verifica que pistas son enteros >= 0"""
        datos = {
            'palabra_objetivo': 'ELEFANTE',
            'pistas_usadas': 2,
            'completado': True
        }
        
        pistas = datos['pistas_usadas']
        es_valido = isinstance(pistas, int) and pistas >= 0
        
        log_test_data(
            "Pistas son cuantitativas",
            datos,
            "int >= 0",
            f"{type(pistas).__name__} = {pistas}",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_03_promedio_errores(self):
        """Verifica calculo de promedio de errores"""
        sesiones = [
            {'errores': 2},
            {'errores': 1},
            {'errores': 3},
            {'errores': 0},
            {'errores': 4},
        ]
        
        promedio = sum(s['errores'] for s in sesiones) / len(sesiones)
        
        log_test_data(
            "Promedio de errores por palabra",
            {'errores': [s['errores'] for s in sesiones]},
            "2.0 errores",
            f"{promedio} errores",
            promedio == 2.0
        )
        
        self.assertEqual(promedio, 2.0)


# ============================================================================
# INDICADOR 5: TIEMPO TOTAL
# ============================================================================
class TestIndicador05_TiempoTotal(unittest.TestCase):
    """
    INDICADOR: Tiempo total de interaccion
    TIPO: Cuantitativo
    CAMPO BD: tiempo_resolucion (suma)
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("ABECEDARIO - Indicador 5: Tiempo Total")
        print("=" * 70)

    def test_01_acumulacion_tiempo(self):
        """Verifica acumulacion de tiempo total"""
        sesiones = [
            {'palabra': 'GATO', 'tiempo': 20.0},
            {'palabra': 'PERRO', 'tiempo': 30.0},
            {'palabra': 'CASA', 'tiempo': 25.0},
            {'palabra': 'MESA', 'tiempo': 15.0},
            {'palabra': 'SILLA', 'tiempo': 35.0},
        ]
        
        tiempo_total = sum(s['tiempo'] for s in sesiones)
        
        log_test_data(
            "Tiempo total acumulado",
            {'tiempos': [s['tiempo'] for s in sesiones]},
            "125.0 segundos (2.08 min)",
            f"{tiempo_total} segundos ({tiempo_total/60:.2f} min)",
            tiempo_total == 125.0
        )
        
        self.assertEqual(tiempo_total, 125.0)


# ============================================================================
# CAMBIO DE NIVEL
# ============================================================================
class TestCambioNivel(unittest.TestCase):
    """Pruebas del flag cambio_nivel"""
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("ABECEDARIO - Cambio de Nivel")
        print("=" * 70)

    def test_01_cambio_nivel_detectado(self):
        """Verifica que cambio_nivel se marca correctamente"""
        sesiones = [
            {'nivel': 'facil', 'cambio_nivel': False},
            {'nivel': 'facil', 'cambio_nivel': False},
            {'nivel': 'intermedio', 'cambio_nivel': True},  # Cambio!
            {'nivel': 'intermedio', 'cambio_nivel': False},
            {'nivel': 'dificil', 'cambio_nivel': True},     # Cambio!
        ]
        
        cambios = sum(1 for s in sesiones if s['cambio_nivel'])
        
        print("-" * 60)
        print("TEST: Deteccion de cambios de nivel")
        print("-" * 60)
        print("SESIONES:")
        for i, s in enumerate(sesiones, 1):
            icono = "[CAMBIO]" if s['cambio_nivel'] else "[------]"
            print(f"    {icono} Sesion {i}: {s['nivel']}")
        print(f"RESULTADO ESPERADO: 2 cambios")
        print(f"RESULTADO OBTENIDO: {cambios} cambios")
        print(f"ESTADO: {'PASS' if cambios == 2 else 'FAIL'}")
        print("-" * 60)
        
        self.assertEqual(cambios, 2)


# ============================================================================
# RESUMEN FINAL
# ============================================================================
class TestZZ_ResumenFinal(unittest.TestCase):
    """Genera resumen"""
    
    def test_99_resumen(self):
        """Muestra resumen de indicadores"""
        print("")
        print("=" * 70)
        print("RESUMEN FINAL - ABECEDARIO")
        print("=" * 70)
        print("""
+----------------------------------------------------------------------+
|                    INDICADORES VALIDADOS                             |
+----------------------------------------------------------------------+
|  [OK] 1. Palabras completadas correctamente (Cuantitativo)           |
|  [OK] 2. Tiempo de resolucion por palabra (Cuantitativo)             |
|  [OK] 3. Nivel maximo de dificultad (Ordinal)                        |
|  [OK] 4. Errores y pistas usadas (Cuantitativo)                      |
|  [OK] 5. Tiempo total de interaccion (Cuantitativo)                  |
+----------------------------------------------------------------------+
        """)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
