import sys
import os
from database import SessionLocal, engine, Base
from models import Resume


class ResumeHandler:
    def __init__(self):
        self.session = SessionLocal()

    def upload_pdf(self, file_path):
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return

        # Ensure table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if not inspector.has_table("resume"):
            print("Table 'resume' not found in DB. Creating...")
            Base.metadata.create_all(bind=engine)
        else:
            print("Table 'resume' already exists.")

        session = self.session
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            filename = os.path.basename(file_path)
            new_resume = Resume(
                filename=filename,
                content=file_content
            )
            
            session.add(new_resume)
            session.commit()
            session.refresh(new_resume)
            print(f"Successfully uploaded '{filename}' with ID: {new_resume.id}")
            
        except Exception as e:
            session.rollback()
            print(f"Error uploading file: {e}")
        finally:
            session.close()

    def delete_pdf(self):
        if not self.session:
            self.session = SessionLocal()
        
        try:
            self.session.query(Resume).delete()
            self.session.commit()
            print("All files deleted successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting file: {e}")
        finally:
            self.session.close()



    def get_and_save_pdf(self, output_path="retrieved_resume.pdf"):
        if not self.session:
            self.session = SessionLocal()
        try:
            # Explicitly use the imported Resume model
            resume_record = self.session.query(Resume).order_by(Resume.id.desc()).first()
            if resume_record:
                with open(output_path, "wb") as f:
                    f.write(resume_record.content)
                print(f"Resume (ID: {resume_record.id}) saved to '{output_path}'")
                return True
            else:
                print("No resume found in database.")
                return False

        except Exception as e:
            self.session.rollback()
            print(f"Error fetching file: {e}")
            return False
        finally:
            self.session.close()

if __name__ == "__main__":
    handler = ResumeHandler()
    
    # Download the latest resume from DB
    print("Attempting to download latest resume from database...")
    if handler.get_and_save_pdf("retrieved_resume.pdf"):
        print("\nSuccess: Resume downloaded to 'retrieved_resume.pdf'.")
        print("Please verify this file opens correctly in your PDF viewer.")
    else:
        print("\nFailed to download resume.")
