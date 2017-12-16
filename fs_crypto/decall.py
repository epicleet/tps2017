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

for root, dirs, files in os.walk("enc"):
    for f in files:
        fname = os.path.join(root, f)
        orig_file = fname.replace("enc/", "")

        IV = os.stat(orig_file).st_ino 
        ciphertext = open(fname).read()
        decipher = AES_XTS(key, IV)

        deciphertext = ""
        for i in range(0, len(ciphertext), 4096):
            deciphertext += decipher.decrypt(ciphertext[i:i+4096])
        
        try:
            os.makedirs("dec/" + root)
        except:
            pass
        padsize = len(deciphertext) - len(open(orig_file).read())
        open("dec/" + fname, "w").write(deciphertext[:-padsize])
