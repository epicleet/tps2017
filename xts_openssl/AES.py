from subprocess import Popen, PIPE

MODE_XTS = 7

def string2number(i):
    return int(i.encode('hex'),16)

def number2string_N(i, N):
    s = '%0*x' % (N*2, i)
    return s.decode('hex')

def xorstring(a,b):
    assert len(a) == len(b)
    return number2string_N(string2number(a)^string2number(b), len(a))

class AES():
    def __init__(self, key, mode, IV):
        cipher_module = Codebook
        self.blocksize = 16

        self.key = key
        self.mode = mode

        self.IV =  number2string_N(IV, self.blocksize) # big endian?
        self.ed = None

        self.cipher = cipher_module(self.key[0])
        self.cipher2 = cipher_module(self.key[1])
        self.chain = XTS(self.cipher, self.cipher2)

    def encrypt(self, plaintext):
        self.ed = 'e'
        
        if self.mode == MODE_XTS:
            # data sequence number (or 'tweak') has to be provided when in XTS mode
            return self.chain.update(plaintext, 'e', self.IV)
        else:
            return self.chain.update(plaintext, 'e')

    def decrypt(self, ciphertext):
        self.ed = 'd'

        if self.mode == MODE_XTS:
            # data sequence number (or 'tweak') has to be provided when in XTS mode
            return self.chain.update(ciphertext, 'd', self.IV)
        else:
            return self.chain.update(ciphertext, 'd')

class XTS:
    # TODO: allow other blocksizes besides 16bytes?
    def __init__(self,codebook1, codebook2):
        self.codebook1 = codebook1
        self.codebook2 = codebook2

    def update(self, data, ed,tweak=''):
        # supply n as a raw string
        # tweak = data sequence number
        output = ''
        assert len(data) > 15, "At least one block of 128 bits needs to be supplied"
        assert len(data) < 128*pow(2,20)

        # initializing T
        # e_k2_n = E_K2(tweak)
        e_k2_n = self.codebook2.encrypt(tweak+ '\x00' * (16-len(tweak)))[::-1]
        self.T = string2number(e_k2_n)

        i=0
        while i < ((len(data) // 16)-1): #Decrypt all the blocks but one last full block and opt one last partial block
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
            self.T = self.T ^ 0x100000000000000000000000000000087


class Codebook:
    def __init__(self, key):
        self.key = key

    def aes(self, key, block, mode='-d'):
        if mode == '-d':
            block += block #block should be 256 to work with the command below
        p = Popen(['openssl','enc','-aes-256-ecb',mode,'-K',key.encode('hex')],stdin=PIPE,stdout=PIPE,stderr=open('/dev/null','w'))
        p.stdin.write(block)
        p.stdin.close()
        return p.stdout.read()[:16] #but we ignore last 128 bits

    def decrypt(self, block):
        return self.aes(self.key, block, '-d')

    def encrypt(self, block):
        return self.aes(self.key, block, '-e')
