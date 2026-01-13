from database import SessionLocal
from models import JobDescription

def main():
    db = SessionLocal()
    try:
        print("Fetching JobDescriptions...")
        jobs = db.query(JobDescription).all()
        if not jobs:
            print("No jobs found in the database.")
        for job in jobs:
            print(f"ID: {job.id} | Role: {job.jobRole} | Company: {job.company} | Active: {job.isActive}")
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(f"ERROR: {e}\n")
            import os
            url = os.getenv("DATABASE_URL", "NOT_SET")
            f.write(f"DEBUG: DATABASE_URL starts with: {url[:20] if url else 'None'}...\n")

    finally:
        db.close()

if __name__ == "__main__":
    main()
