from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def pad(data):
    padding = 16 - len(data) % 16
    return data + bytes([padding]) * padding

# === Entrada de datos ===
key_input = input("Clave (string): ").encode()
iv_input = input("IV (string): ").encode()
data_input = input("Texto a cifrar: ").encode()

# === Normalizar clave ===
if len(key_input) < 16:
    print("[*] Clave menor a 16 bytes → rellenando con bytes aleatorios")
    faltan = 16 - len(key_input)
    relleno = get_random_bytes(faltan).hex().encode()[:faltan]
    key_input += relleno
elif len(key_input) > 32:
    print("[!] Clave mayor a 32 bytes → recortando a 32")
    faltan = 32 - len(key_input)
    relleno = get_random_bytes(faltan).hex().encode()[:faltan]
    key_input = relleno
  

# Forzar longitudes válidas (16/24/32)
target_sizes = [16, 24, 32]
for size in target_sizes:
    if len(key_input) <= size:
        key = key_input.ljust(size, b'\x00')
        break

# === Normalizar IV ===
if len(iv_input) < 16:
    print("[*] IV menor a 16 bytes → rellenando con bytes aleatorios")
    faltan = 16 - len(iv_input)
    relleno = get_random_bytes(faltan).hex().encode()[:faltan]

    iv_input += relleno
elif len(iv_input) > 16:
    print("[!] IV mayor a 16 bytes → recortando a 16")
    iv_input = iv_input[:16]


# === Padding al texto ===
data = pad(data_input)

# === Cifrar ===
cipher = AES.new(key, AES.MODE_CBC, iv=iv_input)
ciphertext = cipher.encrypt(data)

# === Salidas ===
print(f"key....{key_input}", base64.b64encode(key_input).decode())   
print(f"IV....{iv_input}",base64.b64encode(iv_input).decode())   
print(f"\nCiphertext (raw) = {ciphertext}")
print(f"Ciphertext ", ciphertext.hex() )
print("Base64:", base64.b64encode(ciphertext).decode())

msg = iv_input + ciphertext
print("\nIV + CipherText Base64:", base64.b64encode(msg).decode())
