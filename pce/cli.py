
import os
from pathlib import Path, PurePath
import sys
from tarfile import TarInfo
from types import SimpleNamespace

from cryptography.fernet import Fernet

from pce.archiver import archive
from pce.compress import compress_file
from pce.crypto import encrypt_file


DIR_CRYPT = '.crypt'
DIR_WS = 'ws'
FILE_TEMP = 'temp'

def init(context):
    # paths
    dir_ws = Path(context.cwd).joinpath(DIR_CRYPT, DIR_WS)
    if dir_ws.exists(): raise FileExistsError('this directory is already initialized')
    dir_ws.mkdir(parents=True)
    pass

def _archive_filter(info : TarInfo):
    excluded_items = [DIR_CRYPT]
    if not info.name in excluded_items:
        return info
    pass

def prep(context):
    # paths
    cwd = PurePath(context.cwd)
    dir_crypt =  cwd / DIR_CRYPT

    if not Path(dir_crypt).exists() : raise FileNotFoundError("please initialize the directory first")

    dir_ws = dir_crypt.joinpath(DIR_WS)
    file_tar = dir_ws.joinpath(FILE_TEMP).with_suffix('.tar')
    file_xz = dir_ws.joinpath(FILE_TEMP).with_suffix('.tar.xz')
    file_crypt = dir_ws.joinpath(FILE_TEMP).with_suffix('.crypt')

    archive(cwd, file_tar, _archive_filter)
    compress_file(file_tar, file_xz)
    encrypt_file(file_xz, file_crypt, context.key)

    pass

def push(context):
    pass

def test() -> int:
    os.chdir('tests/outputs/test_dir')
    context = SimpleNamespace()
    context.cwd = os.getcwd()
    context.key = Fernet.generate_key()

    #init(context)
    prep(context)
    


if __name__ == '__main__':
    sys.exit(test())