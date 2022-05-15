
from cmath import exp
from lib2to3.pgen2.parse import ParseError
from os import PathLike
import os
from pathlib import Path
from cryptography.fernet import Fernet
from configparser import ConfigParser
import inspect

DIR_CRYPT = '.crypt'
DIR_WS = 'ws'
DIR_PULLED = 'pulled'
DIR_SECRET= 'secret'
DIR_TOKENS = 'tokens'
DIR_PREP = 'prep'
FILE_TEMP = 'temp'
FILE_IGNORE = '.cryptignore'
FILE_CFG = 'crypt.cfg'

CFG_SECTION_GENERAL= 'GENERAL'
CFG_PROJECT_ID = 'ProjectId'
CFG_SECTION_ENCRYPTION = 'ENCRYPTION'
CFG_KEY_PATH = 'KeyPath'
CFG_SECTION_GDRIVE = 'google.drive'

class Context:
    is_folder_initialized : bool = False
    dir_app_root : Path
    dir_crypt : Path
    dir_ws : Path
    dir_secret : Path
    dir_pulled : Path
    dir_prep : Path
    file_cfg : Path
    dir_tokens : Path
    cfg : ConfigParser
    project_id : str

    def __init__(self, client_folder : PathLike) -> None:
        """ Context will hold all paths needed based on the given path.
        When intialized it will NOT generete any folders/files, but
        will just get data."""

        self.dir_client_root = Path(client_folder)
        if not self.dir_client_root.exists() : raise FileNotFoundError('failed to genereate context. directory not found: ' + self.dir_client_root.absolute)

        # set path to folders
        self.dir_app_root = Path(inspect.stack()[0][1]).parent.parent 
        self.dir_crypt = self.dir_client_root.joinpath(DIR_CRYPT)
        self.dir_ws = self.dir_crypt.joinpath(DIR_WS)
        self.dir_secret = self.dir_crypt.joinpath(DIR_SECRET)
        self.dir_pulled = self.dir_crypt.joinpath(DIR_PULLED)
        self.file_cfg = self.dir_crypt.joinpath(FILE_CFG)
        self.dir_tokens = self.dir_crypt.joinpath(DIR_TOKENS)
        self.dir_prep = self.dir_crypt.joinpath(DIR_PREP)
        
        # checks folders and cfg file
        try:
            self.is_folder_initialized = self._check_projectinitialised()
        except:
            #case folder/files exists but not correct
            pass

        if not self.is_folder_initialized : return
        self.cfg  = self._get_cfg()
        #self.project_id = self.cfg[CFG_SECTION_GENERAL][CFG_PROJECT_ID]

        # TODO where to put key?
        self.key =  Fernet.generate_key()
        pass

    def _check_projectinitialised(self) -> bool:
        """ Checks if required folder is present. 
            If it is folder is considered initialized"""

        result = False
        # if .crypt folder exists and
        result = self.dir_crypt.exists()
        # check config file
        result = result and self._check_cfgfile()
        # folder is initialized
        return result

    def _check_cfgfile(self) -> bool:
        """ Checks cfg file, if there is something wrong return false"""
        
        if not self.file_cfg.exists() : raise FileNotFoundError('Cannot find the config file')
        cfg = self._get_cfg()
        if not cfg[CFG_SECTION_GENERAL][CFG_PROJECT_ID] : raise ParseError('Config file does not have the {0} value'.format(CFG_PROJECT_ID))
        return True

    def _get_cfg(self) -> ConfigParser:
        """ Return config parser that reads the cfg file"""
        cfg_parser = ConfigParser()
        cfg_parser.read(self.file_cfg)
        return cfg_parser

    def initialize_project(self):
        """ Initializes everthing needed for the project"""
        self.initialize_folders()
        self.initialize_cfg()
        self.is_folder_initialized = True

    def initialize_folders(self):
        """ Initializes the folder for use"""
        # creates folders needed
        # .crypt folder
        if not self.dir_crypt.exists() : self.dir_crypt.mkdir()
        # check other folders and generate if missing
        if not self.dir_ws.exists() : self.dir_ws.mkdir()
        if not self.dir_pulled.exists() : self.dir_pulled.mkdir()
        if not self.dir_secret.exists() : self.dir_secret.mkdir()
        if not self.dir_tokens.exists() : self.dir_tokens.mkdir()
        if not self.dir_prep.exists() : self.dir_prep.mkdir()

    def initialize_cfg(self):
        """ Initializes cfg file"""
        self.cfg = self._generate_cfg(self.project_id)
        with open(self.file_cfg.absolute(),'w') as cfgfile:
            self.cfg.write(cfgfile)

    def _generate_cfg(self, project_id : str) -> ConfigParser:
        """ Generates crypt.cfg file and returns the parser used to 
            create it"""
        cfg_parser = ConfigParser()
        cfg_parser[CFG_SECTION_GENERAL] = {
            # set id to directory name?
            CFG_PROJECT_ID : project_id
        }
        cfg_parser[CFG_SECTION_ENCRYPTION] = {
            CFG_KEY_PATH : self.dir_secret.joinpath('privatekey').absolute()
        }
        cfg_parser[CFG_SECTION_GDRIVE] = {

        }
        # TODO
        return cfg_parser
        