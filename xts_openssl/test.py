import os
from AES import *

key1 = '264E62702662713A7E7D706D777E762E45555A40412934387A606A28402A4B37'
key2 = '264E62702662713A7E7D706D777E762E45555A40412934387A606A28402A4B37'
IV = os.stat('testfile.txt').st_ino

key = (key1, key2)
plaintext = open('testfile.txt').read()

cipher = AES(key, MODE_XTS, IV)
ciphertext = cipher.encrypt(plaintext)
print(ciphertext.encode('hex'))

decipher = AES(key, MODE_XTS, IV)
deciphertext = decipher.decrypt(ciphertext)
print(deciphertext)
