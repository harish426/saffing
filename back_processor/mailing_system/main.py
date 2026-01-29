from fastapi import FastAPI, BackgroundTasks
import time
from database import engine, SessionLocal
from sqlalchemy import text
from pydantic import BaseModel
from read_data import read_data
# from ai_services import get_Ai_Subject
from email_services import mail
from ai_services import GeminiService
from vectorestore import LocalFAISSStore
import concurrent.futures
from fastapi import Request

# Initialize services
ai_service = GeminiService()
vector_store = LocalFAISSStore()

app = FastAPI()

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

@app.post("/test-email")
def test_email(email_request: EmailRequest):
    success = send_email(email_request.to_email, email_request.subject, email_request.body)
    if success:
        return {"status": "success", "message": "Email sent successfully"}
    else:
        return {"status": "error", "message": "Failed to send email. Check server logs."}


@app.get("/")
def read_root():
    return {"message": "Python Server is running"}

@app.get("/db-test")
def test_db():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"status": "success", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/send-remark")
async def process_and_send_emails():
    print("Background Task Started: Processing Emails...")
    application_details=read_data().get_active_jobs_with_vendor_emails()
    try:
        for application in application_details:
            if application.vendorEmail!="":
                # subject=ai_service.get_Ai_Subject(application.jobRole)
                subject="Following Up on My Application"
                
                if application.jobDescription:
                    MAX_RETRIES = 3
                    RETRY_DELAY = 20  # Seconds
                    
                    for attempt in range(MAX_RETRIES):
                        try:
                            print(f"Generating AI email for {application.jobRole} (Attempt {attempt + 1}/{MAX_RETRIES})...")
                            relevant_context = vector_store.search(application.jobDescription, k=3)
                            generated_body = ai_service.generate_email_body(application.jobRole, application.jobDescription, relevant_context)
                            
                            if "Error" in generated_body:
                                raise Exception(generated_body)
                                
                            body = generated_body
                            break # Success, exit loop
                        except Exception as ai_error:
                            print(f"AI Generation failed: {ai_error}")
                            
                            if attempt < MAX_RETRIES - 1:
                                print(f"Retrying in {RETRY_DELAY} seconds...")
                                time.sleep(RETRY_DELAY)
                            else:
                                print("Max retries reached. Aborting email send.")
                                body = None
                                break

                else:
                    # body=f"I hope you are doing well. \n\nI have 10+ years of experience in {application.jobRole.split('/')[0]} and big data analytics, with strong expertise in machine learning, cloud platforms (AWS), large-scale data processing, and advanced analytics. My background includes building and deploying production-grade ML models, real-time analytics solutions, and executive dashboards, closely aligning with the requirements outlined in the job description. I have attached my resume for your review and would welcome the opportunity to discuss how my skills and experience can contribute to your team.\n\nThank you for your time and consideration. I look forward to hearing from you.\n\nBest regards,\nHarish Jamallamudi"
                    body=f"Dear {application.vendorName},\n\nI hope you are doing well.\\\n\nI wanted to follow up on my email sent yesterday regarding the {application.jobRole.split('/')[0]} opportunity. I’m very enthusiastic about this role and the possibility of contributing my experience in big data analytics, machine learning, and cloud-based solutions to your team.\n\nI understand you may be reviewing many applications, but I would greatly appreciate the opportunity to discuss how my background and skills align with your needs. Please let me know if there is any additional information I can provide.\n\nThank you again for your time and consideration. I look forward to hearing from you.\n\nBest regards,\nHarish Jamallamudi"

                if body:
                    print("--------------------------------------------------")
                    print(f"To: {application.vendorEmail}")
                    print(f"Subject: {subject}")
                    print(f"Body Preview: {body[:100]}...")
                    # print("Body:", body) # Uncomment to see full body
                    print("--------------------------------------------------")
                  
                    mail().send_email(application.vendorEmail, subject, body)
                    # print(f"Sent email to {application.vendorEmail}")
                    
                    print("Waiting 5 seconds before next request...")
                    time.sleep(10)
                else:
                    print(f"Skipping email to {application.vendorEmail} due to AI error.")
    except Exception as e:
        print(f"Error in background task: {e}")

@app.get("/send-remark")
def send_remark(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_and_send_emails)
    return {"status": "success", "message": "Email processing started in background. Check terminal for output."}



@app.get("/send_resume")
async def send_resume(request:Request):
    # to_email=request.query_params.get("to_email")
    # role=request.query_params.get("role")
    jobRole=request.query_params.get("jobRole")
    jobDescription=request.query_params.get("jobDescription")
    vendorName=request.query_params.get("vendorName")
    vendorEmail=request.query_params.get("vendorEmail")
    
    print("Background Task Started: Processing Email for", vendorEmail)

    try:
        if vendorEmail:
            # subject = f"Looking for AI/ML Engineer or Data Scientist role"
            # subject = f"Looking for {jobRole} role"
            subject = f"Greate to hear from you about this {jobRole} role"
            MAX_RETRIES = 3
            RETRY_DELAY = 10  # Seconds
            body = ""

            for attempt in range(MAX_RETRIES):
                try:
                    print(f"Generating AI email for {jobRole} (Attempt {attempt + 1}/{MAX_RETRIES})...")
                    # Fallback to jobRole if jobDescription is missing
                    search_query = jobDescription if jobDescription else jobRole
                    relevant_context = vector_store.search(search_query, k=3)
                    
                    # Use the new initial email generation method
                    generated_body = ai_service.generate_initial_email_body(vendorName, jobRole, jobDescription, relevant_context)
                    
                    if "Error" in generated_body: # Check if ai_service returned an error string
                         raise Exception(generated_body)

                    body = generated_body
                    break # Success
                
                except Exception as ai_error:
                    print(f"AI Generation failed: {ai_error}")
                    
                    if attempt < MAX_RETRIES - 1:
                        print(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        print("Max retries reached. Aborting email send.")
                        return {"status": "partial_success", "message": "Data saved but email not sent due to AI error"}

            if body and "Error" not in body:
                print("--------------------------------------------------")
                print(f"To: {vendorEmail}")
                print(f"Subject: {subject}")
                print(f"Body Preview: {body[:100]}...")
                print("--------------------------------------------------")

                email_sent = mail().send_email_with_pdf(vendorEmail, subject, body, "D:/consultancy/docs/HARISH JAMALLAMUDI_Sr_ AI_engineer.docx")
                
                if email_sent:
                    return {"status": "success", "message": "Email sent successfully"}
                else:
                    return {"status": "error", "message": "Failed to send email. Check server logs."}
            else:
                print("Skipping email due to invalid body or error.")
                return {"status": 404, "message": "Data saved but email not sent due to AI error"}

    except Exception as e:
        print(f"Error in send_resume: {e}")
        return {"status": 404, "message": str(e)}

@app.get("/groupby_vendor")
async def groupby_vendor(request: Request):
    body = await request.json()
    if body.get("vendor") and body.get("month"):
        print("Grouping by vendor", body)
        return {"received": body}
    else:
        return {"error": "Missing vendor or month"}


@app.get("/groupby_location")
def groupby_location():
    pass
    
@app.get("/get_contact_vendor_details")
def vendor_details():
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)