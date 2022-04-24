
# generate context

import os
from pathlib import PurePath
import argparse
from cloud_crypt.cli import push

from tests.gen_testinputfiles import main

main_parser = argparse.ArgumentParser(description='Encrypts files before pushing to cloud..', add_help=False)
subparsers = main_parser.add_subparsers(help='Commands help')

#init parser
init_parser = subparsers.add_parser('init')
init_parser.add_argument('--project-name', required=True)
init_parser.add_argument('--set-cloud', required=True)
# init_parser.add_argument('')

prep_parser = subparsers.add_parser('prep')
# prep_parser.add_argument('')

push_parser = subparsers.add_parser('push')

