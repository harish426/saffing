
import sys
import os

# Add the parent directory to sys.path to resolve app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, get_latest_resume_for_user
from app.models.models import User, Resume

def test_resume_fetch():
    db = SessionLocal()
    try:
        # 1. Get a user who has resumeData
        # Join User and Resume tables to find a user who has uploaded a resume with data
        resume_with_data = db.query(Resume).filter(Resume.resumeData.isnot(None)).first()
        
        if not resume_with_data:
            print("No resumes with data found in the database.")
            return

        user_id = resume_with_data.userId
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
             print(f"Resume found but user {user_id} does not exist.")
             return

        print(f"Testing with User: {user.name} (ID: {user.id})")

        # 2. Check if this user has any resumes
        user_resumes = db.query(Resume).filter(Resume.userId == user.id).all()
        print(f"User has {len(user_resumes)} resumes in total.")

        # 3. Test get_latest_resume_for_user
        latest_resume = get_latest_resume_for_user(db, user.id)
        
        if latest_resume:
            print(f"Successfully fetched latest resume for user {user.id}")
            print(f"Resume ID: {latest_resume.id}")
            print(f"Created At: {latest_resume.createdAt}")
            if latest_resume.userId != user.id:
                print("ERROR: Fetched resume belongs to a different user!")
            else:
                print("PASSED: Resume belongs to the correct user.")
        else:
            print("No resume found with resumeData for this user.")
            if user_resumes:
                 print("Note: User has resumes but maybe none with 'resumeData' populated.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_resume_fetch()
