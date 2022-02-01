
from pathlib import PurePath
import sys
from tarfile import TarInfo
import tarfile

def _archive_filter(info : TarInfo):
    return info

def archive(path_in : PurePath, f_out : PurePath, filter):
    
    archive = tarfile.open(f_out,'w')
    archive.add(path_in, path_in.name, filter=filter)
    pass

def test():
    f_out_arch = PurePath('tests/outputs/inputs.tar')
    p_in = PurePath('tests/inputs/')

    archive(f_out_arch, p_in, _archive_filter)


    pass

if __name__ == '__main__':
    sys.exit(test())