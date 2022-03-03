
from os import PathLike
from pathlib import Path
from cryptography.fernet import Fernet

DIR_CRYPT = '.crypt'
DIR_WS = 'ws'
DIR_PULLED = 'pulled'
FILE_TEMP = 'temp'
FILE_IGNORE = '.cryptignore'

class Context:

    def __init__(self, folder : PathLike) -> None:

        self.cwd = Path(folder)
        self.dir_crypt = self.cwd / DIR_CRYPT
        self.dir_ws = self.dir_crypt / DIR_WS
        self.dir_pulled = self.dir_crypt / DIR_PULLED
        self.is_folder_initialized = False
        self.key =  Fernet.generate_key()

        if not self.cwd.exists: raise FileNotFoundError('failed to genereate context. directory not found' + self.cwd.absolute)

        self._check_cryptdirs_exist()
        pass

    def _check_cryptdirs_exist(self):
        # if .crypt doesn't exist, return
        if not self.dir_crypt.exists : return

        self.is_folder_initialized = True
        # check folders and generate if missing
        if not self.dir_ws.exists() : self.dir_ws.mkdir()
        if not self.dir_pulled.exists() : self.dir_pulled.mkdir()


