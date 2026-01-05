"""
PRUEBA DE CARGA - ABECEDARIO CON GEMINI
========================================
Mide el límite de usuarios concurrentes que soporta la API KEY de Gemini
en el juego de Abecedario.

IMPORTANTE:
- Niveles FACIL/INTERMEDIO: Usan JSON local (NO gastan Gemini)
- Nivel DIFICIL: Usa Gemini en lotes de 20 palabras (SÍ gasta Gemini)

Esta prueba FUERZA nivel DIFICIL para medir capacidad real de la API KEY.
"""

import requests
import time
import concurrent.futures
import json
from datetime import datetime
from typing import List, Dict
import statistics


class AbecedarioLoadTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'usuarios_creados': 0,
            'sesiones_exitosas': 0,
            'sesiones_fallidas': 0,
            'llamadas_gemini_estimadas': 0,  # Solo en nivel DIFICIL
            'sesiones_por_nivel': {'facil': 0, 'intermedio': 0, 'dificil': 0},
            'errores_api_key': 0,
            'tiempos_respuesta': [],
            'hora_inicio': None,
            'hora_fin': None
        }
    
    def crear_usuario(self, numero: int) -> Dict:
        """Crea un usuario de prueba"""
        url = f"{self.base_url}/register"
        data = {
            'nombre': f"abc_test_{numero}_{int(time.time())}",
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
        """Simula una sesión completa de Abecedario"""
        inicio = time.time()
        
        try:
            # 1. Obtener desafío (puede usar Gemini en DIFICIL)
            url_challenge = f"{self.base_url}/abecedario/next-challenge/{user_id}"
            response = requests.get(url_challenge, timeout=30)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Error obteniendo desafío: {response.status_code}",
                    'tiempo': time.time() - inicio
                }
            
            challenge_data = response.json()
            
            if 'challenge' not in challenge_data:
                return {
                    'success': False,
                    'error': "Respuesta sin 'challenge'",
                    'tiempo': time.time() - inicio
                }
            
            palabra = challenge_data['challenge'].get('palabra_objetivo')
            nivel = challenge_data['challenge'].get('nivel_dificultad', 'facil')
            
            if not palabra:
                return {
                    'success': False,
                    'error': "No se recibió palabra",
                    'tiempo': time.time() - inicio
                }
            
            # 2. Simular juego
            time.sleep(0.3)
            
            # 3. Guardar sesión
            url_save = f"{self.base_url}/abecedario/session"
            
            # Si forzar_dificil = True, hacer victorias perfectas para subir rápido
            if forzar_dificil and nivel != 'dificil':
                completado = True
                errores = 0
                tiempo = 8
            else:
                completado = True
                errores = 0
                tiempo = 12 + (sesion_num % 5)
            
            session_data = {
                'user_id': user_id,
                'palabra_objetivo': palabra,
                'tiempo_resolucion': tiempo,
                'cantidad_errores': errores,
                'pistas_usadas': 0,
                'completado': completado,
                'nivel_dificultad': nivel
            }
            
            response = requests.post(url_save, json=session_data, timeout=10)
            
            tiempo_total = time.time() - inicio
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'tiempo': tiempo_total,
                    'nivel': nivel,
                    'usa_gemini': nivel == 'dificil'  # Solo DIFICIL usa Gemini
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
        Cada usuario juega hasta llegar a nivel DIFICIL
        """
        print(f"\n{'='*70}")
        print(f"🔤 PRUEBA DE LÍMITE - ABECEDARIO")
        print(f"{'='*70}")
        print(f"👥 Usuarios concurrentes: {num_usuarios}")
        print(f"🎮 Sesiones por usuario: {sesiones_por_usuario}")
        print(f"⚡ Modo: FORZAR NIVEL DIFICIL (máximo uso de Gemini)")
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
                    print(f"  ✅ User {user_id} - Sesión {sesion_num+1:2d} [{nivel:10s}] {gemini}: {resultado['tiempo']:.2f}s")
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
                emoji = "💾" if nivel in ['facil', 'intermedio'] else "🤖"
                print(f"  • {nivel.capitalize():12s} {emoji}: {count} sesiones")
        
        print(f"\n🤖 USO DE GEMINI:")
        print(f"  • Sesiones DIFICIL:   {self.results['sesiones_por_nivel']['dificil']}")
        print(f"  • Llamadas estimadas: ~{self.results['llamadas_gemini_estimadas']} (batch de 20)")
        print(f"  • Llamadas reales:    ~{max(1, self.results['llamadas_gemini_estimadas'] // 20)}")
        
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
        filename = f"test_abecedario_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {filename}")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     PRUEBA DE CARGA - ABECEDARIO CON GEMINI                   ║
║     Mide el límite de usuarios que soporta la API KEY         ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  IMPORTANTE:
- Esta prueba FUERZA nivel DIFICIL para máximo uso de Gemini
- Nivel DIFICIL usa Gemini en lotes de 20 palabras
- Se necesitan ~10-15 sesiones para llegar a DIFICIL

🎯 OBJETIVO:
Determinar cuántos usuarios concurrentes pueden jugar
simultáneamente sin saturar la API KEY de Gemini.

""")
    
    tester = AbecedarioLoadTester()
    
    print("Configuración de la prueba:")
    num_usuarios = int(input("¿Cuántos usuarios concurrentes? (recomendado: 10-30): "))
    sesiones = int(input("¿Cuántas sesiones por usuario? (mínimo 15 para DIFICIL): "))
    
    if sesiones < 15:
        print("\n⚠️  Con menos de 15 sesiones puede no alcanzar nivel DIFICIL")
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
