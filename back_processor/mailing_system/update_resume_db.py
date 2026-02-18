
import json
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, get_latest_resume
from app.models.models import Resume

def update_resume_data():
    json_path = os.path.join(os.getcwd(), "data", "resume", "resume.json")
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return

    with SessionLocal() as db:
        resume = get_latest_resume(db)
        if not resume:
            print("No resume found in database to update.")
            return

        print(f"Updating resume ID: {resume.id}")
        # Update the resumeData column
        resume.resumeData = new_data
        db.commit()
        db.refresh(resume)
        print("Resume data updated successfully in database.")

if __name__ == "__main__":
    update_resume_data()
