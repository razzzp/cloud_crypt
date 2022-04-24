from cloud_crypt.context import Context
from pathlib import Path, PurePath

DIR_CREDENTIALS = 'credentials'
DIR_TOKENS = 'tokens'
CLOUD_GDRIVE = 'googledrive'

def get_credential_filepath(context : Context) -> Path:
    return context.dir_app_root.joinpath(DIR_CREDENTIALS).joinpath('client_creds_desktop.json')

def get_token_filepath(cloudname: str, context : Context) -> Path:
    if cloudname == 'googledrive':
        return context.dir_tokens.joinpath('token_googledrive.json')
    return None
