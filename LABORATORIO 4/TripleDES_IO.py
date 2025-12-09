from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
import base64

# === Entrada de datos ===
key_input = input("Clave (mínimo 16 o 24 bytes para 3DES): ").encode()
iv_input = input("IV (8 bytes): ").encode()
plaintext = input("Texto a cifrar: ").encode()

# === Ajustar la clave ===
# Clave válida en 3DES: 16 ó 24 bytes
original_len = len(key_input)

if original_len < 16:
    print("[*] Clave menor a 16 → rellenando con bytes hex uniformes")
    faltan = 16 - original_len
    relleno = get_random_bytes(faltan).hex().encode()[:faltan]
    key_input += relleno

elif 16 <= original_len < 24:
    print("[*] Expandimos clave a 24 bytes → rellenando con bytes hex uniformes")
    faltan = 24 - original_len
    relleno = get_random_bytes(faltan).hex().encode()[:faltan]
    key_input += relleno

if len(key_input) > 24:
    print("[!] Clave mayor a 24 → recortando")
    key_input = key_input[:24]

# === Ajustar paridad (requisito 3DES) ===
try:
    key = DES3.adjust_key_parity(key_input)
except ValueError:
    print("[!] La clave no cumple paridad, generando una válida")
    while True:
        try:
            key = DES3.adjust_key_parity(get_random_bytes(24))
            break
        except ValueError:
            pass

print(f"Clave final usada (hex-friendly): {key}")

# === Normalizar IV ===
if len(iv_input) < 8:
    print("[*] IV menor a 8 → rellenando con hex")
    faltan = 8 - len(iv_input)
    relleno = get_random_bytes(faltan).hex().encode()[:faltan]
    iv_input += relleno
elif len(iv_input) > 8:
    print("[!] IV mayor → recortando")
    iv_input = iv_input[:8]

iv = iv_input
print(f"IV usado: {iv}")

# === Crear cifrador (CFB no requiere padding) ===
cipher = DES3.new(key, DES3.MODE_CFB, iv=iv)

# === Cifrar ===
print(f"Texto plano padded: {plaintext}")
ciphertext = cipher.encrypt(plaintext)


# === Construcción final ===
msg = iv + ciphertext

print("\nCiphertext raw (bytes):", ciphertext)
print(f"Ciphertext ", ciphertext.hex() )

print("Mensaje (IV + ciphertext):", msg)


# === Mostrar salidas ===

print("\nMensaje (IV + ciphertext) en Base64:")
print(base64.b64encode(msg).decode())
