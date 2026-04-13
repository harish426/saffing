import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import logging
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path=_env_path)

logger = logging.getLogger(__name__)


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
            logger.error("SMTP credentials are incomplete. server=%s port=%s username=%s password_set=%s",
                         self.smtp_server, self.smtp_port, self.smtp_username, bool(self.smtp_password))
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
            
            logger.info("Email sent successfully to %s", to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, e, exc_info=True)
            return False

    def send_email_with_pdf(self, to_email: str, subject: str, body: str, pdf_path: str) -> bool:
        """
        Sends an email with a PDF attachment using SMTP server details from environment variables.
        Returns True if successful, False otherwise.
        """
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            logger.error("SMTP credentials are incomplete. server=%s port=%s username=%s password_set=%s",
                         self.smtp_server, self.smtp_port, self.smtp_username, bool(self.smtp_password))
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
                logger.error("PDF file not found at %s", pdf_path)
                return False

            port = int(self.smtp_port)
            server = smtplib.SMTP(self.smtp_server, port)
            server.starttls()  # Secure the connection
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            logger.info("Email with PDF sent successfully to %s", to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email with PDF to %s: %s", to_email, e, exc_info=True)
            return False

    def send_email_with_attachment_buffer(self, to_email: str, subject: str, body: str, file_buffer, filename: str) -> bool:
        """
        Sends an email with an attachment from a memory buffer.
        """
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            logger.error("SMTP credentials are incomplete. server=%s port=%s username=%s password_set=%s",
                         self.smtp_server, self.smtp_port, self.smtp_username, bool(self.smtp_password))
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))
            logger.debug("Preparing email with attachment buffer: filename=%s", filename)
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
                logger.error("File buffer is empty for attachment: %s", filename)
                return False

            port = int(self.smtp_port)
            server = smtplib.SMTP(self.smtp_server, port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            logger.info("Email with attachment (%s) sent successfully to %s", filename, to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email with attachment to %s: %s", to_email, e, exc_info=True)
            return False



    def send_linkedin_comment(self, to_email: str, subject: str, body: str) -> bool:
        pass