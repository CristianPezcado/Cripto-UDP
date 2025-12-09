from Crypto.Cipher import AES
import base64


key = b'Sixteen byte key'

iv=b'iLXCYfm9rd2E7wU8'

data=b'sona si latine l'

cipher = AES.new(key, AES.MODE_CBC,iv=iv)

textoC= cipher.encrypt(data)

print(f" texto cifrado = {textoC}")

print("Mensaje en Base64:", base64.b64encode(textoC).decode())

msg= cipher.iv + textoC

print("Mensaje IV en Base64:", base64.b64encode(msg).decode())




