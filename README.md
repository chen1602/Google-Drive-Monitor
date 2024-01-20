# Google Drive Permissions Monitor

### Project Description
This Python script monitors your Google Drive for new files, evaluating their sharing status. If a new file is in a publicly accessible folder, the script automatically adjusts its permissions to private, ensuring your sensitive content remains secure. The script provides clear output for each file, indicating its sharing status and any changes made by the program.

### Requirements
* Tested on - Python 3.10.11
* Google Drive API credentials file with the following permissions:

    **OAuth 2.0 Client for the SCOPE - https://www.googleapis.com/auth/drive**

### Usage:
* Install required dependencies.
* Set up Google Drive API credentials.
* Run the script for automated monitoring and securing of new files
  * `python3 monitor.py`
  * In the first execution, a browser window will pop up and ask you to give the application the permission noted above
  * Next, after the file token.json will be created, the tool will use it, and refresh it by itself when required

### Set up Google Drive API credentials - follow one of these:
* Use this guide, section **Set up your environment**
  * https://developers.google.com/drive/api/quickstart/python
  * Make sure you add the relevant SCOPE
* Go to the Google Cloud Console.
  * Create a new project or use an existing one.
  * Enable the "Google Drive API" for your project.
  * Setting up your OAuth consent screen - https://support.google.com/cloud/answer/10311615?hl=en&ref_topic=3473162&sjid=5240481285407109691-EU
    * In the Cloud Console, navigate to the "OAuth consent screen"
    * Publishing status - Testing 
    * User Type - External 
    * Add the relevant SCOPE - /auth/drive
    * Add user email address to the "Test Users"
  * Create OAuth 2.0 Credentials - https://support.google.com/cloud/answer/6158849?hl=en&ref_topic=3473162&sjid=5240481285407109691-EU
    * In the Cloud Console, navigate to the "APIs & Services" > "Credentials" section.
    * Click on "Create Credentials" and choose "OAuth client ID".
    * Select "Desktop app" as the application type.
    * Download the JSON file containing your credentials.
    * Rename the file to 'credentials.json' and put it in the project directory

### Security issues - attack surfaces
* Authorization Scopes - Excessive permissions could lead to unauthorized access to the drive resources, posing a security risk.
* Credentials File - To mitigate the risk of the user having to grant permissions each time the application runs, the API employs a token system. If an attacker gains access to the token file, they would have unrestricted access to the drive files without needing knowledge of the user credentials.

### Next steps
* Using an encryption for the token file with a key supplied by the user. If the key is changed, the app will require the user to allow the permissions again

### Output Example 
![alt text](https://github.com/chen1602/Google-Drive-Monitor/blob/main/output_example.png?raw=true)


