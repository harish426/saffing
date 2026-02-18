import os
import sys
from unittest.mock import MagicMock, patch

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import test_email, EmailRequest
from app.models.models import User

def test_test_email_endpoint_with_userid():
    # Setup
    user_id = "user123"
    email_req = EmailRequest(to_email="test@example.com", subject="Test", body="Body")
    
    mock_user = User(id=user_id, jobEmail="user@example.com", appPassword="password")
    
    # Mock SessionLocal to return our mock user
    with patch('app.main.SessionLocal') as mock_session_cls:
        mock_db = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock mail service to verifying it's called with our user
        with patch('app.main.mail') as mock_mail_cls:
            mock_mail_instance = mock_mail_cls.return_value
            mock_mail_instance.send_email.return_value = True
            
            # Execute
            response = test_email(email_req, user_id=user_id)
            
            # Verify
            mock_mail_cls.assert_called_with(mock_user)
            mock_mail_instance.send_email.assert_called_with("test@example.com", "Test", "Body")
            print("test_test_email_endpoint_with_userid PASSED")

if __name__ == "__main__":
    test_test_email_endpoint_with_userid()
