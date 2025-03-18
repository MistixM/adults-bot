import configparser

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.constants.global_settings import FOLDER_ID

config = configparser.ConfigParser()
config.read('app/constants/config.ini')

def get_or_create_folder(service, parent_folder_id, folder_name):
    # Gets parent folder ID (that set in the global_settings.py)
    # Creates a folder name with
    query = f"mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and name='{folder_name}' and trashed=false"
    response = service.files().list(q=query, fields="files(id)").execute()
    
    # Если папка найдена, возвращаем её ID
    if response.get("files"):
        return response["files"][0]["id"]
    
    # Create a metadata for folder
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }

    # Create a folder
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


async def upload_to_drive(path: str, group_name: str, filename: str):
    # Init credentials for the Google Drive 
    creds = service_account.Credentials.from_service_account_file(
        config['Main']['SERVICE_ACCOUNT_FILE'], 
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    # Google Drive API init
    drive_service = build("drive", "v3", credentials=creds)
    
    # Check if required folder exists. If no, create one
    folder_id = get_or_create_folder(drive_service, FOLDER_ID, group_name)
    
    # Metadata for the file
    metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    
    # File loading
    media = MediaFileUpload(path, mimetype="image/jpeg")
    drive_service.files().create(body=metadata, media_body=media, fields="id").execute()