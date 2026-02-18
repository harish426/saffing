import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.models import User
from app.services.email_services import mail

def test_mail_initialization_with_user():
    # Mock user object
    mock_user = MagicMock(spec=User)
    mock_user.jobEmail = "test@example.com"
    mock_user.appPassword = "password123"
    
    # Initialize mail service
    email_service = mail(mock_user)
    
    # Verify credentials
    assert email_service.smtp_username == "test@example.com"
    assert email_service.smtp_password == "password123"
    print("test_mail_initialization_with_user PASSED")

def test_mail_initialization_without_user():
    # Mock env vars
    with patch.dict(os.environ, {"SMTP_USERNAME": "env@example.com", "SMTP_PASSWORD": "envpassword"}):
        email_service = mail()
        
        # Verify credentials from env
        assert email_service.smtp_username == "env@example.com"
        assert email_service.smtp_password == "envpassword"
        print("test_mail_initialization_without_user PASSED")

if __name__ == "__main__":
    test_mail_initialization_with_user()
    test_mail_initialization_without_user()
