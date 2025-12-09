from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import base64

# Clave de 8 bytes (requerida por DES)
key = b'-8B key-'
print(f"Clave (key): {key}")

iv = b'12345678'   # 8 bytes exactamente

# Crear el cifrador en modo CBC (genera IV automáticamente)
cipher = DES.new(key, DES.MODE_CBC,iv=iv)
print(f"IV generado automáticamente: {cipher.iv}")

# Texto en claro
plaintext = b'sona si latine loqueris '

print(f"Texto plano (plaintext): {plaintext}")

# Cifrado del texto
ciphertext = cipher.encrypt(plaintext)
print(f"Texto cifrado (ciphertext): {ciphertext}")

# Mensaje final (IV + ciphertext)
msg = cipher.iv + ciphertext
print(f"Mensaje final (msg = IV + ciphertext): {msg}")

# Mostrar longitudes para entender estructura
print(f"Longitud del IV: {len(cipher.iv)} bytes")
print(f"Longitud del ciphertext: {len(ciphertext)} bytes")
print(f"Longitud total (msg): {len(msg)} bytes")

# Versión compatible para copiar/pegar:
print("Mensaje en Base64:", base64.b64encode(msg).decode())
