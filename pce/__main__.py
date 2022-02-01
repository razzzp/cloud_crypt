
# generate context

import os
from pathlib import PurePath
import argparse

from tests.gen_testinputfiles import main

main_parser = argparse.ArgumentParser(description='Encrypts files before pushing to cloud..', add_help=False)
main_parser.add_argument('init')

prep_parser = argparse.ArgumentParser(parents=[main_parser])
prep_parser.add_argument('--')