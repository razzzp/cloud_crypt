
import os
from pathlib import Path, PurePath
import sys
from tarfile import TarInfo
from typing import List

from pce.archiver import archive, extract
from pce.compress import compress_file, decompress_file
from pce.context import DIR_CRYPT, FILE_IGNORE, FILE_TEMP, Context
from pce.crypto import decrypt_file, encrypt_file

_ignored_items = None

def init(context : Context):
    # TODO make .crypt dir hidden
    # under .cryptdir
    #  create ws(workspace) dir
    #  create pulled dir
    if context.is_folder_initialized : raise FileExistsError('this directory is already initialized')
    # will also create .crypt dir
    context.dir_ws.mkdir(parents=True)
    context.dir_pulled.mkdir()
    pass

def _init_ignored_items(context : Context) -> List:
    # gets list of items to ignore from
    # .cryptignore
    # TODO put in context?
    global _ignored_items
    if _ignored_items == None:
        _ignored_items = [DIR_CRYPT]
        ignore_file = PurePath(context.cwd).joinpath(FILE_IGNORE)
        with open(ignore_file, 'r') as f:
            for line in f:
                _ignored_items.append(line.strip())
    return _ignored_items


def _archive_filter(info : TarInfo):
    # gets list of items to ignore from
    # .cryptignore

    # for now just check the name(last item in path)
    path = PurePath(info.path)
    if not path.name in _ignored_items:
        return info
    pass

def prep(context : Context):

    if not context.is_folder_initialized : raise FileNotFoundError("please initialize the directory first")

    # file paths for prep files
    dir_ws = context.dir_ws
    file_tar = dir_ws.joinpath(FILE_TEMP).with_suffix('.tar')
    file_xz = dir_ws.joinpath(FILE_TEMP).with_suffix('.tar.xz')
    file_crypt = dir_ws.joinpath(FILE_TEMP).with_suffix('.crypt')


    # archive to .tar, 
    # then compress to .tar.xz
    # then encrypt to .crypt which will be uploaded to cloud 
    _init_ignored_items(context)
    archive(context.cwd, file_tar, _archive_filter)
    compress_file(file_tar, file_xz)
    encrypt_file(file_xz, file_crypt, context.key)

    pass

def push(context : Context):
    pass

def pull(context : Context):
    pass

def _decrypt_decompress_extract(context : Context):
    # test
    file_crypt = context.dir_ws.joinpath(FILE_TEMP).with_suffix('.crypt')
    file_xz = context.dir_pulled.joinpath(FILE_TEMP).with_suffix('.tar.xz')
    file_tar = context.dir_pulled.joinpath(FILE_TEMP).with_suffix('.tar')

    decrypt_file(file_crypt, file_xz, context.key)
    decompress_file(file_xz, file_tar)
    extract(file_tar, context.dir_pulled)
    pass

def generate_context(folder : os.PathLike) -> Context:
    return Context(folder)


def test() -> int:
    os.chdir('tests/test_dir')
    context = generate_context(os.getcwd())

    if not context.is_folder_initialized:
        init(context)
    prep(context)
    _decrypt_decompress_extract(context)
    


if __name__ == '__main__':
    sys.exit(test())