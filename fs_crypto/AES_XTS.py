from subprocess import Popen, PIPE
import struct
from Crypto.Cipher import AES

BLOCK_SIZE = 16

def string2number(i):
    return int(i.encode('hex'),16)

def number2string_N(i, N):
    s = '%0*x' % (N*2, i)
    return s.decode('hex')

def xorstring(a,b):
    return number2string_N(string2number(a)^string2number(b), len(a))

class AES_XTS():
    def __init__(self, key, IV):
        cipher_module = Codebook

        self.key = key
        self.IV = struct.pack("I", IV) + "\x00"*(BLOCK_SIZE - 4)

        self.cipher = cipher_module(self.key[0])
        self.cipher2 = cipher_module(self.key[1])
        self.chain = XTS(self.cipher, self.cipher2)

    def encrypt(self, plaintext):
        return self.chain.update(plaintext, 'e', self.IV)

    def decrypt(self, ciphertext):
        return self.chain.update(ciphertext, 'd', self.IV)

class XTS:
    def __init__(self,codebook1, codebook2):
        self.codebook1 = codebook1
        self.codebook2 = codebook2

    def update(self, data, ed,tweak=''):
        output = ''
        
        # initializing T
        # e_k2_n = E_K2(tweak)
        e_k2_n = self.codebook2.encrypt(tweak+ '\x00' * (16-len(tweak)))[::-1]
        self.T = string2number(e_k2_n)

        i=0
        while i < ((len(data) // 16)-1):
            # C = E_K1(P xor T) xor T
            output += self.__xts_step(ed, data[i*16:(i+1)*16], self.T)
            # T = E_K2(n) mul (a pow i)
            self.__T_update()
            i+=1

        # Check if the data supplied is a multiple of 16 bytes -> one last full block and we're done
        if len(data[i*16:]) == 16:
            # C = E_K1(P xor T) xor T
            output += self.__xts_step(ed,data[i*16:(i+1)*16],self.T)
            # T = E_K2(n) mul (a pow i)
            self.__T_update()
        else:
            T_temp = [self.T]
            self.__T_update()
            T_temp.append(self.T)
            if ed=='d':
                # Permutation of the last two indexes
                T_temp.reverse()

            # Decrypt/Encrypt the last two blocks when data is not a multiple of 16 bytes
            Cm1 = data[i*16:(i+1)*16]
            Cm = data[(i+1)*16:]
            PP = self.__xts_step(ed,Cm1,T_temp[0])
            Cp = PP[len(Cm):]
            Pm = PP[:len(Cm)]
            CC = Cm+Cp
            Pm1 = self.__xts_step(ed,CC,T_temp[1])
            output += Pm1 + Pm
        return output

    def __xts_step(self, ed, tocrypt, T):
        T_string = number2string_N(T,16)[::-1]
        # C = E_K1(P xor T) xor T
        if ed == 'd':
            return xorstring(T_string, self.codebook1.decrypt(xorstring(T_string, tocrypt)))
        else:
            return xorstring(T_string, self.codebook1.encrypt(xorstring(T_string, tocrypt)))

    def __T_update(self):
        # Used for calculating T for a certain step using the T value from the previous step
        self.T = self.T << 1
        if self.T >> (8*16):
            #T[0] ^= GF_128_FDBK;
            self.T = self.T ^ 0x100000000000000000000000000000087L


class Codebook:
    def __init__(self, key):
        self.mykey = key
        self.aes_ecb = AES.new(key.decode("hex"), AES.MODE_ECB)

    def aes(self, block, mode='-d'):

        if mode == '-d':
            res = self.aes_ecb.decrypt(block)
        else:
            res = self.aes_ecb.encrypt(block)
        return res

    def decrypt(self, block):
        return self.aes(block, '-d')

    def encrypt(self, block):
        return self.aes(block, '-e')
