from lzma import FORMAT_XZ, LZMAFile
from pathlib import PurePath
import sys

def compress_file(f_in : PurePath, f_out: PurePath):
    # TODO refactor later to get f_comp
    f_comp = LZMAFile(f_out, 'wb',format=FORMAT_XZ)
    with open(f_in, 'rb') as f_ucomp:
        # read one buffer worth of data
        curBytes = f_ucomp.read1()
        while curBytes != b'':
            f_comp.write(curBytes)
            curBytes = f_ucomp.read1()
    f_comp.close()

def decompress_file(f_in : PurePath, f_out: PurePath):
    # TODO refactor later to get f_comp
    f_comp = LZMAFile(f_in, 'rb',format=FORMAT_XZ)
    with open(f_out, 'wb') as f_ucomp:
        # read one buffer worth of data
        curBytes = f_comp.read1()
        while curBytes != b'':
            f_ucomp.write(curBytes)
            curBytes = f_comp.read1()
    f_comp.close()

def test() -> None:
    f_in = PurePath('tests/inputs/3chunks.txt')
    f_out_comp = PurePath('tests/outputs/3chunks.xz')
    f_out_decomp = PurePath('tests/outputs/3chunks_decomp.txt')
    compress_file(f_in, f_out_comp)
    decompress_file(f_out_comp, f_out_decomp)
    pass

if __name__ == '__main__':
    sys.exit(test())