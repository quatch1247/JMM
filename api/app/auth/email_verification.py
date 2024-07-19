import os
import base64
import random
import re
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import get_settings

settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def generate_verification_code():
    return str(random.randint(100000, 999999))

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print(f"Message Id: {message['id']}")
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def is_valid_solideos_email(email):
    return re.match(r"[^@]+@solideos\.com$", email) is not None

def send_email_verification_code(to_email):
    # if not is_valid_solideos_email(to_email):
    #     raise ValueError("Invalid email address. Only @solideos.com addresses are allowed.")

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    }
                },
                SCOPES
            )
            creds = flow.run_console()
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        verification_code = generate_verification_code()
        subject = "인증 코드"
        body = f"인증 코드는 {verification_code} 입니다."
        message = create_message("me", to_email, subject, body)
        send_message(service, "me", message)
        return verification_code
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
