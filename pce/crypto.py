
from pathlib import Path, PurePath
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


AES_BLOCK_SIZE = 16
CHUNK_SIZE = 100 * 16



def encrypt_file(f_in : PurePath, f_out: PurePath, key : str):

    f = Fernet(key)

    with open(f_out, 'wb', buffering= CHUNK_SIZE) as f_cipher:
        with open(f_in, 'rb', buffering= CHUNK_SIZE) as f_clear :
            for chunk in f_clear:
                token = f.encrypt(chunk)
                f_cipher.write(token)
                pass
    pass

def decrypt_file(f_in: PurePath, f_out : PurePath, key : str):
    f = Fernet(key)

    with open(f_out, 'wb', buffering= CHUNK_SIZE) as f_cipher:
        with open(f_in, 'rb', buffering= CHUNK_SIZE) as f_clear :
            for chunk in f_clear:
                clear = f.decrypt(chunk)
                f_cipher.write(clear)
                pass
    pass

def test():
    key = Fernet.generate_key()
    f = Fernet(key)

    Path('tests/inputs')

    pass


if __name__ == '__main__':
    sys.exit(test())