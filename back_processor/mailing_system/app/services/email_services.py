import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv()


from app.models.models import User

class mail:
    def __init__(self, user: User = None):
        if user and user.jobEmail and user.appPassword:
            self.smtp_username = user.jobEmail
            self.smtp_password = user.appPassword
            # Default to env or gmail if not in user (assuming user only stores creds, not server config)
            self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            self.smtp_port = os.getenv("SMTP_PORT", "587")
        else:
            self.smtp_server = os.getenv("SMTP_SERVER")
            self.smtp_port = os.getenv("SMTP_PORT")
            self.smtp_username = os.getenv("SMTP_USERNAME")
            self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Sends an email using SMTP server details from environment variables.
        Returns True if successful, False otherwise.
        """

        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            print("Error: SMTP credentials are incomplete in environment variables.")
            return False        

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Connect to the server
            port = int(self.smtp_port)
            server = smtplib.SMTP(self.smtp_server, port)
            server.starttls()  # Secure the connection
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            # print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            # print(f"Failed to send email: {e}")
            return False

    def send_email_with_pdf(self, to_email: str, subject: str, body: str, pdf_path: str) -> bool:
        """
        Sends an email with a PDF attachment using SMTP server details from environment variables.
        Returns True if successful, False otherwise.
        """
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            print("Error: SMTP credentials are incomplete in environment variables.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                    msg.attach(attach)
            else:
                 print(f"Error: PDF file not found at {pdf_path}")
                 return False

            port = int(self.smtp_port)
            server = smtplib.SMTP(self.smtp_server, port)
            server.starttls()  # Secure the connection
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            # print(f"Email with PDF sent successfully to {to_email}")
            return True
        except Exception as e:
            # print(f"Failed to send email with PDF: {e}")
            return False

    def send_email_with_attachment_buffer(self, to_email: str, subject: str, body: str, file_buffer, filename: str) -> bool:
        """
        Sends an email with an attachment from a memory buffer.
        """
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            print("Error: SMTP credentials are incomplete in environment variables.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Attach from buffer
            if file_buffer:
                # Determine content type based on extension, defaulting to application/octet-stream
                import mimetypes
                ctype, encoding = mimetypes.guess_type(filename)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                
                maintype, subtype = ctype.split('/', 1)
                
                attach = MIMEApplication(file_buffer.read(), _subtype=subtype)
                attach.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attach)
            else:
                 print(f"Error: File buffer is empty")
                 return False

            port = int(self.smtp_port)
            server = smtplib.SMTP(self.smtp_server, port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            # print(f"Email with attachment ({filename}) sent successfully to {to_email}")
            return True
        except Exception as e:
            # print(f"Failed to send email with attachment: {e}")
            return False



    def send_linkedin_comment(self, to_email: str, subject: str, body: str) -> bool:
        pass