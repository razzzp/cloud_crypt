from cloud_crypt.context import Context
from pathlib import Path, PurePath

DIR_CREDENTIALS = 'credentials'
DIR_TOKENS = 'tokens'

def get_credential_filepath(context : Context) -> Path:
    return context.dir_app_root.joinpath(DIR_CREDENTIALS).joinpath('client_creds_desktop.json')

def get_token_filepath(context : Context) -> Path:
    return context.dir_app_root.joinpath(DIR_TOKENS).joinpath('token.json')
