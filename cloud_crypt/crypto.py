
from pathlib import Path, PurePath
import sys
from cryptography.fernet import Fernet

# TODO make configurable
AES_BLOCK_SIZE = 16
CHUNK_SIZE = 100 * AES_BLOCK_SIZE
TOKEN_SIZE = 57 + CHUNK_SIZE # (8+64+128+256)/8 = 57 bytes see below

# TOKEN structure
# Version ‖ Timestamp ‖ IV ‖ Ciphertext ‖ HMAC
# Version, 8 bits
# Timestamp, 64 bits
# IV, 128 bits
# Ciphertext, variable length, multiple of 128 bits
# HMAC, 256 bits


def encrypt_file(f_in : PurePath, f_out: PurePath, key : bytes):

    f = Fernet(key)
    print('encrypt')
    iter = 0
    with open(f_out, 'wb', buffering= CHUNK_SIZE) as f_cipher :
        with open(f_in, 'rb', buffering= CHUNK_SIZE) as f_clear :
            chunk  = f_clear.read1()
            while chunk != b'':
                token = f.encrypt(chunk)
                f_cipher.write(token)               
                print(len(chunk))
                print(len(token))
                iter +=1
                chunk  = f_clear.read1()
    print(iter)
                

def decrypt_file(f_in: PurePath, f_out : PurePath, key : bytes):

    f = Fernet(key)
    print('decrypt')
    iter = 0
    with open(f_out, 'wb', buffering= TOKEN_SIZE) as f_clear:
        with open(f_in, 'rb', buffering= TOKEN_SIZE) as f_cipher:
            chunk  = f_cipher.read1()
            while chunk != b'':
                clear = f.decrypt(chunk)
                f_clear.write(clear)
                print(len(chunk))
                print(len(clear))
                iter +=1
                chunk  = f_cipher.read1()

    print(iter)

def test():
    key = Fernet.generate_key()
    f = Fernet(key)

    Path('tests/inputs')

    pass


if __name__ == '__main__':
    sys.exit(test())