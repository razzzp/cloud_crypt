
from datetime import datetime
import os
from pathlib import Path, PurePath
import sys
from tarfile import TarInfo
from typing import List
import cloud_crypt

from cloud_crypt.archiver import archive, extract_filesunderfolder
from cloud_crypt.cloud_handler import _get_appdata_files, download, upload, _get_appdata_files_forproject
from cloud_crypt.compress import compress_file, decompress_file
from cloud_crypt.context import DIR_CRYPT, DIR_PREP, FILE_IGNORE, FILE_TEMP, Context
from cloud_crypt.crypto import decrypt_file, encrypt_file

_ignored_items = None

def init(context : Context):
    # TODO make .crypt dir hidden
    # under .cryptdir
    #  create ws(workspace) dir
    #  create pulled dir
    if context.is_folder_initialized : raise FileExistsError('this directory is already initialized')
    try:
        # initialize folder
        context.initialize_project()
    except:
        # TODO
        pass


def _init_ignored_items(context : Context) -> List:
    # gets list of items to ignore from
    # .cryptignore
    # TODO put in context?
    global _ignored_items
    if _ignored_items == None:
        _ignored_items = [DIR_CRYPT]
        ignore_file = Path(context.dir_client_root).joinpath(FILE_IGNORE)
        if not ignore_file.exists() : return None
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

def prep(context : Context) -> Path:

    if not context.is_folder_initialized : raise FileNotFoundError("please initialize the directory first")
    # create any missing folders
    context.initialize_folders()
    # file paths for prep files
    crypt_filename = _generate_cryptfilename()
    dir_ws = context.dir_ws
    dir_prep = context.dir_prep
    file_tar = dir_ws.joinpath(crypt_filename).with_suffix('.tar')
    file_xz = dir_ws.joinpath(crypt_filename).with_suffix('.tar.xz')
    file_crypt = dir_prep.joinpath(crypt_filename).with_suffix('.crypt')


    # archive to .tar, 
    # then compress to .tar.xz
    # then encrypt to .crypt which will be uploaded to cloud 
    _init_ignored_items(context)
    archive(context.dir_client_root, file_tar, _archive_filter)
    compress_file(file_tar, file_xz)
    encrypt_file(file_xz, file_crypt, context.key)
    return file_crypt

def _generate_cryptfilename() -> str:
    """ Just name it as current date time for now"""
    return str(datetime.now().strftime('%Y%m%d%H%M%S'))

def push(context : Context):
    if not context.is_folder_initialized : raise FileNotFoundError("please initialize the directory first")

    # get newest created crypt file
    latest = 0
    latest_file = None
    for file in context.dir_prep.iterdir():
        if '.crypt' in file.name:
            ctime = file.stat().st_ctime_ns
            if  ctime > latest:
                latest = ctime
                latest_file = file

    if latest_file == None : latest_file = prep(context)
    upload(latest_file, context)

    pass

def pull(context : Context):
    if not context.is_folder_initialized : raise FileNotFoundError("please initialize the directory first")

    download(context)

def _decrypt_decompress_extract(name : str, context : Context):
    # test
    file_crypt = context.dir_ws.joinpath(name).with_suffix('.crypt')
    file_xz = context.dir_pulled.joinpath(name).with_suffix('.tar.xz')
    file_tar = context.dir_pulled.joinpath(name).with_suffix('.tar')
    dir_out = context.dir_pulled.joinpath('out')
    if not dir_out.exists() : dir_out.mkdir()

    decrypt_file(file_crypt, file_xz, context.key)
    decompress_file(file_xz, file_tar)
    extract_filesunderfolder(file_tar, dir_out, 'data')
    pass

def generate_context(folder : os.PathLike) -> Context:
    return Context(folder)

def test() -> int:
    context = generate_context('tests/test_dir')
    context.project_id = 'test-project'
    if not context.is_folder_initialized:
        init(context)
    context.initialize_folders()
    # ---
    prep(context)
    push(context)
    pull(context)
    
    
if __name__ == '__main__':
    sys.exit(test())