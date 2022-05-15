
from argparse import ArgumentError
from pathlib import Path
from pydoc import cli
import sys
from typing import Any
import uuid
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from cloud_crypt.context import Context

from cloud_crypt.secret_handler import CLOUD_GDRIVE, get_credential_filepath, get_token_filepath

SCOPES = ['https://www.googleapis.com/auth/drive.appdata']
MIME_GCLOUDFOLDER = 'application/vnd.google-apps.folder'
GCLOUD_ID = 'id'
GCLOUD_NAME = 'name'
GCLOUD_MIMETYPE = 'mimeType'
GCLOUD_PARENTS = 'parents'

def upload(file_path : Path,  context : Context) -> Any:
    if file_path == None : raise ArgumentError('file path is null')
    if not file_path.exists() : raise FileNotFoundError('File does not exist' + file_path.absolute())

    try:
        service = _build_cloudservice(context)
        # use name for now
        cloudfolder_name = context.project_id

        # checks if folder for project exists, if not create one
        cloudfolder_id = _get_cloudfolderid(cloudfolder_name, service)
        if not cloudfolder_id:
            cloudfolder_id = _create_cloudfolder(cloudfolder_name, service)
            
        # upload crypt file
        file_metadata = {
            GCLOUD_NAME: file_path.name,
            GCLOUD_PARENTS: [cloudfolder_id]
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
        return file
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

def download(context : Context):
    try:
        service = _build_cloudservice(context)
        cloud_projectfiles = _get_appdata_files_forproject(context.project_id, service)
        print(cloud_projectfiles)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')



def _get_appdata_files_forproject(project_id : str, service) :
    cloudfolder_id = _get_cloudfolderid(project_id, service)
    results = []
    try:
        #if service == None : service = _build_cloudservice(context)
        # query to search .crypt folder
        next_page_token = None
        while True:
            q_results = service.files().list(
                q = "'{}' in parents".format(cloudfolder_id),
                spaces='appDataFolder',
                pageSize=10, 
                fields="nextPageToken, files(id, name, mimeType, parents)",
            ).execute()
            
            results.extend(q_results.get('files', []))
            next_page_token  = q_results.get('nextPageToken')
            # if next page token None, no more items in space
            if not next_page_token : break
        return results
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return


def _create_cloudfolder(name : str, service) -> str:
    """ Creates folder in cloud with the following id and name
        id currently not used"""
    file_metadata = {
        # TODO how does id work? there is a specific format
        #GCLOUD_ID: id,
        GCLOUD_NAME: name,
        GCLOUD_MIMETYPE : MIME_GCLOUDFOLDER,
        GCLOUD_PARENTS: ['appDataFolder']
    }
    file = service.files().create(
        body=file_metadata,
        fields='name, id'
    ).execute()
    return file[GCLOUD_ID]

def get_cloudfolderid(folder_name : str, context : Context)-> str:
    """ wrapper for _get_cloudfolderid"""
    service = _build_cloudservice(context)
    return _get_cloudfolderid(folder_name, service)

def _get_cloudfolderid(folder_name : str, service) -> str:
    """ Gets the id of the given folder name
        returns null if no folder found"""
    #if service == None: service = _build_cloudservice(context)
    existing_folders = _get_appdata_files(service)
    for file in existing_folders:
        if file[GCLOUD_NAME] == folder_name and file[GCLOUD_MIMETYPE] == MIME_GCLOUDFOLDER: return file[GCLOUD_ID]
    return None

def _get_appdata_files(service):
    results = []
    try:
        #if service == None : service = _build_cloudservice(context)
        # query to search .crypt folder
        next_page_token = None
        while True:
            q_results = service.files().list(
                spaces='appDataFolder',
                pageSize=10, 
                fields="nextPageToken, files(id, name, mimeType, parents)"
            ).execute()
            
            results.extend(q_results.get('files', []))
            next_page_token  = q_results.get('nextPageToken')
            # if next page token None, no more items in space
            if not next_page_token : break
        return results

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return

def _get_cloudfoldername(projectid : str)-> str:
    """ TODO should we set id too?"""
    return str(uuid.uuid3(uuid.NAMESPACE_OID, projectid))

def _build_cloudservice(context : Context):
    creds = get_credentials(context)
    return build('drive', 'v3', credentials=creds)

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
    token_path = get_token_filepath(CLOUD_GDRIVE, context)
    cred_path= get_credential_filepath(context)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    try:
        if not creds or not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
    except BaseException as e:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    return creds

def test():
    from cloud_crypt.cli import generate_context
    context = generate_context('tests/test_dir')
    context.project_id = 'test1'
    service = _build_cloudservice(context)
    # list
    appdata_files = _get_appdata_files(service)
    print(appdata_files)
    # upload
    file_toupload = context.dir_ws.joinpath('temp.crypt')
    
    upload(file_toupload, context)
    # list 
    appdata_files = _get_appdata_files(service)
    print(appdata_files)

if __name__ == '__main__':    
    sys.exit(test())