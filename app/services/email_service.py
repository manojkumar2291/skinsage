import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import os

SMTP_SERVER =settings.EMAIL_HOST
SMTP_PORT = settings.EMAIL_PORT
SMTP_USER = settings.EMAIL_USER
SMTP_PASSWORD = settings.EMAIL_PASS

def send_email_sync(to_email: str, subject: str, body: str):
    
    print('--- Preparing to send email ---')
    print(f"From: {SMTP_USER}")
    print(f"To: {to_email}")

    try:
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

       
        msg.attach(MIMEText(body, 'plain'))

        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        
        server.login(SMTP_USER, SMTP_PASSWORD)

        
        text = msg.as_string()
        server.sendmail(SMTP_USER, to_email, text)
        
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        
        raise e