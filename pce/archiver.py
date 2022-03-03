
from importlib.resources import contents
from pathlib import Path, PurePath
import sys
from tarfile import TarInfo
import tarfile

def _archive_filter(info : TarInfo):
    return info

def archive(path_in : PurePath, f_out : PurePath, filter):
    
    archive = tarfile.open(f_out,'w')
    # archive.add(path_in, 'data', filter=filter)
    dir = Path(path_in)
    data_path = PurePath('data')
    for file in dir.iterdir():
        archive.add(file, data_path.joinpath(file.name), filter=filter)
    archive.close()
    pass

def extract(f_in : PurePath, path_out : PurePath) :

    archive = tarfile.open(f_in, 'r')
    # for file in archive.getmembers():
    #     archive.extract(file)
    archive.extractall(path_out)
    archive.close()
    pass

def test():
    f_out_arch = PurePath('tests/outputs/inputs.tar')
    p_in = PurePath('tests/inputs/')

    archive(p_in, f_out_arch, _archive_filter)


    pass

if __name__ == '__main__':
    sys.exit(test())