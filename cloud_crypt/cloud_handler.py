
from argparse import ArgumentError
from pathlib import Path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from cloud_crypt.cli import generate_context
from cloud_crypt.context import Context

from cloud_crypt.secret_handler import get_credential_filepath, get_token_filepath

SCOPES = ['https://www.googleapis.com/auth/drive.appdata']
MIME_GCLOUDFOLDER = 'application/vnd.google-apps.folder'

def upload(file_path : Path, creds : Credentials, context : Context) -> bool:
    if file_path == None : raise ArgumentError('file path is null')
    if not file_path.exists() : raise FileNotFoundError('File does not exist' + file_path.absolute())

    try:
        service = build('drive', 'v3', credentials=creds)

        # upload crypt file
        file_metadata = {
            'name': 'temp.crypt',
            'parents': ['appDataFolder']
        }
        file_body = MediaFileUpload(file_path.absolute(),
                        mimetype='application/octet-stream',
                        resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=file_body,
            fields='name, id'
        ).execute()

        print('Folder ID: %s' % file.get('id'))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

def get_appdata_files(creds : Credentials, context : Context):
    results = []
    try:
        service = build('drive', 'v3', credentials=creds)
        # query to search .crypt folder
        next_page_token = None
        while True:
            q_results = service.files().list(
                q="name='temp.crypt'",
                spaces='appDataFolder',
                pageSize=10, 
                fields="nextPageToken, files(id, name)"
            ).execute()
            results.append(q_results.get('files', []))
            next_page_token  = q_results.get('nextPageToken')
            # if next page token None, no more items in space
            if not next_page_token : break
        return results

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return

    

def get_credentials(context : Context) -> Credentials:
    """ searches for existing token to create credentials if
        still valid.
        if not valid but can refresh, refresh the token
        if cannot refresh, build from credentials file """

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
     # paths to token and credential
    token_path = get_token_filepath(context)
    cred_path= get_credential_filepath(context)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def test():
    context = generate_context('tests/test_dir')
    creds = get_credentials(context)
    # list
    appdata_files = get_appdata_files(creds, context)
    print(appdata_files)
    # upload
    file_toupload = context.dir_ws.joinpath('temp.crypt')
    # upload(file_toupload, creds, context)
    # list 
    appdata_files = get_appdata_files(creds, context)
    print(appdata_files)

if __name__ == '__main__':    
    sys.exit(test())