import os
import sys

# Add the directory to sys.path to import ai_services
sys.path.append(r'd:\freelancing\Staffing\development\back_processor\mailing_system')

from app.services.ai_services import GeminiService

def test_email_generation():
    service = GeminiService()
    
    print("\n--- Testing generate_email_body ---")
    body = service.generate_email_body(
        job_role="Software Engineer", 
        job_description="We need a Python developer with experience in AI.", 
        relevant_context=[{"text": "Experienced Python developer with 5 years of experience."}]
    )
    print("generated email body:\n", body)
    
    print("\n--- Testing generate_initial_email_body ---")
    body_init, summary, reqs = service.generate_initial_email_body(
        vendor_name="Tech Solutions", 
        job_role="Data Scientist", 
        job_description="Looking for valid Data Scientist with NLP experience.", 
        relevant_context=[{"text": "Built NLP models using Transformers."}]
    )
    print("generated initial email body:\n", body_init)

if __name__ == "__main__":
    test_email_generation()
