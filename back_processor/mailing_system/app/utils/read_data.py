from app.core.database import SessionLocal
from app.models.models import JobDescription, User
import logging
logger = logging.getLogger(__name__)



from sqlalchemy.orm import joinedload

class read_data:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_active_jobs_with_vendor_emails(self):
        try:
            print("Fetching Active JobDescriptions with Vendor Emails...")
            jobs = self.db.query(JobDescription).options(joinedload(JobDescription.user)).filter(
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
            
    def get_unique_vendors(self, user_email: str):
        try:
            print(f"Fetching Unique Vendors for user: {user_email}...")
            # Join JobDescription with User to filter by user_email
            vendors = self.db.query(
                JobDescription.vendorName, 
                JobDescription.vendorEmail
            ).join(User, JobDescription.userId == User.id).filter(
                User.email == user_email,
                JobDescription.vendorEmail != None,
                JobDescription.vendorEmail != "",
                JobDescription.isActive == True
            ).distinct().all()

            if not vendors:
                print("No unique vendors found.")
            else:
                for vendor in vendors:
                    print(f"Vendor: {vendor.vendorName} | Email: {vendor.vendorEmail}")

            return vendors
        except Exception as e:
            logger.error(f"Error fetching unique vendors: {e}", exc_info=True)
            return []
        finally:
            self.db.close()

if __name__ == "__main__":
    read_data().get_active_jobs_with_vendor_emails()
