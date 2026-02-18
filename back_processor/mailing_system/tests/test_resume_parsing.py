import requests
from app.core.database import SessionLocal
from app.models.models import Resume

def get_latest_resume_id():
    db = SessionLocal()
    try:
        # Get the latest uploaded resume
        resume = db.query(Resume).order_by(Resume.createdAt.desc()).first()
        if resume:
            print(f"Found Resume ID: {resume.id}, Filename: {resume.filename}")
            return resume.id
        else:
            print("No resumes found in database.")
            return None
    finally:
        db.close()

def test_resume_conversion(resume_id):
    url = f"http://127.0.0.1:8001/convert_resume_to_json?resume_id={resume_id}"
    print(f"Calling API: {url}")
    
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            import json
            with open("resume_output.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Result saved to resume_output.json")
        else:
            print(f"Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    resume_id = get_latest_resume_id()
    if resume_id:
        test_resume_conversion(resume_id)
