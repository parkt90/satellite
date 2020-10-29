import json, hashlib, random, time, hmac
from crypty_helper.xor import *
from crypty_helper.AES_use import *
from crypty_helper.DES_use import *
from crypty_helper.DES_3_use import *

def getHash(msg):
    # options = get_options()
    # if options['Hash_option'] == 1: # sha1
        # return hashlib.sha1(msg).hexdigest()
    # elif options['Hash_option'] == 2: # sha256
        # return hashlib.sha256(msg).hexdigest()
    # elif options['Hash_option'] == 3: # sha512
        return hashlib.sha512(msg).hexdigest()

def getRandom():
    # options = get_options()
    # if options['Len_Ru'] == 1: # 16 duan
        return random.randint(1000000000000000, 9999999999999999)
    # elif options['Len_Ru'] == 2: # 32 jiaochang
        # return random.randint(10000000000000000000000000000000, 99999999999999999999999999999999)
    # elif options['Len_Ru'] == 3: # 48 chang
        # return random.randint(100000000000000000000000000000000000000000000000, 999999999999999999999999999999999999999999999999)

if __name__ == '__main__':
    timestamp = int(time.time())
    Ru = getRandom()
    userId = "8fdd279fa23da935ab2b1edb96897598039517b0"
    msg = getHash(str(userId) + str(Ru) +str(timestamp))
    print msg
    # return msg
