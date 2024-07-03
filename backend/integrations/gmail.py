import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64

CREDENTIALS = "C:/Users/marka/fun/briefly/backend/integrations/markacastellano2@gmail_credentials_desktop.json"
TOKEN = "C:/Users/marka/fun/briefly/backend/integrations/token.json"

def get_google_api_service(service_name: str, version: str):
    # SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/calendar"]
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        assert (creds) is not None, "No GMAIL credientals found"
        with open(TOKEN, 'w') as token:
            token.write(creds.to_json())
    return build(service_name, version, credentials=creds)


def get_messages_since_yesterday():
    service = get_google_api_service('gmail', 'v1')
    
    # Calculate yesterday's date and today's date
    yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    now = datetime.now()
    
    # Convert dates to RFC 3339 format
    yesterday_str = yesterday.strftime('%Y/%m/%d')
    now_str = now.strftime('%Y/%m/%d')
    
    # Construct the query
    query = f'after:{yesterday_str} before:{now_str}'
    
    # Get messages
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    downloaded_messages = []

    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        subject = next(header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject')
        sender = next(header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'from')
        
        # Get the message body
        if 'parts' in msg['payload']:
            body = msg['payload']['parts'][0]['body']
        else:
            body = msg['payload']['body']
        
        if 'data' in body:
            body_data = base64.urlsafe_b64decode(body['data']).decode('utf-8')
        else:
            body_data = "No message body"
        
        downloaded_messages.append({
            'subject': subject,
            'sender': sender,
            'body': body_data,
            'date': msg['internalDate']
        })
    
    return downloaded_messages

def get_recent_messages():
    service = get_google_api_service('gmail', 'v1')
    
    # Get the 10 most recent messages
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    
    downloaded_messages = []
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        subject = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject'), 'No Subject')
        sender = next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'from'), 'Unknown Sender')
        
        # Get the message body
        if 'parts' in msg['payload']:
            body = msg['payload']['parts'][0]['body']
        else:
            body = msg['payload']['body']
        
        body_data = base64.urlsafe_b64decode(body.get('data', '')).decode('utf-8') if 'data' in body else "No message body"
        
        downloaded_messages.append({
            'subject': subject,
            'sender': sender,
            'body': body_data,
            'date': msg['internalDate']
        })
    return downloaded_messages


def get_attendee_email_threads(attendee, max_threads=3):
    service = get_google_api_service('gmail', 'v1')
    query = f"to:{attendee} OR from:{attendee}"
    threads = service.users().threads().list(userId='me', q=query).execute().get('threads', [])
    
    thread_messages = []
    for thread in threads[:max_threads]:
        thread_data = service.users().threads().get(userId='me', id=thread['id']).execute()
        for msg in thread_data['messages']:
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
            
            if 'parts' in msg['payload']:
                body = msg['payload']['parts'][0]['body']
            else:
                body = msg['payload']['body']
            
            body_data = base64.urlsafe_b64decode(body.get('data', '')).decode('utf-8') if 'data' in body else "No message body"
            
            thread_messages.append({
                'subject': subject,
                'sender': sender,
                'body': body_data
            })
    
    return thread_messages

if __name__ == '__main__':
    messages = get_messages_since_yesterday()
    print(f"Downloaded {len(messages)} messages.")
    for msg in messages:
        print(f"Subject: {msg['subject']}")
        print(f"From: {msg['sender']}")
        print(f"Date: {msg['date']}")
        print(f"Body: {msg['body']}...")
        print("---")