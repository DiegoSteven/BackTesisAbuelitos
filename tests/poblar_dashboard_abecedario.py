"""
SCRIPT DE PRUEBA - Poblar Abecedario con Datos de Múltiples Días
================================================================
Este script crea un usuario y le genera sesiones en diferentes días
para verificar cómo se visualiza en el dashboard.
"""

import requests
import time
from datetime import date, timedelta
import random


BASE_URL = "http://localhost:5000"


def crear_usuario_prueba():
    """Crea un usuario de prueba"""
    timestamp = int(time.time())
    nombre = f"prueba_dashboard_{timestamp}"
    
    data = {
        'nombre': nombre,
        'password': 'test123',
        'edad': 70,
        'genero': 'femenino'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=data, timeout=10)
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data['user']['id']
            print(f"✅ Usuario creado: {nombre} (ID: {user_id})")
            return user_id, nombre
        else:
            print(f"❌ Error creando usuario: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return None, None


def jugar_palabra(user_id, fecha_juego, forzar_completado=None):
    """
    Juega una palabra individual
    
    Args:
        user_id: ID del usuario
        fecha_juego: Fecha en formato YYYY-MM-DD
        forzar_completado: True/False para forzar el resultado, None para aleatorio
    """
    try:
        # 1. Obtener desafío
        response = requests.get(f"{BASE_URL}/abecedario/next-challenge/{user_id}", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo desafío: {response.status_code}")
            return False
            
        challenge_data = response.json()
        palabra = challenge_data['challenge'].get('palabra_objetivo')
        nivel_actual = challenge_data['challenge'].get('nivel_dificultad', 'facil')
        
        # 2. Simular juego
        # Si forzar_completado está especificado, usarlo; sino, usar lógica aleatoria
        if forzar_completado is not None:
            completado = forzar_completado
        else:
            # Lógica aleatoria basada en nivel
            if nivel_actual == 'facil':
                completado = random.random() < 0.85
            elif nivel_actual == 'intermedio':
                completado = random.random() < 0.75
            else:  # dificil
                completado = random.random() < 0.70
        
        # Ajustar métricas según si completó o no
        if completado:
            if nivel_actual == 'facil':
                errores = random.randint(0, 2)
                tiempo = random.uniform(10, 20)
                pistas = random.randint(0, 1)
            elif nivel_actual == 'intermedio':
                errores = random.randint(1, 3)
                tiempo = random.uniform(15, 28)
                pistas = random.randint(0, 2)
            else:  # dificil
                errores = random.randint(1, 4)
                tiempo = random.uniform(20, 35)
                pistas = random.randint(1, 2)
        else:
            # Falló: más errores, más tiempo
            if nivel_actual == 'facil':
                errores = random.randint(3, 5)
                tiempo = random.uniform(15, 25)
                pistas = random.randint(1, 2)
            elif nivel_actual == 'intermedio':
                errores = random.randint(4, 6)
                tiempo = random.uniform(25, 35)
                pistas = random.randint(2, 3)
            else:  # dificil
                errores = random.randint(5, 8)
                tiempo = random.uniform(30, 45)
                pistas = random.randint(2, 4)
        
        # 3. Guardar sesión CON FECHA ESPECÍFICA
        session_data = {
            'user_id': user_id,
            'palabra_objetivo': palabra,
            'tiempo_resolucion': round(tiempo, 1),
            'cantidad_errores': errores,
            'pistas_usadas': pistas,
            'completado': completado,
            'nivel_dificultad': nivel_actual,
            'fecha_juego': fecha_juego
        }
        
        response = requests.post(f"{BASE_URL}/abecedario/session", json=session_data, timeout=10)
        
        if response.status_code in [200, 201]:
            estado = "✅" if completado else "❌"
            nivel_emoji = {"facil": "🟢", "intermedio": "🟡", "dificil": "🔴"}.get(nivel_actual, "⚪")
            print(f"  {estado} {nivel_emoji} {nivel_actual.upper():10s} | {palabra:15s} | {tiempo:.1f}s | {errores} err")
            return completado  # Retornar si fue exitosa
        else:
            print(f"❌ Error guardando sesión: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def poblar_datos_multiples_dias(user_id):
    """Genera datos de prueba en 5 días diferentes con PROGRESIÓN DE NIVEL"""
    
    # Generar 5 fechas (hoy hacia atrás)
    hoy = date.today()
    fechas = [
        (hoy - timedelta(days=4)).isoformat(),  # Hace 4 días
        (hoy - timedelta(days=3)).isoformat(),  # Hace 3 días
        (hoy - timedelta(days=2)).isoformat(),  # Hace 2 días
        (hoy - timedelta(days=1)).isoformat(),  # Ayer
        hoy.isoformat()                          # Hoy
    ]
    
    # Estrategia de progresión:
    # Día 1: FACIL - Buen rendimiento (para subir)
    # Día 2: FACIL → INTERMEDIO (necesita 5+ palabras con >70% precisión)
    # Día 3: INTERMEDIO - Buen rendimiento
    # Día 4: INTERMEDIO → DIFICIL
    # Día 5: DIFICIL - Se mantiene
    
    estrategia_dias = [
        {'nombre': 'DÍA 1 - Aprendiendo FACIL', 'palabras': 12, 'tasa_exito_objetivo': 0.90},
        {'nombre': 'DÍA 2 - Dominando FACIL (Subir a INT)', 'palabras': 15, 'tasa_exito_objetivo': 0.88},
        {'nombre': 'DÍA 3 - Progresando en INTERMEDIO', 'palabras': 14, 'tasa_exito_objetivo': 0.80},
        {'nombre': 'DÍA 4 - Dominando INT (Subir a DIF)', 'palabras': 16, 'tasa_exito_objetivo': 0.82},
        {'nombre': 'DÍA 5 - Desafío DIFICIL', 'palabras': 12, 'tasa_exito_objetivo': 0.75}
    ]
    
    print("\n" + "="*70)
    print("📅 GENERANDO DATOS CON PROGRESIÓN DE NIVELES")
    print("="*70)
    print("\nEstrategia:")
    print("  Día 1: Buen rendimiento en FACIL")
    print("  Día 2: Subir a INTERMEDIO (necesita 5+ completadas con >70% precisión)")
    print("  Día 3: Consolidar INTERMEDIO")
    print("  Día 4: Subir a DIFICIL")
    print("  Día 5: Mantenerse en DIFICIL")
    
    for dia_num, (fecha, estrategia) in enumerate(zip(fechas, estrategia_dias), 1):
        print(f"\n📆 {estrategia['nombre']} ({fecha})")
        print("-" * 70)
        
        num_palabras = estrategia['palabras']
        tasa_exito = estrategia['tasa_exito_objetivo']
        
        # Jugar con rendimiento controlado para permitir progresión
        exitosas = 0
        for i in range(num_palabras):
            # Decidir si esta palabra será exitosa según la tasa objetivo
            debe_completar = random.random() < tasa_exito
            
            # Jugar la palabra forzando el resultado
            resultado = jugar_palabra(user_id, fecha, forzar_completado=debe_completar)
            if resultado:
                exitosas += 1
            time.sleep(0.2)
        
        precision = (exitosas / num_palabras * 100) if num_palabras > 0 else 0
        print(f"  ✅ Día {dia_num} completado: {num_palabras} palabras | {exitosas} exitosas ({precision:.1f}%)")
        
        if dia_num < 5:
            time.sleep(0.5)


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║   SCRIPT DE PRUEBA - POBLAR DASHBOARD                         ║
║   Genera datos de Abecedario en múltiples días                ║
╚═══════════════════════════════════════════════════════════════╝

Este script crea un usuario y genera sesiones en 5 días diferentes
para verificar cómo se visualiza en el dashboard.

Estructura esperada en el dashboard:
  📅 Sesión: 2026-01-14
    ├── 🟢 FACIL (4 palabras)
    ├── 🟡 INTERMEDIO (2 palabras)
    └── 🔴 DIFICIL (1 palabra)
  
  📅 Sesión: 2026-01-15
    ├── 🟢 FACIL (3 palabras)
    └── 🟡 INTERMEDIO (5 palabras)
  ...

""")
    
    # Verificar que el backend esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Backend conectado\n")
    except:
        print("❌ Error: Backend no está corriendo en http://localhost:5000")
        print("   Por favor, inicia el backend antes de ejecutar este script.\n")
        return
    
    # Crear usuario
    user_id, user_name = crear_usuario_prueba()
    if not user_id:
        print("❌ No se pudo crear el usuario")
        return
    
    # Generar datos
    input("\nPresiona ENTER para generar datos de prueba...")
    poblar_datos_multiples_dias(user_id)
    
    # Resumen
    print("\n" + "="*70)
    print("✅ DATOS GENERADOS EXITOSAMENTE")
    print("="*70)
    print(f"\n📊 Usuario de prueba: {user_name} (ID: {user_id})")
    print(f"📅 Días con sesiones: 5 (desde hace 4 días hasta hoy)")
    print(f"🎮 Total aproximado: 35-50 palabras jugadas")
    
    print(f"\n🌐 Pasos para verificar en el dashboard:")
    print(f"   1. Abre el dashboard: http://localhost:5173")
    print(f"   2. Ve a la pestaña 'Usuarios'")
    print(f"   3. Busca el usuario: {user_name}")
    print(f"   4. Haz clic en el card 'Abecedario'")
    print(f"   5. Deberías ver las sesiones agrupadas por fecha")
    print(f"   6. Cada sesión muestra niveles expandibles")
    print(f"   7. Cada nivel muestra las palabras jugadas")
    
    print(f"\n💡 Qué verificar:")
    print(f"   ✅ Total Sesiones = 5")
    print(f"   ✅ Palabras Completadas = ~30-40")
    print(f"   ✅ Nivel Alcanzado = FACIL/INTERMEDIO/DIFICIL")
    print(f"   ✅ Sesiones ordenadas por fecha (más reciente primero)")
    print(f"   ✅ Desplegables funcionan correctamente")
    print(f"   ✅ Métricas se calculan bien (tiempo, errores, pistas)")


if __name__ == "__main__":
    print("\n🔧 Asegúrate de que el backend esté corriendo en http://localhost:5000")
    input("Presiona ENTER para continuar...")
    main()
