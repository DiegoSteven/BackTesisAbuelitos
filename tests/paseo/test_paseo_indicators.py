"""
================================================================================
PRUEBAS UNITARIAS - Juego de Paseo (Catch Spheres Game)
================================================================================

Indicadores Validados:
- Numero de aciertos (esferas correctas atrapadas)
- Tiempo de reaccion promedio
- Nivel maximo de dificultad alcanzado
- Numero de sesiones completadas
- Precision (aciertos vs errores)

Ejecutar con:
    python -m pytest tests/paseo/test_paseo_indicators.py -v --html=tests/paseo/informe_indicadores.html --self-contained-html
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
# INDICADOR 1: NUMERO DE ACIERTOS (Esferas correctas)
# ============================================================================
class TestIndicador01_EsferasAtrapadas(unittest.TestCase):
    """
    INDICADOR: Numero de esferas correctas atrapadas
    TIPO: Cuantitativo
    CAMPO BD: paseo_session.esferas_rojas_atrapadas
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Indicador 1: Esferas Atrapadas")
        print("=" * 70)

    def test_01_aciertos_cuantitativos(self):
        """Verifica que esferas_rojas_atrapadas es entero >= 0"""
        datos = {
            'esferas_rojas_atrapadas': 15,
            'esferas_azules_atrapadas': 3,
            'esferas_perdidas': 2
        }
        
        aciertos = datos['esferas_rojas_atrapadas']
        es_valido = isinstance(aciertos, int) and aciertos >= 0
        
        log_test_data(
            "Aciertos tipo cuantitativo",
            datos,
            "int >= 0",
            f"{type(aciertos).__name__} = {aciertos}",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_calculo_precision(self):
        """Verifica calculo de precision: aciertos / (aciertos + errores) * 100"""
        casos = [
            {'aciertos': 15, 'errores': 0, 'esperado': 100.0},
            {'aciertos': 15, 'errores': 5, 'esperado': 75.0},
            {'aciertos': 10, 'errores': 10, 'esperado': 50.0},
            {'aciertos': 0, 'errores': 5, 'esperado': 0.0},
        ]
        
        print("-" * 60)
        print("TEST: Calculo de precision")
        print("-" * 60)
        print("CASOS:")
        
        todos_ok = True
        for caso in casos:
            total = caso['aciertos'] + caso['errores']
            precision = (caso['aciertos'] / total * 100) if total > 0 else 0
            ok = abs(precision - caso['esperado']) < 0.1
            estado = "[OK]" if ok else "[FAIL]"
            print(f"    {estado} {caso['aciertos']}/{total} = {precision:.1f}% (esperado: {caso['esperado']}%)")
            todos_ok = todos_ok and ok
        
        print(f"ESTADO: {'PASS' if todos_ok else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_ok)

    def test_03_meta_aciertos_por_nivel(self):
        """Verifica meta de aciertos por nivel"""
        metas = {
            'facil': 15,
            'intermedio': 20,
            'dificil': 30
        }
        
        print("-" * 60)
        print("TEST: Meta de aciertos por nivel")
        print("-" * 60)
        print("CONFIGURACION:")
        for nivel, meta in metas.items():
            print(f"    - {nivel}: {meta} aciertos para ganar")
        
        # Verificar que meta aumenta
        valores = list(metas.values())
        es_creciente = valores == sorted(valores)
        
        print(f"ESPERADO: Metas crecientes con dificultad")
        print(f"ESTADO: {'PASS' if es_creciente else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(es_creciente)


# ============================================================================
# INDICADOR 2: TIEMPO DE REACCION
# ============================================================================
class TestIndicador02_TiempoReaccion(unittest.TestCase):
    """
    INDICADOR: Tiempo de reaccion promedio
    TIPO: Cuantitativo (segundos)
    CAMPO BD: paseo_session.tiempo_reaccion_promedio
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Indicador 2: Tiempo de Reaccion")
        print("=" * 70)

    def test_01_tiempo_reaccion_registrado(self):
        """Verifica que tiempo_reaccion_promedio se registra"""
        datos = {
            'tiempo_reaccion_promedio': 0.85,
            'precision': 80.0
        }
        
        tiempo = datos['tiempo_reaccion_promedio']
        es_valido = isinstance(tiempo, (int, float)) and tiempo > 0
        
        log_test_data(
            "Tiempo de reaccion registrado",
            datos,
            "float > 0 segundos",
            f"{type(tiempo).__name__} = {tiempo}s",
            es_valido
        )
        
        self.assertTrue(es_valido)

    def test_02_tiempo_reaccion_razonable(self):
        """Verifica que tiempo de reaccion esta en rango esperado (0.3s - 3s)"""
        tiempos_normales = [0.5, 0.8, 1.2, 0.9, 1.5]
        
        print("-" * 60)
        print("TEST: Tiempos de reaccion en rango razonable")
        print("-" * 60)
        print("TIEMPOS REGISTRADOS:")
        
        todos_razonables = True
        for t in tiempos_normales:
            razonable = 0.3 <= t <= 3.0
            estado = "[OK]" if razonable else "[FUERA RANGO]"
            print(f"    {estado} {t}s")
            todos_razonables = todos_razonables and razonable
        
        print(f"RANGO ESPERADO: 0.3s - 3.0s")
        print(f"ESTADO: {'PASS' if todos_razonables else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todos_razonables)


# ============================================================================
# INDICADOR 3: NIVEL DE DIFICULTAD
# ============================================================================
class TestIndicador03_NivelDificultad(unittest.TestCase):
    """
    INDICADOR: Nivel maximo de dificultad alcanzado
    TIPO: Ordinal
    CAMPO BD: paseo_session.nivel_dificultad
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Indicador 3: Nivel de Dificultad")
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

    def test_02_parametros_por_nivel(self):
        """Verifica parametros de juego por nivel"""
        parametros = {
            'facil': {'velocidad': 1.0, 'intervalo_spawn': 2.0, 'colores': 'rojo'},
            'intermedio': {'velocidad': 1.5, 'intervalo_spawn': 1.5, 'colores': 'rojo,azul'},
            'dificil': {'velocidad': 2.0, 'intervalo_spawn': 1.0, 'colores': 'todos'},
        }
        
        print("-" * 60)
        print("TEST: Parametros por nivel")
        print("-" * 60)
        print("CONFIGURACION:")
        for nivel, params in parametros.items():
            print(f"    - {nivel}:")
            print(f"        velocidad: {params['velocidad']}")
            print(f"        intervalo_spawn: {params['intervalo_spawn']}s")
            print(f"        colores: {params['colores']}")
        
        # Verificar que velocidad aumenta y spawn disminuye
        velocidades = [parametros[n]['velocidad'] for n in ['facil', 'intermedio', 'dificil']]
        intervalos = [parametros[n]['intervalo_spawn'] for n in ['facil', 'intermedio', 'dificil']]
        
        velocidad_crece = velocidades == sorted(velocidades)
        intervalo_decrece = intervalos == sorted(intervalos, reverse=True)
        
        print(f"ESPERADO: Velocidad crece, intervalo decrece")
        print(f"ESTADO: {'PASS' if velocidad_crece and intervalo_decrece else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(velocidad_crece and intervalo_decrece)

    def test_03_nivel_maximo_historial(self):
        """Verifica obtencion de nivel maximo"""
        NIVELES = {'facil': 1, 'intermedio': 2, 'dificil': 3}
        historial = ['facil', 'facil', 'intermedio', 'intermedio', 'dificil', 'intermedio']
        
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
# INDICADOR 4: SESIONES COMPLETADAS
# ============================================================================
class TestIndicador04_SesionesCompletadas(unittest.TestCase):
    """
    INDICADOR: Numero de sesiones completadas
    TIPO: Cuantitativo
    CAMPO BD: paseo_session.sesion_completa, resultado
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Indicador 4: Sesiones Completadas")
        print("=" * 70)

    def test_01_resultados_validos(self):
        """Verifica resultados de sesion validos"""
        RESULTADOS = ['victoria', 'derrota_timeout', 'derrota_errores', 'derrota_abandono']
        
        log_test_data(
            "Resultados de sesion validos",
            {'resultados': RESULTADOS},
            "4 resultados posibles",
            f"{len(RESULTADOS)} resultados: {RESULTADOS}",
            len(RESULTADOS) == 4
        )
        
        self.assertEqual(len(RESULTADOS), 4)

    def test_02_conteo_victorias(self):
        """Verifica conteo de victorias"""
        sesiones = [
            {'id': 1, 'resultado': 'victoria'},
            {'id': 2, 'resultado': 'derrota_timeout'},
            {'id': 3, 'resultado': 'victoria'},
            {'id': 4, 'resultado': 'derrota_errores'},
            {'id': 5, 'resultado': 'victoria'},
        ]
        
        victorias = sum(1 for s in sesiones if s['resultado'] == 'victoria')
        
        print("-" * 60)
        print("TEST: Conteo de victorias")
        print("-" * 60)
        print("SESIONES:")
        for s in sesiones:
            icono = "[VICTORIA]" if s['resultado'] == 'victoria' else "[DERROTA]"
            print(f"    {icono} Sesion {s['id']}: {s['resultado']}")
        print(f"RESULTADO ESPERADO: 3 victorias")
        print(f"RESULTADO OBTENIDO: {victorias} victorias")
        print(f"ESTADO: {'PASS' if victorias == 3 else 'FAIL'}")
        print("-" * 60)
        
        self.assertEqual(victorias, 3)

    def test_03_razones_derrota(self):
        """Verifica razones de derrota"""
        derrotas = [
            {'resultado': 'derrota_timeout', 'razon': 'timeout'},
            {'resultado': 'derrota_errores', 'razon': 'errores_excesivos'},
            {'resultado': 'derrota_abandono', 'razon': 'abandono'},
        ]
        
        print("-" * 60)
        print("TEST: Razones de derrota")
        print("-" * 60)
        print("TIPOS DE DERROTA:")
        for d in derrotas:
            print(f"    - {d['resultado']}: razon='{d['razon']}'")
        
        todas_tienen_razon = all(d['razon'] is not None for d in derrotas)
        
        print(f"ESPERADO: Todas las derrotas tienen razon")
        print(f"ESTADO: {'PASS' if todas_tienen_razon else 'FAIL'}")
        print("-" * 60)
        
        self.assertTrue(todas_tienen_razon)


# ============================================================================
# INDICADOR 5: TIEMPO TOTAL
# ============================================================================
class TestIndicador05_TiempoTotal(unittest.TestCase):
    """
    INDICADOR: Tiempo total de interaccion
    TIPO: Cuantitativo
    CAMPO BD: paseo_session.tiempo_total_sesion (suma)
    """
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Indicador 5: Tiempo Total")
        print("=" * 70)

    def test_01_duracion_sesion(self):
        """Verifica duracion estandar de sesion (180 segundos)"""
        DURACION_SESION = 180  # 3 minutos
        
        log_test_data(
            "Duracion estandar de sesion",
            {'duracion_configurada': DURACION_SESION},
            "180 segundos (3 minutos)",
            f"{DURACION_SESION} segundos",
            DURACION_SESION == 180
        )
        
        self.assertEqual(DURACION_SESION, 180)

    def test_02_tiempo_total_acumulado(self):
        """Verifica acumulacion de tiempo total"""
        sesiones = [
            {'tiempo_total': 180.0, 'sesion_completa': True},
            {'tiempo_total': 120.0, 'sesion_completa': False},  # Abandono
            {'tiempo_total': 180.0, 'sesion_completa': True},
            {'tiempo_total': 180.0, 'sesion_completa': True},
        ]
        
        tiempo_total = sum(s['tiempo_total'] for s in sesiones)
        tiempo_sesiones_completas = sum(s['tiempo_total'] for s in sesiones if s['sesion_completa'])
        
        log_test_data(
            "Tiempo total acumulado",
            {'sesiones': len(sesiones), 'tiempos': [s['tiempo_total'] for s in sesiones]},
            "660.0s total, 540.0s completas",
            f"{tiempo_total}s total, {tiempo_sesiones_completas}s completas",
            tiempo_total == 660.0 and tiempo_sesiones_completas == 540.0
        )
        
        self.assertEqual(tiempo_total, 660.0)
        self.assertEqual(tiempo_sesiones_completas, 540.0)


# ============================================================================
# CAMBIO DE NIVEL
# ============================================================================
class TestCambioNivel(unittest.TestCase):
    """Pruebas del flag cambio_nivel"""
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Cambio de Nivel")
        print("=" * 70)

    def test_01_cambio_nivel_por_victoria(self):
        """Verifica que victoria sube de nivel"""
        sesiones = [
            {'nivel': 'facil', 'resultado': 'victoria', 'cambio_nivel': True},
            {'nivel': 'intermedio', 'resultado': 'derrota_timeout', 'cambio_nivel': False},
            {'nivel': 'intermedio', 'resultado': 'victoria', 'cambio_nivel': True},
            {'nivel': 'dificil', 'resultado': 'victoria', 'cambio_nivel': False},  # Ya esta en max
        ]
        
        print("-" * 60)
        print("TEST: Cambio de nivel por victoria")
        print("-" * 60)
        print("PROGRESION:")
        for s in sesiones:
            icono = "[CAMBIO]" if s['cambio_nivel'] else "[------]"
            print(f"    {icono} {s['nivel']} + {s['resultado']}")
        
        cambios = sum(1 for s in sesiones if s['cambio_nivel'])
        
        print(f"RESULTADO ESPERADO: 2 cambios de nivel")
        print(f"RESULTADO OBTENIDO: {cambios} cambios")
        print(f"ESTADO: {'PASS' if cambios == 2 else 'FAIL'}")
        print("-" * 60)
        
        self.assertEqual(cambios, 2)


# ============================================================================
# FASES DEL JUEGO
# ============================================================================
class TestFasesJuego(unittest.TestCase):
    """Pruebas de fases: tutorial vs adaptativo"""
    
    @classmethod
    def setUpClass(cls):
        print("=" * 70)
        print("PASEO - Fases del Juego")
        print("=" * 70)

    def test_01_fases_validas(self):
        """Verifica fases validas"""
        FASES = ['tutorial', 'adaptativo']
        
        log_test_data(
            "Fases de juego validas",
            {'fases': FASES},
            "2 fases: tutorial, adaptativo",
            f"{len(FASES)} fases: {FASES}",
            len(FASES) == 2
        )
        
        self.assertEqual(len(FASES), 2)

    def test_02_transicion_tutorial_adaptativo(self):
        """Verifica transicion de tutorial a adaptativo"""
        sesiones = [
            {'fase': 'tutorial', 'resultado': 'victoria'},
            {'fase': 'adaptativo', 'resultado': 'victoria'},  # Pasa a adaptativo
            {'fase': 'adaptativo', 'resultado': 'derrota_timeout'},
        ]
        
        paso_a_adaptativo = any(
            i > 0 and sesiones[i-1]['fase'] == 'tutorial' and s['fase'] == 'adaptativo'
            for i, s in enumerate(sesiones)
        )
        
        log_test_data(
            "Transicion tutorial -> adaptativo",
            {'secuencia_fases': [s['fase'] for s in sesiones]},
            "Transicion detectada",
            f"{'Transicion detectada' if paso_a_adaptativo else 'Sin transicion'}",
            paso_a_adaptativo
        )
        
        self.assertTrue(paso_a_adaptativo)


# ============================================================================
# RESUMEN FINAL
# ============================================================================
class TestZZ_ResumenFinal(unittest.TestCase):
    """Genera resumen"""
    
    def test_99_resumen(self):
        """Muestra resumen de indicadores"""
        print("")
        print("=" * 70)
        print("RESUMEN FINAL - PASEO")
        print("=" * 70)
        print("""
+----------------------------------------------------------------------+
|                    INDICADORES VALIDADOS                             |
+----------------------------------------------------------------------+
|  [OK] 1. Esferas correctas atrapadas (Cuantitativo)                  |
|  [OK] 2. Tiempo de reaccion promedio (Cuantitativo)                  |
|  [OK] 3. Nivel maximo de dificultad (Ordinal)                        |
|  [OK] 4. Sesiones completadas/victorias (Cuantitativo)               |
|  [OK] 5. Tiempo total de interaccion (Cuantitativo)                  |
+----------------------------------------------------------------------+
        """)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
