from app.core.database import SessionLocal
from app.models.models import JobDescription



class read_data:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_active_jobs_with_vendor_emails(self):
        try:
            print("Fetching Active JobDescriptions with Vendor Emails...")
            jobs = self.db.query(JobDescription).filter(
            JobDescription.vendorEmail!=None,
            JobDescription.isActive == True
        ).all()

            if not jobs:
                print("No matching jobs found.")
            for job in jobs:
                print(f"ID: {job.id} | Role: {job.jobRole} | Vendor: {job.vendorName} | Email: {job.vendorEmail}")

            return jobs
        except Exception as e:
            with open("error.log", "w") as f:
                f.write(f"ERROR: {e}\n")
                import os
                url = os.getenv("DATABASE_URL", "NOT_SET")
                f.write(f"DEBUG: DATABASE_URL starts with: {url[:20] if url else 'None'}...\n")
            
        finally:
            self.db.close()

if __name__ == "__main__":
    read_data().get_active_jobs_with_vendor_emails()
