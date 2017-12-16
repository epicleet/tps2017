import os
from AES_XTS import *

dsk_file = "dsk.img"

key1 = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
offset1 = 512 + 7
offset2 = 512 + 128

dsk_dump = open(dsk_file).read()
k = ord(dsk_dump[offset1])

key2 = ""
for byte in dsk_dump[offset2:offset2 + 32]:
    key2 += chr(ord(byte) ^ k)

key2 = key2.encode("hex")
key = (key1, key2)

for root, dirs, files in os.walk("original"):
    for f in files:
        fname = os.path.join(root, f)
        IV = os.stat(fname).st_ino # change to fname
        plaintext = open(fname).read()
        padsize = 16 - (len(plaintext) % 16)
        plaintext += 'L' * padsize 
        cipher = AES_XTS(key, IV)

        ciphertext = ""
        for i in range(0, len(plaintext), 4096):
            ciphertext += cipher.encrypt(plaintext[i:i+4096])
        
        try:
            os.makedirs("enc/" + root)
        except:
            pass
        open("enc/" + fname, "w").write(ciphertext)
