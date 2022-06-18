
from datetime import datetime
import os
from pathlib import Path, PurePath
import re
import sys
from tarfile import TarInfo
from typing import Callable, List
from cloud_crypt import archiver, cloud_handler, compressor, crypto
from cloud_crypt.context import *

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


def _get_ignored_items(context : Context) -> List:
    # gets list of items to ignore from
    # .cryptignore

    # alwyas ignore crypt folder
    ignored_items = [DIR_CRYPT]
    ignore_file = Path(context.dir_client_root).joinpath(FILE_IGNORE)
    # no ignore file
    if not ignore_file.exists() : return ignored_items

    with open(ignore_file, 'r') as f:
        for line in f:
            ignored_items.append(line.strip())

    return ignored_items


def _build_ignore_file_filter() -> Callable[[TarInfo],TarInfo]:
    """
    Builds function to 
    """
    ignored_items = _get_ignored_items()
    def ignore_filter(info: TarInfo):
        path = PurePath(info.path)
        if not path.name in ignored_items:
            return info
    return ignore_filter


def _archive_project_folder(context : Context, output_path : Path):

    ignore_filter = _build_ignore_file_filter()
    archiver.archive(context.dir_client_root, output_path, ignore_filter)


def _generate_cryptfilename() -> str:
    """ 
    Just name it as current date time for now
    """
    return str(datetime.utcnow().strftime(cloud_handler.GCLOUD_DATEFORMAT))


def prep(context : Context) -> Path:
    """
    Prepares the encrypted, compressed archive of the client folder
    """
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
    _archive_project_folder(context, file_tar)
    compressor.compress_file(file_tar, file_xz)
    crypto.encrypt_file(file_xz, file_crypt, context.key)
    return file_crypt


def push(context : Context):
    """
    Pushes the latest .crypt file in the prep folder,
    if none present prep the folder to create one first
    then upload to cloud
    """
    if not context.is_folder_initialized : raise FileNotFoundError("please initialize the directory first")
    # create any missing folders
    context.initialize_folders()

    latest_local_crypt_file = _get_latest_local_crypt_file(context)

    if latest_local_crypt_file == None : latest_local_crypt_file = prep(context)
    cloud_handler.upload(latest_local_crypt_file, context)

    pass

def pull(context : Context):
    """
    Downloads the latest crypt file from cloud,
    puts it in the pulled folder, then replaces
    the user's directory with its contents
    """
    if not context.is_folder_initialized : raise FileNotFoundError("please initialize the directory first")
    # create any missing folders
    context.initialize_folders()

    latest_cloud_crypt_file = cloud_handler.get_latest_crypt_file(context)
    if latest_cloud_crypt_file == None:
        print('This folder has not been uploaded to the cloud yet.')
        return
    cloud_file_cdate = cloud_handler.get_create_date_for_filename(latest_cloud_crypt_file[cloud_handler.GCLOUD_NAME])

    latest_local_crypt_file = _get_latest_local_crypt_file(context)
    if latest_local_crypt_file:
        local_file_cdate = cloud_handler.get_create_date_for_filename(latest_local_crypt_file.name)
    else:
        local_file_cdate = None

    # if file in cloud older than local files, ask user if want to continue
    can_continue = True
    if (local_file_cdate) and local_file_cdate > cloud_file_cdate:
        user_input = input('File found in the cloud is older than your local files.\n \
            Do you want to continue? (Y/N)')
        user_input = user_input.upper()
        if user_input == 'N' or user_input == 'NO':
            can_continue = True

    if not can_continue:
        return
    download_path = context.dir_pulled.joinpath(latest_cloud_crypt_file[cloud_handler.GCLOUD_NAME])
    cloud_handler.download(latest_cloud_crypt_file[cloud_handler.GCLOUD_ID], download_path, context)


def _get_latest_local_crypt_file(context : Context) -> Path:
    # get newest available crypt file
    latest = 0
    latest_file = None

    reg_crypt = re.compile(r"\.crypt$")
    for file in context.dir_prep.iterdir():
        # using match doesn't work ?
        if reg_crypt.search(file.name):
            ctime = file.stat().st_ctime_ns
            if  ctime > latest:
                latest = ctime
                latest_file = file
    return latest_file


def _decrypt_decompress_extract(name : str, context : Context):
    # for test
    file_crypt = context.dir_ws.joinpath(name).with_suffix('.crypt')
    file_xz = context.dir_pulled.joinpath(name).with_suffix('.tar.xz')
    file_tar = context.dir_pulled.joinpath(name).with_suffix('.tar')
    dir_out = context.dir_pulled.joinpath('out')
    if not dir_out.exists() : dir_out.mkdir()

    crypto.decrypt_file(file_crypt, file_xz, context.key)
    compressor.decompress_file(file_xz, file_tar)
    archiver.extract_filesunderfolder(file_tar, dir_out, 'data')
    pass


def generate_context(folder : os.PathLike) -> Context:
    return Context(folder)


def test() -> int:
    context = generate_context('tests/test_dir')
    context.project_id = 'test-project'
    if not context.is_folder_initialized:
        init(context)

    # ---
    # prep(context)
    # push(context)
    pull(context)
    
    
if __name__ == '__main__':
    sys.exit(test())