import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP_SSL

logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

def load_env(filename: str = '.env'):
    with open(filename, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip comments and blank lines
            key, value = line.split('=', 1)
            value = value.strip('"').strip("'")
            os.environ[key] = value  # Set the value in os.environ

# Set up the server
def connect_smtp() -> SMTP_SSL | None:
    try:
        server = smtplib.SMTP_SSL(os.getenv('MAIL_HOST'), int(os.getenv('MAIL_PORT')))
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
    except Exception as e:
        logging.error(f"SMTP error occurred: {str(e)}")
        return None

    return server

# Quit the server
def close_smtp(server: SMTP_SSL):
    server.quit()

# Email sending VIA SMTP SSL
def send_email(server: SMTP_SSL|None,subject: str, body: str, recipient: str) -> bool:
    if server is None:
        logging.error(f"SMTP server is not set in connect_smtp")
        return False

    msg = MIMEMultipart()
    msg['From'] = formataddr((os.getenv('MAIL_FROM_NAME'), os.getenv('MAIL_USERNAME')))
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server.send_message(msg)
    except Exception as e:
        logging.error(f"SMTP error occurred: {str(e)}")
        return False

    return True

def write_file(path: str, data: [any, any], data_type: str = '') -> None:
    with open(path, 'w', encoding='utf-8') as file:
        if data_type == 'json':
            json.dump(data, file, indent=4)
        else:
            file.write(data)

def read_file(path: str, data_type: str = '') -> str | [any, any]:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            if data_type == '':
                return json.load(file)
            else:
                return file.read()
    return None