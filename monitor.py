import sys
from datetime import datetime
from os.path import exists as is_file_exist
from time import sleep

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the necessary scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Constants
TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'
DEFAULT_PAGE_SIZE = 500
FOLDER_TYPE = 'application/vnd.google-apps.folder'
TEST_FILE_META_DATA = {
    'name': 'test',
    'mimeType': 'text/plain'
}
TIME_TO_WAIT = 5


class GoogleDriveMonitor:
    """
    Monitor Google Drive Handler
    """
    def __init__(self):
        self.last_checked = self.get_current_timestamp()  # init with the execution start time
        self.creds = self.get_credentials()
        self.service = build(
            serviceName='drive',
            version='v3',
            credentials=self.creds
        )

    @staticmethod
    def get_current_timestamp():
        """ Get current timestamp in the Google Drive timestamp format. UTC is required"""
        return datetime.utcnow().isoformat() + 'Z'

    @staticmethod
    def get_credentials() -> Credentials:
        """Get user credentials or create new ones if not available."""
        creds = None

        # There are available creds
        if is_file_exist(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(
                filename=TOKEN_PATH
            )
            print("[+] Credential retrieved from file")

        # No valid creds
        if not creds or not creds.valid:

            # There are a token, but it is needed to be refreshed
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not is_file_exist(CREDENTIALS_PATH):
                    print('[+] No credentials.json file in the current directory, Please add it and try again')
                    sys.exit()

                # First execution - asking the user access to his Drive
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file=CREDENTIALS_PATH,
                    scopes=SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Saves the new / refreshed creds in a file
            with open(TOKEN_PATH, 'w') as token:
                print(f"[+] Token saved to {TOKEN_PATH}")
                token.write(creds.to_json())

        return creds

    def list_files(self) -> list:
        """List all files in the user's Google Drive with paging"""
        time_of_check = self.get_current_timestamp()

        _filter = f"createdTime >= '{self.last_checked}' and createdTime < '{time_of_check}'"

        results = self.service.files().list(
            pageSize=DEFAULT_PAGE_SIZE,
            fields="nextPageToken, files(id, name, mimeType)",
            q=_filter
        ).execute()

        files = results['files']

        # Paging handling
        while results.get('nextPageToken'):
            results = self.service.files().list(
                pageSize=DEFAULT_PAGE_SIZE,
                fields="nextPageToken, files(id, name, mimeType)",
                q=_filter,
                pageToken=results['nextPageToken'],
            ).execute()

            files.extend(results['files'])

        # Update the last time new files were checked
        self.last_checked = time_of_check

        return files

    def check_and_update_permissions(self, file_obj: dict) -> None:
        """Check if the file is publicly accessible update permissions is it is"""

        # Folders permissions leak to the files in it, so we don't need to check them
        if file_obj.get('mimeType') == FOLDER_TYPE:
            return

        # Gets the file permissions list
        file_name = file_obj['name']
        file_id = file_obj['id']
        file_permissions = self.service.permissions().list(
            fileId=file_id
        ).execute()

        if not file_permissions:
            print(f'[+] Failed to retrieve permissions for file - {file_name}')
            return

        # Checks for 'anyone' permissions which means "publicly available", and removes them
        for perm in file_permissions.get('permissions'):
            if perm['type'] == 'anyone':
                print(f"[+] File '{file_name}' is publicly accessible.")

                # Change permissions to private by removing the public permissions
                self.service.permissions().delete(
                    fileId=file_id,
                    permissionId=perm['id']
                ).execute()

                print(f"[+] Permissions for file '{file_name}' changed to private.")
                return

        print(f"[+] File '{file_name}' is NOT publicly accessible.")

    def get_default_sharing_permissions(self) -> None:
        """Get default permissions for a new file by creating a new one, check its permissions and removing it"""

        # Creation
        file = self.service.files().create(
            body=TEST_FILE_META_DATA
        ).execute()

        # Permissions checking
        file_permissions = self.service.permissions().list(
            fileId=file['id']
        ).execute()

        # Removing
        self.service.files().delete(
            fileId=file['id']
        ).execute()

        # Checks if 'anyone' appears as one of the permissions types
        if 'anyone' in [_file['type'] for _file in file_permissions.get('permissions')]:
            print(f"[+] Default permissions for files is publicly accessible.")
        else:
            print(f"[+] Default permissions for files is NOT publicly accessible.")

    def monitor_drive(self):
        """Main - Monitor the user's Google Drive for new files."""
        print("[+] Monitoring Google Drive for new files. Press Ctrl+C to stop.")
        print(f'[+] Starting time - {self.last_checked}')
        try:
            # user_data = self.service.about().get(fields="*").execute()
            self.get_default_sharing_permissions()

            while True:
                new_files = self.list_files()

                for new_file in new_files:
                    self.check_and_update_permissions(new_file)

                sleep(TIME_TO_WAIT)

        except KeyboardInterrupt:
            print("[+] Monitoring stopped.")
        except Exception as e:
            print(f"[+] Monitoring stopped due to an error - {e}")
        finally:
            self.service.close()


if __name__ == '__main__':
    GoogleDriveMonitor().monitor_drive()
