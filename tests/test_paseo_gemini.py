"""
PRUEBA DE CARGA - PASEO CON GEMINI
===================================
Mide el límite de usuarios concurrentes que soporta la API KEY de Gemini
en el juego de Paseo.

IMPORTANTE:
- Paseo usa Gemini SOLO cuando pierde en nivel DIFICIL
- Esta prueba FUERZA derrotas en DIFICIL para medir capacidad real

Esta prueba es más exigente porque cada derrota hace una llamada a Gemini.
"""

import requests
import time
import concurrent.futures
import json
from datetime import datetime
from typing import List, Dict
import statistics


class PaseoLoadTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'usuarios_creados': 0,
            'sesiones_exitosas': 0,
            'sesiones_fallidas': 0,
            'llamadas_gemini_estimadas': 0,  # Solo en derrotas DIFICIL
            'sesiones_por_nivel': {'facil': 0, 'intermedio': 0, 'dificil': 0, 'tutorial': 0},
            'victorias_dificil': 0,
            'derrotas_dificil': 0,
            'errores_api_key': 0,
            'tiempos_respuesta': [],
            'hora_inicio': None,
            'hora_fin': None
        }
    
    def crear_usuario(self, numero: int) -> Dict:
        """Crea un usuario de prueba"""
        url = f"{self.base_url}/register"
        data = {
            'nombre': f"paseo_test_{numero}_{int(time.time())}",
            'password': 'test123',
            'edad': 65 + (numero % 20),
            'genero': 'masculino' if numero % 2 == 0 else 'femenino'
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 201:
                user_data = response.json()
                print(f"✅ Usuario creado: {data['nombre']} (ID: {user_data['user']['id']})")
                return user_data['user']
            else:
                print(f"❌ Error creando usuario: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Excepción: {str(e)}")
            return None
    
    def jugar_sesion(self, user_id: int, sesion_num: int, forzar_dificil: bool = True) -> Dict:
        """Simula una sesión completa de Paseo"""
        inicio = time.time()
        
        try:
            # 1. Iniciar sesión (puede usar Gemini para decidir nivel)
            url_start = f"{self.base_url}/paseo/start-session"
            response = requests.post(url_start, json={'user_id': user_id}, timeout=30)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Error iniciando sesión: {response.status_code}",
                    'tiempo': time.time() - inicio
                }
            
            plan_data = response.json()
            
            if 'plan' not in plan_data:
                return {
                    'success': False,
                    'error': "Respuesta sin 'plan'",
                    'tiempo': time.time() - inicio
                }
            
            plan = plan_data['plan']
            nivel = plan['nivel_dificultad']
            meta = plan.get('meta_aciertos', 5)
            
            # 2. Simular juego
            time.sleep(0.3)
            
            # 3. Guardar sesión con estrategia para forzar uso de Gemini
            url_save = f"{self.base_url}/paseo/save-session"
            
            if forzar_dificil:
                if nivel != 'dificil':
                    # Subir rápido: victorias perfectas
                    aciertos = meta
                    completado = True
                else:
                    # En DIFICIL: alternar victorias y derrotas para usar Gemini
                    if sesion_num % 3 == 0:  # 1 de cada 3 es derrota
                        aciertos = meta - 2  # Derrota → USA GEMINI
                        completado = False
                    else:
                        aciertos = meta  # Victoria
                        completado = True
            else:
                aciertos = meta
                completado = True
            
            session_data = {
                'user_id': user_id,
                'nivel_dificultad': nivel,
                'meta_aciertos': meta,
                'total_aciertos': aciertos,
                'total_errores_incorrecto': 1 if not completado else 0,
                'total_errores_perdidas': 1 if not completado else 0,
                'duracion_total': plan.get('duracion_estimada', 60),
                'completado': completado,
                'velocidad_esferas': plan.get('velocidad', 3.0),
                'intervalo_spawn': plan.get('intervalo', 2.0),
                'colores_activos': 'rojo',
                'color_correcto': 'rojo'
            }
            
            response = requests.post(url_save, json=session_data, timeout=10)
            
            tiempo_total = time.time() - inicio
            
            if response.status_code in [200, 201]:
                # Gemini se usa SOLO en derrotas de nivel DIFICIL
                usa_gemini = (nivel == 'dificil' and not completado)
                
                return {
                    'success': True,
                    'tiempo': tiempo_total,
                    'nivel': nivel,
                    'completado': completado,
                    'usa_gemini': usa_gemini
                }
            else:
                return {
                    'success': False,
                    'error': f"Error guardando sesión: {response.status_code}",
                    'tiempo': tiempo_total
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout',
                'tiempo': time.time() - inicio
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tiempo': time.time() - inicio
            }
    
    def test_limite_usuarios_concurrentes(self, num_usuarios: int, sesiones_por_usuario: int):
        """
        Prueba el límite de usuarios concurrentes que soporta Gemini
        Fuerza derrotas en DIFICIL para máximo uso de Gemini
        """
        print(f"\n{'='*70}")
        print(f"🎯 PRUEBA DE LÍMITE - PASEO")
        print(f"{'='*70}")
        print(f"👥 Usuarios concurrentes: {num_usuarios}")
        print(f"🎮 Sesiones por usuario: {sesiones_por_usuario}")
        print(f"⚡ Modo: FORZAR DERROTAS EN DIFICIL (máximo uso de Gemini)")
        print(f"{'='*70}\n")
        
        self.results['hora_inicio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Crear usuarios
        print("📝 Creando usuarios...\n")
        usuarios = []
        for i in range(num_usuarios):
            user = self.crear_usuario(i)
            if user:
                usuarios.append(user)
                self.results['usuarios_creados'] += 1
            time.sleep(0.1)
        
        if not usuarios:
            print("❌ No se pudieron crear usuarios")
            return
        
        print(f"\n✅ {len(usuarios)} usuarios creados\n")
        print(f"🎮 Iniciando sesiones concurrentes...\n")
        
        # 2. Función para cada usuario
        def jugar_usuario(user_info):
            user_id = user_info['id']
            resultados = []
            
            for sesion_num in range(sesiones_por_usuario):
                resultado = self.jugar_sesion(user_id, sesion_num, forzar_dificil=True)
                resultados.append(resultado)
                
                if resultado['success']:
                    nivel = resultado.get('nivel', '?')
                    gemini = "🤖" if resultado.get('usa_gemini', False) else "💾"
                    victoria = "✓" if resultado.get('completado', True) else "✗"
                    print(f"  ✅ User {user_id} - Sesión {sesion_num+1:2d} [{nivel:10s}] {victoria} {gemini}: {resultado['tiempo']:.2f}s")
                else:
                    print(f"  ❌ User {user_id} - Sesión {sesion_num+1:2d}: {resultado.get('error', 'Error')}")
                
                time.sleep(0.2)
            
            return resultados
        
        # 3. Ejecutar en paralelo
        inicio = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_usuarios) as executor:
            futures = [executor.submit(jugar_usuario, user) for user in usuarios]
            todos_resultados = []
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    todos_resultados.extend(future.result())
                except Exception as e:
                    print(f"❌ Error en thread: {str(e)}")
        
        tiempo_total = time.time() - inicio
        
        # 4. Procesar resultados
        for resultado in todos_resultados:
            if resultado['success']:
                self.results['sesiones_exitosas'] += 1
                self.results['tiempos_respuesta'].append(resultado['tiempo'])
                
                nivel = resultado.get('nivel', 'facil')
                if nivel in self.results['sesiones_por_nivel']:
                    self.results['sesiones_por_nivel'][nivel] += 1
                
                if nivel == 'dificil':
                    if resultado.get('completado', True):
                        self.results['victorias_dificil'] += 1
                    else:
                        self.results['derrotas_dificil'] += 1
                
                if resultado.get('usa_gemini', False):
                    self.results['llamadas_gemini_estimadas'] += 1
            else:
                self.results['sesiones_fallidas'] += 1
                if 'rate' in resultado.get('error', '').lower() or '429' in resultado.get('error', ''):
                    self.results['errores_api_key'] += 1
        
        self.results['hora_fin'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 5. Mostrar resultados
        self._mostrar_resultados(tiempo_total)
    
    def _mostrar_resultados(self, tiempo_total: float):
        """Muestra resumen de resultados"""
        print(f"\n{'='*70}")
        print("📊 RESULTADOS DE LA PRUEBA")
        print(f"{'='*70}")
        
        print(f"\n⏱️  TIEMPO:")
        print(f"  • Inicio:     {self.results['hora_inicio']}")
        print(f"  • Fin:        {self.results['hora_fin']}")
        print(f"  • Duración:   {tiempo_total:.2f} segundos")
        
        print(f"\n👥 USUARIOS:")
        print(f"  • Creados:    {self.results['usuarios_creados']}")
        
        print(f"\n🎮 SESIONES:")
        total = self.results['sesiones_exitosas'] + self.results['sesiones_fallidas']
        print(f"  • Total:      {total}")
        print(f"  • Exitosas:   {self.results['sesiones_exitosas']} ({self.results['sesiones_exitosas']/total*100:.1f}%)")
        print(f"  • Fallidas:   {self.results['sesiones_fallidas']} ({self.results['sesiones_fallidas']/total*100:.1f}%)")
        
        print(f"\n📊 POR NIVEL:")
        for nivel, count in self.results['sesiones_por_nivel'].items():
            if count > 0:
                emoji = "💾" if nivel != 'dificil' else "🤖"
                print(f"  • {nivel.capitalize():12s} {emoji}: {count} sesiones")
        
        print(f"\n🎯 NIVEL DIFICIL:")
        print(f"  • Victorias:  {self.results['victorias_dificil']}")
        print(f"  • Derrotas:   {self.results['derrotas_dificil']} (cada una usa Gemini)")
        
        print(f"\n🤖 USO DE GEMINI:")
        print(f"  • Llamadas estimadas: {self.results['llamadas_gemini_estimadas']}")
        print(f"  • (1 llamada por cada derrota en DIFICIL)")
        
        print(f"\n❌ ERRORES:")
        print(f"  • API KEY límite:     {self.results['errores_api_key']}")
        
        if self.results['tiempos_respuesta']:
            print(f"\n⚡ TIEMPOS DE RESPUESTA:")
            print(f"  • Promedio:   {statistics.mean(self.results['tiempos_respuesta']):.2f}s")
            print(f"  • Mínimo:     {min(self.results['tiempos_respuesta']):.2f}s")
            print(f"  • Máximo:     {max(self.results['tiempos_respuesta']):.2f}s")
        
        print(f"\n{'='*70}")
        
        # Guardar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_paseo_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {filename}")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     PRUEBA DE CARGA - PASEO CON GEMINI                        ║
║     Mide el límite de usuarios que soporta la API KEY         ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  IMPORTANTE:
- Paseo usa Gemini SOLO en derrotas de nivel DIFICIL
- Esta prueba fuerza derrotas para máximo uso de Gemini
- Cada derrota en DIFICIL = 1 llamada a Gemini

🎯 OBJETIVO:
Determinar cuántos usuarios concurrentes pueden jugar
simultáneamente sin saturar la API KEY de Gemini.

""")
    
    tester = PaseoLoadTester()
    
    print("Configuración de la prueba:")
    num_usuarios = int(input("¿Cuántos usuarios concurrentes? (recomendado: 10-30): "))
    sesiones = int(input("¿Cuántas sesiones por usuario? (mínimo 10 para DIFICIL): "))
    
    if sesiones < 10:
        print("\n⚠️  Con menos de 10 sesiones puede no alcanzar nivel DIFICIL")
        continuar = input("¿Continuar? (s/N): ").strip().lower()
        if continuar != 's':
            print("Prueba cancelada.")
            return
    
    print(f"\n⚡ Iniciando prueba con {num_usuarios} usuarios, {sesiones} sesiones cada uno...")
    input("Presiona ENTER para continuar...")
    
    tester.test_limite_usuarios_concurrentes(num_usuarios, sesiones)


if __name__ == "__main__":
    print("\n🔧 Asegúrate de que el backend esté corriendo en http://localhost:5000")
    input("Presiona ENTER para continuar...")
    main()
