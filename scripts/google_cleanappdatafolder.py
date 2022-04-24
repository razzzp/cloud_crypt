import os
from pathlib import Path
import sys
cwd = Path(os.getcwd())
sys.path.append(str(cwd.absolute()))
# print(sys.path)
from cloud_crypt import cloud_handler
from cloud_crypt import cli

def clean():
    test_folder = cwd.joinpath('tests').joinpath('test_dir')
    context = cli.generate_context(test_folder)
    service = cloud_handler._build_cloudservice(context)
    listoffiles = cloud_handler._get_appdata_files(service)
    for file in listoffiles:
        #
        print(file)
        if file[cloud_handler.GCLOUD_MIMETYPE] == cloud_handler.MIME_GCLOUDFOLDER:
            service.files().delete(
                fileId = file[cloud_handler.GCLOUD_ID]
            ).execute()
    listoffiles = cloud_handler._get_appdata_files(service)
    print(listoffiles)


if __name__ == '__main__':
    sys.exit(clean())