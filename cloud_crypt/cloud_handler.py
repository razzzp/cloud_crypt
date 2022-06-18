
from argparse import ArgumentError
import datetime
from ftplib import error_perm
import io
from pathlib import Path, PurePath
from pydoc import cli
import sys
from typing import Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from cloud_crypt.context import Context

from cloud_crypt.secret_handler import CLOUD_GDRIVE, get_credential_filepath, get_token_filepath

SCOPES = ['https://www.googleapis.com/auth/drive.appdata']
MIME_GCLOUDFOLDER = 'application/vnd.google-apps.folder'
GCLOUD_ID = 'id'
GCLOUD_NAME = 'name'
GCLOUD_MIMETYPE = 'mimeType'
GCLOUD_PARENTS = 'parents'
GCLOUD_DATEFORMAT = '%Y%m%d%H%M%S'

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
        return



def download(gcloud_file_id, download_path : PurePath, context : Context):
    """
    downloads file with given file id from the drive
    project folder to the .crypt/pulled 
    """
    try:
        service = _build_cloudservice(context)
         # use name for now
        cloudfolder_name = context.project_id

        # checks if folder for project exists
        cloudfolder_id = _get_cloudfolderid(cloudfolder_name, service)
        query = "'{}' in parents".format(cloudfolder_id)

        # download to buffer
        request = service.files().get_media(fileId=gcloud_file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%.".format(int(status.progress() * 100)))

        # write to file
        with open(download_path, 'wb') as f:
            f.write(fh.getbuffer())
        




    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return 


def get_latest_crypt_file(context : Context):
    """
    gets the latest crypt file in the project folder of
    the drive
    """
    try:
        service = _build_cloudservice(context)
         # use name for now
        cloudfolder_name = context.project_id

        # checks if folder for project exists
        cloudfolder_id = _get_cloudfolderid(cloudfolder_name, service)
        # query to seacrh for files under certain folder
        query = "'{}' in parents".format(cloudfolder_id)
        project_files = _get_appdata_files(service, query)

        # earliest date possible
        cur_min_datetime = datetime.datetime.min
        latest_file = None
        for file in project_files:
            cur_create_date = get_create_date_for_filename(file[GCLOUD_NAME])
            if cur_create_date and (cur_create_date > cur_min_datetime):
                latest_file = file

        return latest_file

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return


def get_create_date_for_filename(file_name):
    file_name = file_name.split('.crypt')[0]
    try:
        create_date = datetime.datetime.strptime(file_name,GCLOUD_DATEFORMAT)
        return create_date
    except:
        return None


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
    try:
        file = service.files().create(
            body=file_metadata,
            fields='name, id'
        ).execute()
    except HttpError as error:
        raise error
    return file[GCLOUD_ID]

def get_cloudfolderid(folder_name : str, context : Context)-> str:
    """ wrapper for _get_cloudfolderid"""
    service = _build_cloudservice(context)
    return _get_cloudfolderid(folder_name, service)

def _get_cloudfolderid(folder_name : str, service) -> str:
    """ 
    Gets the google drive folder id of the given folder name 
        returns null if no folder found in the drive
    """
    existing_folders = _get_appdata_files(service, None)
    for file in existing_folders:
        if file[GCLOUD_NAME] == folder_name and file[GCLOUD_MIMETYPE] == MIME_GCLOUDFOLDER: return file[GCLOUD_ID]
    return None

def _get_appdata_files(service, query):
    results = []
    try:
        # query to search .crypt folder
        next_page_token = None
        while True:
            q_results = service.files().list(
                q = query,
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
        raise error


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
    context.project_id = 'test-project'
    service = _build_cloudservice(context)
    # list
    appdata_files = _get_appdata_files(service, None)
    print(appdata_files)
    # upload
    file_toupload = context.dir_ws.joinpath('temp.crypt')
    
    upload(file_toupload, context)
    # list 
    appdata_files = _get_appdata_files(service, None)
    print(appdata_files)

if __name__ == '__main__':    
    sys.exit(test())