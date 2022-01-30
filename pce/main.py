from lib2to3.pgen2 import token
from turtle import clear
from typing import final
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

AES_BLOCK_SIZE = 16
CHUNK_SIZE = 100 * 16

def encrypt_file(file_clear : str, file_cipher: str, key : str):

    f = Fernet(key)

    with open(file_cipher, 'wb', buffering= CHUNK_SIZE) as f_cipher:
        with open(file_clear, 'rb', buffering= CHUNK_SIZE) as f_clear :
            for chunk in f_clear:
                token = f.encrypt(chunk)
                f_cipher.write(token)
                pass
    pass

def decrypt_file(file_cipher: str, file_clear : str, key : str):
    f = Fernet(key)

    with open(file_clear, 'wb', buffering= CHUNK_SIZE) as f_cipher:
        with open(file_cipher, 'rb', buffering= CHUNK_SIZE) as f_clear :
            for chunk in f_clear:
                clear = f.decrypt(chunk)
                f_cipher.write(clear)
                pass
    pass

def main():
    key = Fernet.generate_key()
    f = Fernet(key)
    print(key)
    token = f.encrypt(b"A really secret message. Not for prying eyes.")
    print(token)
    clear = f.decrypt(token)
    print(clear)

    encrypt_file('tests/inputs/hello.txt', 'tests/outputs/hello_encrypted', key)
    decrypt_file('tests/outputs/hello_encrypted', 'tests/outputs/hello_decrypted.txt', key)

    encrypt_file('tests/inputs/3chunks.txt', 'tests/outputs/3chunks_encrypted', key)
    decrypt_file('tests/outputs/3chunks_encrypted', 'tests/outputs/3chunks_decrypted.txt', key)

    pass


if __name__ == '__main__':
    main()