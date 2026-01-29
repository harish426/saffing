import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv()


class mail:
    def __init__(self):
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
            
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
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
            
            print(f"Email with PDF sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email with PDF: {e}")
            return False



    def send_linkedin_comment(self, to_email: str, subject: str, body: str) -> bool:
        pass