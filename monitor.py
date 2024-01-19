import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the necessary scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Constants
TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'


class GoogleDriveMonitor:
    def __init__(self):
        self.creds = self.get_credentials()
        self.service = build(
            serviceName='drive',
            version='v3',
            credentials=self.creds
        )

        self.last_files = self.list_files()

    @staticmethod
    def get_credentials():
        """Get user credentials or create new ones if not available."""
        creds = None

        # There are available creds
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH)

        # No valid creds
        if not creds or not creds.valid:

            # There are a token, but it is needed to be refreshed
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Saves the new / refreshed creds in a file
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        return creds

    def list_files(self):
        """List all files in the user's Google Drive."""
        results = self.service.files().list().execute()
        files = results.get('files', [])
        return files

    def check_and_update_permissions(self, file_id):
        """Check if the file is in a publicly accessible folder and update permissions."""
        file = self.service.files().get(fileId=file_id).execute()

        sharing_status = file.get('sharingStatus', 'unknown')

        if sharing_status == 'publiclyAccessible':
            print(f"File '{file['name']}' is publicly accessible.")

            # Change permissions to private
            self.service.permissions().create(
                fileId=file_id,
                body={'role': 'owner', 'type': 'user', 'emailAddress': 'user@example.com'}
            ).execute()

            print(f"Permissions for file '{file['name']}' changed to private.")
            return True
        else:
            print(f"File '{file['name']}' is not publicly accessible.")
            return False

    def monitor_drive():
        """Monitor the user's Google Drive for new files."""
        self.service = build('drive', 'v3', credentials=self.creds)

        print("Monitoring Google Drive for new files. Press Ctrl+C to stop.")
        try:
            while True:
                files_before = list_files(self.service)

                # Wait for a change in the user's Drive
                input("Press Enter to check for new files...")

                files_after = list_files(self.service)

                new_files = [file for file in files_after if file not in files_before]

                for new_file in new_files:
                    file_id = new_file['id']
                    changed = check_and_update_permissions(self.service, file_id)

                    print(f"Sharing Status for file '{new_file['name']}': {new_file.get('sharingStatus', 'unknown')}")
                    print(f"Changed by the program: {changed}\n")

        except KeyboardInterrupt:
            print("Monitoring stopped.")


if __name__ == '__main__':
    monitor_drive()
