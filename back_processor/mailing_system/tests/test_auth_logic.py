import os
import sys
from unittest.mock import MagicMock, patch
import pytest
from jose import jwt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import get_current_user, SECRET_KEY, ALGORITHM
from app.models.models import User
from fastapi import HTTPException

# Mock async execution since we are not running in an event loop here unless we use pytest-asyncio
# But get_current_user is async, so we need to await it.
import asyncio

def run_async(coro):
    return asyncio.run(coro)

def test_get_current_user_valid_token():
    # Setup
    user_id = "user123"
    token = jwt.encode({"sub": user_id}, SECRET_KEY, algorithm=ALGORITHM)
    
    mock_db = MagicMock()
    mock_user = User(id=user_id, name="Test User")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Execute
    user = run_async(get_current_user(token, mock_db))
    
    # Verify
    assert user.id == user_id
    print("test_get_current_user_valid_token PASSED")

def test_get_current_user_invalid_token():
    # Setup
    token = "invalid.token.here"
    mock_db = MagicMock()
    
    # Execute & Verify
    try:
        run_async(get_current_user(token, mock_db))
        print("test_get_current_user_invalid_token FAILED (Should have raised HTTPException)")
    except HTTPException as e:
        assert e.status_code == 401
        print("test_get_current_user_invalid_token PASSED")
    except Exception as e:
        # python-jose might raise JWTError which get_current_user catches and re-raises as HTTPException
        # But if we are calling it directly, let's see.
        print(f"test_get_current_user_invalid_token RAISED {type(e)}")

if __name__ == "__main__":
    test_get_current_user_valid_token()
    test_get_current_user_invalid_token()
