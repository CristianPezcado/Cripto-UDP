from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64

# === Entrada de datos ===
key_input = input("Clave (mínimo 8 bytes): ").encode()
iv_input = input("IV (8 bytes): ").encode()
plaintext = input("Texto a cifrar: ").encode()

# === Normalizar clave (8 bytes total) ===
if len(key_input) < 8:
    print("[*] Clave menor a 8 → rellenando con bytes aleatorios")
    key_input += get_random_bytes(8 - len(key_input))
elif len(key_input) > 8:
    print("[!] Clave mayor a 8 → recortando")
    key_input = key_input[:8]

key = key_input
print(f"Clave usada: {key}")

# === Normalizar IV ===
if len(iv_input) < 8:
    print("[*] IV menor a 8 → rellenando")
    iv_input += get_random_bytes(8 - len(iv_input))
elif len(iv_input) > 8:
    print("[!] IV mayor → recortando")
    iv_input = iv_input[:8]

iv = iv_input
print(f"IV usado: {iv}")

# === Padding PKCS7 ===
plaintext = pad(plaintext, DES.block_size)

print(f"Texto plano padded: {plaintext}")

# === Cifrado ===
cipher = DES.new(key, DES.MODE_CBC, iv=iv)
ciphertext = cipher.encrypt(plaintext)

print(f"Ciphertext (raw): {ciphertext}")
print(f"Ciphertext ", ciphertext.hex() )


# === Construcción final IV + ciphertext ===
msg = iv + ciphertext

# === Mostrar longitudes ===
print(f"Longitud del IV: {len(iv)} bytes")
print(f"Longitud del ciphertext: {len(ciphertext)} bytes")
print(f"Longitud total: {len(msg)} bytes")

# === Base64 exportable ===
print("\nMensaje (IV + ciphertext) en Base64:")
print(base64.b64encode(msg).decode())
