from fastapi import FastAPI, BackgroundTasks
import time
import os
import json
from app.core.database import engine, SessionLocal
from sqlalchemy import text
from pydantic import BaseModel
from app.utils.read_data import read_data
# from ai_services import get_Ai_Subject
from app.services.email_services import mail
from app.services.ai_services import GeminiService
from app.utils.tools import UserContext
import concurrent.futures
from fastapi import Request
from app.models.models import User
import logging
from app.core.logging_config import setup_logging
from app.services.ai_services_fresher import GeminiServiceFresher
from app.services.generate_resume_fresher import generate_fresher_resume_buffer
from fastapi.responses import StreamingResponse
import io

setup_logging()
logger = logging.getLogger(__name__)

from functools import lru_cache

# Initialize services lazily
@lru_cache()
def get_ai_service():
    return GeminiService()

# @lru_cache()
# def get_vector_store():
#     return LocalFAISSStore()

app = FastAPI()

# Initialize Resume Analyzer
from app.services.resume_analysor import ResumeAnalysor
from app.utils.resume_parser import extract_text_from_bytes
from app.utils.resume_parser import extract_text_from_bytes
from app.models.models import Resume
from app.core.database import get_latest_resume

resume_analyzer = ResumeAnalysor()

@app.post("/convert_resume_to_json")
async def convert_resume_to_json(request: Request):
    """
    Converts a resume (PDF/DOCX) stored in the database to a structured JSON format.
    Expects 'resume_id' in query params.
    """
    resume_id = request.query_params.get("resume_id")
    if not resume_id:
        return {"error": "resume_id is required"}

    try:
        # Fetch resume from DB
        with SessionLocal() as db:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            
            if not resume:
                return {"error": "Resume not found"}
            
            if not resume.content:
                 return {"error": "Resume content is empty"}

            # Extract Text
            text_content = extract_text_from_bytes(resume.content, resume.filename or "resume.pdf")
            
            if not text_content:
                return {"error": "Failed to extract text from resume"}

            # Analyze with Gemini
            json_data = resume_analyzer.parse_resume_to_json(text_content)
            
            # Save to Database
            resume.resumeData = json_data
            db.commit()
            db.refresh(resume)

            return {"status": "success", "data": json_data}

    except Exception as e:
        logger.error(f"Error in convert_resume_to_json: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

class FresherResumeBuilderRequest(BaseModel):
    description: str
    question: str
    user_id: str = None

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

@app.post("/test-email")
def test_email(email_request: EmailRequest, user_id: str = None):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first() if user_id else None
        
    success = mail(user).send_email(email_request.to_email, email_request.subject, email_request.body)
    
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
    logger.info("Background Task Started: Processing Emails...")
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
                            logger.info(f"Generating AI email for {application.jobRole} (Attempt {attempt + 1}/{MAX_RETRIES})...")
                            relevant_context = get_vector_store().search(application.jobDescription, k=3)
                            generated_body = get_ai_service().generate_email_body(application.jobRole, application.jobDescription, relevant_context)
                            
                            if "Error" in generated_body:
                                raise Exception(generated_body)
                                
                            body = generated_body
                            break # Success, exit loop
                        except Exception as ai_error:
                            logger.error(f"AI Generation failed: {ai_error}", exc_info=True)
                            
                            if attempt < MAX_RETRIES - 1:
                                print(f"Retrying in {RETRY_DELAY} seconds...")
                                time.sleep(RETRY_DELAY)
                            else:
                                logger.warning("Max retries reached. Aborting email send.")
                                body = None
                                break

                else:
                    # body=f"I hope you are doing well. \n\nI have 10+ years of experience in {application.jobRole.split('/')[0]} and big data analytics, with strong expertise in machine learning, cloud platforms (AWS), large-scale data processing, and advanced analytics. My background includes building and deploying production-grade ML models, real-time analytics solutions, and executive dashboards, closely aligning with the requirements outlined in the job description. I have attached my resume for your review and would welcome the opportunity to discuss how my skills and experience can contribute to your team.\n\nThank you for your time and consideration. I look forward to hearing from you.\n\nBest regards,\nHarish Jamallamudi"
                    body=f"Dear {application.vendorName},\n\nI hope you are doing well.\\\n\nI wanted to follow up on my email sent yesterday regarding the {application.jobRole.split('/')[0]} opportunity. I’m very enthusiastic about this role and the possibility of contributing my experience in big data analytics, machine learning, and cloud-based solutions to your team.\n\nI understand you may be reviewing many applications, but I would greatly appreciate the opportunity to discuss how my background and skills align with your needs. Please let me know if there is any additional information I can provide.\n\nThank you again for your time and consideration. I look forward to hearing from you.\n\nBest regards,\nHarish Jamallamudi"

                if body:
                    logger.info("Sending email", extra={
                        "to": application.vendorEmail,
                        "subject": subject,
                        "body_preview": body[:100]
                    })
                  
                    if application.user:
                        mail(application.user).send_email(application.vendorEmail, subject, body)
                    else:
                        logger.warning(f"Skipping email to {application.vendorEmail} because no user is associated with this job.")
                    # print(f"Sent email to {application.vendorEmail}")
                    
                    logger.info("Waiting 5 seconds before next request...")
                    time.sleep(10)
                else:
                    logger.warning(f"Skipping email to {application.vendorEmail} due to AI error.")
    except Exception as e:
        logger.error(f"Error in background task: {e}", exc_info=True)

@app.get("/send-remark")
def send_remark(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_and_send_emails)
    return {"status": "success", "message": "Email processing started in background. Check terminal for output."}



@app.get("/send_resume")
async def send_resume(request:Request):
    from fastapi.responses import StreamingResponse
    import io

    user_id = request.query_params.get("user_id")
    current_user = None
    if user_id:
        with SessionLocal() as db:
            current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        return {"status": "error", "message": "User not found or user_id missing"}
    
    # to_email=request.query_params.get("to_email")
    # role=request.query_params.get("role")
    user_name=current_user.name
    jobRole=request.query_params.get("jobRole")
    jobDescription=request.query_params.get("jobDescription")
    vendorName=request.query_params.get("vendorName")
    vendorEmail=request.query_params.get("vendorEmail")

    # Build dynamic user context for AI sign-off
    user_ctx = UserContext(
        name=current_user.name or "",
        email=current_user.jobEmail or current_user.email or "",
        phone=current_user.phoneNumber or "",
        linkedin_url=current_user.linkedinUrl or "",
    )
    
    logger.info(f"Background Task Started: Processing Resume for {vendorEmail if vendorEmail else 'Download'}")

    try:


        from app.core.database import get_latest_resume, get_latest_resume_for_user

        # gets the resume data from the database
        with SessionLocal() as db:
            # resume_entry = get_latest_resume(db)
            resume_entry = get_latest_resume_for_user(db, current_user.id)
            
            if not resume_entry or not resume_entry.resumeData:
                logger.error(f"Error: No resume data found in database for user {current_user.id}.")
                return {"status": "error", "message": "No resume data found in database."}
                
            resume_data = resume_entry.resumeData

        # Common Resume Generation Logic
        # We need to generate the resume regardless of whether we send it or download it
        # BUT for download, we might skip the email generation part if it's strictly just "tailor resume for JD"
        # However, the current logic generates email body first. 
        # For simplicity and adhering to "tailor resume according to jd", we can reuse the logic or extract it.
        
        # If vendorEmail is present -> Send Email
        if vendorEmail:
            # subject = f"Looking for AI/ML Engineer or Data Scientist role"
            # subject = f"Looking for {jobRole} role"
            subject = f"Great to hear from you about this {jobRole} role"
            MAX_RETRIES = 3
            RETRY_DELAY = 10  # Seconds
            body = ""

            for attempt in range(MAX_RETRIES):
                try:
                    logger.info(f"Generating AI email for {jobRole} (Attempt {attempt + 1}/{MAX_RETRIES})...")
                    # Fallback to jobRole if jobDescription is missing
                    # search_query = jobDescription if jobDescription else jobRole
                    # relevant_context = get_vector_store().search(search_query, k=3)
                    
                    # Use the new initial email generation method
                    generated_body, jd_summary, job_requirements = get_ai_service().generate_initial_email_body(vendorName, jobRole, jobDescription, resume_data, user_ctx)
                    
                    if "Error" in generated_body: # Check if ai_service returned an error string
                         raise Exception(generated_body)

                    body = generated_body
                    # You can use jd_summary and job_requirements here if needed in the future
                    logger.info(f"JD Summary: {jd_summary}")
                    logger.info(f"Job Requirements: {job_requirements}")
                    break # Success
                
                except Exception as ai_error:
                    logger.error(f"AI Generation failed: {ai_error}", exc_info=True)
                    
                    if attempt < MAX_RETRIES - 1:
                        logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        logger.warning("Max retries reached. Aborting email send.")
                        return {"status": "partial_success", "message": "Data saved but email not sent due to AI error"}

            if body and "Error" not in body:
                logger.info("Sending email", extra={
                    "to": vendorEmail,
                    "subject": subject,
                    "body_preview": body[:100]
                })

                # Generate Resume DOCX in-memory
                from app.services.generate_resume_docx import generate_resume_buffer
                # import os
                
                # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # json_source = os.path.join(base_dir, "data", "resume", "resume.json")
                

                resume_buffer = generate_resume_buffer(resume_data, jobDescription, job_requirements)
                
                if resume_buffer:
                    email_sent = mail(current_user).send_email_with_attachment_buffer(
                        vendorEmail, 
                        subject, 
                        body, 
                        resume_buffer, 
                        filename=f"{user_name}_resume.docx"
                    )
                
                    if email_sent:
                        return {"status": "success", "message": "Email sent successfully with tailored resume"}
                    else:
                        return {"status": "error", "message": "Failed to send email. Check server logs."}
                else:
                    return {"status": "error", "message": "Failed to generate resume buffer."}
            else:
                logger.warning("Skipping email due to invalid body or error.")
                return {"status": 404, "message": "Data saved but email not sent due to AI error"}

        # If vendorEmail is MISSING -> Generate and Return Download
        else:
            logger.info("Vendor Email missing. Generating resume for download.")
            
            try:
                # We reuse this to get job_requirements. 
                # Assuming 'Vendor' can be generic if missing.
                temp_vendor_name = vendorName if vendorName else "Hiring Manager"
                
                # FIX: Pass user_ctx and use resume_data instead of undefined relevant_context
                _, jd_summary, job_requirements = get_ai_service().generate_initial_email_body(
                    temp_vendor_name, jobRole, jobDescription, resume_data, user_ctx
                )
                
                from app.services.generate_resume_docx import generate_resume_buffer

                # FIX: Pass jobDescription to generate_resume_buffer for full context
                resume_buffer = generate_resume_buffer(resume_data, jobDescription, job_requirements)
                
                if resume_buffer:
                    # Reset buffer position to beginning
                    resume_buffer.seek(0)
                    filename = f"{user_name}_resume.docx"
                    
                    return StreamingResponse(
                        resume_buffer,
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"Content-Disposition": f"attachment; filename={filename}"}
                    )
                else:
                     return {"status": "error", "message": "Failed to generate resume buffer."}

            except Exception as e:
                logger.error(f"Error generating download resume: {e}", exc_info=True)
                return {"status": "error", "message": str(e)}

    except Exception as e:
        logger.error(f"Error in send_resume: {e}", exc_info=True)
        return {"status": 404, "message": str(e)}

async def process_and_send_greetings(user_email: str, current_user: User):
    logger.info(f"Background Task Started: Sending Greetings to Vendors for {user_email}...")
    
    from app.core.database import get_latest_resume_for_user
    with SessionLocal() as db:
        resume_entry = get_latest_resume_for_user(db, current_user.id)
        if not resume_entry or not resume_entry.resumeData:
            logger.error(f"No resume data found for user {current_user.id}.")
            return
        resume_data = resume_entry.resumeData

    vendors = read_data().get_unique_vendors(user_email)
    if not vendors:
        logger.warning(f"No unique vendors found for user {user_email}.")
        return

    # User Context for AI and signature
    user_ctx = UserContext(
        name=current_user.name or "",
        email=current_user.jobEmail or current_user.email or "",
        phone=current_user.phoneNumber or "",
        linkedin_url=current_user.linkedinUrl or "",
    )

    try:
        # Generate the core message ONCE
        logger.info("Generating 200-word AI greeting core content...")
        core_body = get_ai_service().generate_greeting_email(resume_data, user_ctx)

        if not core_body or "Error" in core_body:
            logger.error(f"Failed to generate greeting core content: {core_body}")
            return

        subject = f"Greeting from {current_user.name} - Inquiry regarding AI/ML Roles"

        for vendor in vendors:
            vendor_email = vendor.vendorEmail
            if not vendor_email:
                continue

            vendor_name = vendor.vendorName or "Hiring Manager"
            
            # Assemble the final email body
            full_body = f"Dear {vendor_name},\n\n{core_body}\n\n"
            full_body += f"Best regards,\n{user_ctx.name}\n"
            if user_ctx.phone:
                full_body += f"{user_ctx.phone}\n"
            full_body += f"{user_ctx.email}\n"
            if user_ctx.linkedin_url:
                full_body += f"{user_ctx.linkedin_url}\n"

            logger.info(f"Sending greeting email to {vendor_name} ({vendor_email})")
            mail(current_user).send_email(vendor_email, subject, full_body)
            
            # Rate limiting / polite delay
            logger.info("Waiting 10 seconds before next greeting...")
            time.sleep(10)

    except Exception as e:
        logger.error(f"Error in greeting background task: {e}", exc_info=True)

@app.get("/send-greeting-to-all-vendors")
async def send_greeting_to_all_vendors(user_email: str, background_tasks: BackgroundTasks = None):
    """
    Endpoint to send personalized greetings to all unique vendors for a specific user.
    Takes user_email as an argument and retrieves vendors from the database.
    """
    if not user_email:
        return {"status": "error", "message": "user_email is required"}

    with SessionLocal() as db:
        current_user = db.query(User).filter(User.email == user_email).first()
        if not current_user:
            return {"status": "error", "message": "User not found"}

    if background_tasks:
        background_tasks.add_task(process_and_send_greetings, user_email, current_user)
        return {"status": "success", "message": f"Greeting process for {user_email} started in background."}
    else:
        # Fallback if BackgroundTasks is not injected (though FastAPI usually takes care of it)
        await process_and_send_greetings(user_email, current_user)
        return {"status": "success", "message": f"Greeting process for {user_email} completed."}
@app.get("/groupby_vendor")
async def groupby_vendor(request: Request):
    body = await request.json()
    if body.get("vendor") and body.get("month"):
        logger.info(f"Grouping by vendor {body}")
        return {"received": body}
    else:
        return {"error": "Missing vendor or month"}


@app.get("/groupby_location")
def groupby_location():
    pass
    
@app.post("/fresher_resume_builder")
async def fresher_resume_builder(request: FresherResumeBuilderRequest):
    """
    Builder for fresher resumes: tailoring, cover letters, and Q&A.
    """
    logger.info(f"Fresher Resume Builder Request: {request.question[:50]}...")
    
    try:
        # 1. Load the base resume data (Local only as requested)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        harish_json_path = os.path.join(os.path.dirname(base_dir), "data", "resume", "resume_harish.json")
        
        if os.path.exists(harish_json_path):
            with open(harish_json_path, "r") as f:
                resume_data = json.load(f)
                user_name = resume_data.get("personal_info", {}).get("name", "Harish")
        else:
            return {"status": "error", "message": "Local resume data not found."}

        # 2. Process the request with AI
        svc = GeminiServiceFresher()
        result = svc.process_builder_request(resume_data, request.description, request.question)

        # 3. Handle the response based on type
        if result["type"] == "text":
            return {"status": "success", "intent": result["intent"], "content": result["content"]}
        
        elif result["type"] == "resume":
            # Generate the tailored resume as a buffer
            tailored_json = result["content"]
            buffer = generate_fresher_resume_buffer(tailored_json)
            
            filename = f"harish_resume.docx"
            return StreamingResponse(
                buffer,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return {"status": "error", "message": result["content"]}

    except Exception as e:
        logger.error(f"Error in fresher_resume_builder: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.get("/get_contact_vendor_details")
def vendor_details():
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)