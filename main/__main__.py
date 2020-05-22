from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
NUM_COPIES=3
INITIAL_FILE_NAME='tt000'
FINAL_FILE_NAME='tt999'

def callback(request_id, response, e):
    if e:
        # Handle error
        print(e)
    else:
        return response

def share_file(service, file):
    file_id = file['id']
    user_permission = {
        'type': 'anyone',
        'role': 'writer'
    }
    service.permissions().create(
            fileId=file_id,
            body=user_permission
    ).execute()
    result = service.files().get(fileId=file_id, fields='webViewLink').execute()
    return result

def copy_spreadsheet(service, dirID, fileId):
    print("copying files")
    #batch = service.new_batch_http_request(callback=callback)
    for g in ["c", "j"]:
        for n in range(1,NUM_COPIES+1):
            group_name = "{0}{1:03}".format(g, n)
            results = service.files().copy(fileId=fileId, body={"parents": [{"kind": "drive#fileLink", "id" : dirID}], "name": group_name}).execute()
            results = share_file(service, results)
            print(f"{group_name}: {results['webViewLink']}")
            service.files().update(fileId=fileId, body={"name": FINAL_FILE_NAME}).execute()
            
            
def clone_spreadsheets(service):
    results = service.files().list(q=f"name = '{INITIAL_FILE_NAME}' and mimeType = 'application/vnd.google-apps.spreadsheet'", fields="nextPageToken, files(id, name, parents)").execute()
    originals = results.get('files', [])
    for item in originals:
        copy_spreadsheet(service, item['parents'], item['id'])

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    clone_spreadsheets(service)

if __name__ == '__main__':
    main()