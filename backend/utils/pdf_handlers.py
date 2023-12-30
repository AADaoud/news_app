from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from google_auth_oauthlib.flow import InstalledAppFlow
from email import encoders
from xhtml2pdf import pisa
import os.path
import mimetypes
import base64
import pickle


def generate_pdf_report(message, filename):
    directory = "news_pdf"
    if not os.path.exists(directory):
        os.makedirs(directory)

    pdf_path = os.path.join(directory, filename)

    # Converting HTML to PDF
    result_file = open(pdf_path, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            message,                # the HTML to convert
            dest=result_file)       # file handle to recieve result

    result_file.close()                 # close output file

    print(f"PDF report generated: {pdf_path}")

    return pdf_path if not pisa_status.err else None


def send_email_with_pdf_report(pdf_filename):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message = create_message_with_attachment(
        sender='',
        to='',
        subject='News Report',
        message_text='Hello, your daily news report is ready.',
        file=os.path.join('news_pdf', pdf_filename)  # Provide the path to the PDF file
    )

    try:
        message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Email sent! Message ID: {message['id']}")
    except HttpError as error:
        print(f"An error occurred while sending the email: {error}")

def create_message_with_attachment(sender, to, subject, message_text, file):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        with open(file, 'r') as f:
            msg = MIMEText(f.read(), _subtype=sub_type)
    else:
        with open(file, 'rb') as f:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(f.read())
        encoders.encode_base64(msg)

    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}