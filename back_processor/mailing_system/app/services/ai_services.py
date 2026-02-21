from google import genai
from google.genai import types
import os
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from app.utils.tools import Tools

load_dotenv()

class InitialEmailResponse(BaseModel):
    job_description_summary: str
    job_requirements: List[str]
    email_body: str

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # print("Warning: GEMINI_API_KEY not found in environment variables.")
            pass
        else:
            self.client = genai.Client(api_key=self.api_key)

    def generate_email_body(self, job_role: str, job_description: str, relevant_context: list[str]) -> str:
        """
        Generates a personalized email body using Gemini AI.
        """
        if not self.api_key:
            return "Error: Gemini API key not configured."

        context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])
        
        prompt = f"""
        You are a professional assistant helping a candidate apply for a job.
        
        Job Role: {job_role}
        
        Job Description:
        {job_description[:2000]}  # Truncate to avoid token limits if necessary
        
        Candidate's Resume Context (Matched from Vector Store):
        {context_str}
        
        Task:
        Draft a concise, professional, and persuasive cold email body to the hiring manager/recruiter. 
        - STRICTLY limit the body to exactly 3 sentences.
        - Analyze the "Candidate's Resume Context" and "Job Description" to create a high-impact message.
        - Do not include the subject line in the output.
        - ABSOLUTELY NO HTML TAGS or <br>. Use actual newlines (\n) for line breaks.
        - Separated sentences with a single newline.
        - Do not include placeholders like "[Your Name]". The candidate's name is Harish Jamallamudi.
        - Sign off exactly as follows (preceded by 2 newlines):
        
        Best regards,
        Harish Jamallamudi
        +13146696026
        harishjamalladi@gmail.com
        """

        # try:
        tools = [Tools.get_todays_date, Tools.calculate_experience, Tools.get_linkedin_profile, Tools.get_current_location]
        response = self.client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=tools
            )
        )
        text_response = response.text
        # Post-processing to ensure plain text
        if text_response:
             text_response = text_response.replace("<br>", "\n").replace("<br/>", "\n").replace("</br>", "\n")
        
        # Ensure sign-off separation
        if text_response and "Best regards," in text_response and "\n\nBest regards," not in text_response:
             text_response = text_response.replace("Best regards,", "\n\nBest regards,")
        return text_response if text_response else ""
        # except Exception as e:
        #     print(f"Error generating content with Gemini: {e}")
        #     raise e # Re-raise for main.py to handle


    def generate_initial_email_body(self, vendor_name: str, job_role: str, job_description: str, relevant_context: list[str]) -> tuple[str, str, list[str]]:
        """
        Generates an initial contact email body, JD summary, and requirements list using Gemini AI.
        Returns: (email_body, job_description_summary, job_requirements)
        """
        if not self.api_key:
            return "Error: Gemini API key not configured.", "", []

        context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])
        
        prompt = f"""
        You are a professional assistant helping a candidate apply for a job.
        
        Job Role: {job_role}
        Vendor Name: {vendor_name}
        
        Job Description:
        {job_description[:3000]}
        
        Candidate's Resume Context:
        {context_str}
        
        Instructions:
        1. Analyze the Job Description and Candidate's Context.
        2. Generate three things based on the following rules:
            a. **job_description_summary**: A concise summary of the job description (max 3 sentences).
            b. **job_requirements**: A list of STRICTLY technical skills, programming languages, databases, frameworks, and tools extracted from the JD (e.g., Python, SQL, PowerBI, AWS, React). Do NOT include soft skills, years of experience, or general duties.
            
            c. **email_body**: A cold email body to the vendor, which greet the vendor first (eg: Hi {vendor_name}, if his name is available following these rules:
                - act behalf of Harish Jamallamudi and send this email to the vendor,not like a chatbot or a third person.
                - STRICTLY limit the body to exactly 3 sentences.
                - If the JD matches AI/ML/Data Science, write a persuasive pitch highlighting relevant experience.
                - If the JD does NOT match well, politely request consideration for AI/ML/Data Science roles.
                - If the JD is Data Engineering, explain the profile as a Data Engineer.
                - ABSOLUTELY NO HTML TAGS or <br>. Use actual newlines (\n) for line breaks.
                - Separated each sentence with a new line (\n).
                - No subject line in the body.
                - No placeholders.
                - Sign off exactly as follows (preceded by 2 newlines):
                    Best regards,
                    Harish Jamallamudi
                    +13146696026
                    harishjamalladi@gmail.com
        """

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-flash-latest", 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=InitialEmailResponse
                        # tools=tools
                    )
                )
                
                # response.parsed should be an instance of InitialEmailResponse
                data = response.parsed
                
                if not data:
                    # Fallback if parsed isn't populated (rare with schema)
                    import json
                    json_data = json.loads(response.text)
                    email_body = json_data.get("email_body", "")
                else:
                    email_body = data.email_body
                # print(email_body)
                # Post-processing cleanup
                email_body = email_body.replace("<br>", "\n").replace("<br/>", "\n").replace("</br>", "\n")
                if "Best regards," in email_body:
                    # Ensure double newline before sign-off
                    parts = email_body.partition("Best regards,")
                    if not parts[0].endswith("\n"):
                         email_body = parts[0].strip() + "\n\n" + "Best regards," + parts[2]

                return (
                    email_body,
                    data.job_description_summary if data else json_data.get("job_description_summary", ""),
                    data.job_requirements if data else json_data.get("job_requirements", [])
                )

            except Exception as e:
                # print(f"Attempt {attempt + 1} failed: {e}")
                if "503" in str(e) or "429" in str(e): # Overloaded or Rate Limit
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2 # Exponential backoff
                        continue
                return f"Error: {e}", "", []
        
        return "Error: Max retries exceeded.", "", []


    def get_Ai_Subject(self, job_role):
        # print("Generating subject with gemini--latest...")
        prompt = f"""
        You are a professional assistant helping a candidate apply for a job.
        
        Job Role: {job_role}
        
        Task:
        Draft a four-words subject line for the job application. 
        - only 4 words,
        - Do not include placeholders like "[Your Name]". The candidate's name is Harish Jamallamudi.
        
        """
        try:    
            return self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            ).text
        except Exception as e:
            # print(f"Error generating subject with Gemini: {e}")
            pass


 




    def generate_tailored_resume_content(self, current_content:  list[str], job_description: str) -> list[str]:
        """
        Generates a tailored version of a resume section using Gemini AI, specifically for experience points.
        Returns a list of bullet points.
        """
        if not self.api_key:
            return current_content

        
        prompt = f"""
        You are an expert resume writer. Your task is to rewrite the specific job experience points for the client to align with a target Job Description, WHILE STRICTLY PRESERVING THE TRUTH.
        
        Target Job Description:
        {job_description}

        Current Experience Points (Context):
        {current_content}
        
        Instructions:
        - Analyze the "Current Experience Points" and "Target Job Description".
        - Rewrite the experience points to highlight relevance to the JD, but **DO NOT FABRICATE** experience.
        - **CRITICAL**: Do NOT replace the tools/technologies the user actually used with ones from the JD unless they are generic synonyms(means they similar tools but different providers). 
            - Example: If the user used "Faiss" and the JD asks for "Pinecone", change it to "Pinecone", because pinecone is a also vector database.
            - Example: If the user worked in "Telecom", do NOT change it to "Healthcare" just because the JD is for a Healthcare company.
        - **Keyword Integration**: Use keywords from the JD to *frame* the experience or as starting action verbs.
            - Example: If the JD asks for "Data Analysis" and the user "looked at call logs", rewrite it as "Performed Data Analysis on call logs...".
            --JD ask for communication skill, explain communication skills in projects
        - If a specific requirement from the JD is totally missing from the user's experience, try to find relation withexisting experience clearly, and mention it, if no relation found then skip that point.
        - The output must be a JSON list of strings, where each string is a bullet point.
        - Do not include markdown formatting like ```json ... ``` or bullet characters inside the strings. Just the raw text of the point.
        - Make the points punchy, impact-oriented, and keyword-rich where truthful.
        - Should not include "*" or "-" etc. only plain text.
        - Keep the same number of bullet points as the input.
        
        Example Output Format:
        ["Developed an ETL pipeline using Python...", "Optimized database queries decreasing load time by 30%...","second point"]
        """

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )
                
                # Clean up the response to ensure it parses as JSON
                text_response = response.text.strip()
                # Remove potential markdown code blocks
                if text_response.startswith("```"):
                    text_response = text_response.strip("`").replace("json", "").strip()
                
                import json
                try:
                    points = json.loads(text_response)
                    if isinstance(points, list):
                        return points
                    else:
                        # Fallback if AI returns something else, just split by newlines
                        return [line.strip("-•* ") for line in text_response.split('\n') if line.strip()]
                except json.JSONDecodeError:
                     # Fallback if not valid JSON
                    return [line.strip("-•* ") for line in text_response.split('\n') if line.strip()]

            except Exception as e:
                # print(f"Attempt {attempt + 1} failed: {e}")
                if "503" in str(e) or "429" in str(e): # Overloaded or Rate Limit
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2 # Exponential backoff
                        continue
                return current_content
        
        return current_content

    def tailor_technical_skills(self, current_skills: dict, job_requirements: list[str]) -> dict:
        """
        Merges job requirements into the current skills dictionary using Gemini AI.
        Returns the updated dictionary.
        """
        if not self.api_key:
            return current_skills

        prompt = f"""
        You are an expert technical resume writer. Your task is to intelligently merge a list of "Job Requirements" into an existing "Current Skills" dictionary.

        Current Skills Dictionary:
        {json.dumps(current_skills, indent=2)}

        Job Requirements (New Skills to Add):
        {json.dumps(job_requirements, indent=2)}

        Instructions:
        - Analyze the "Job Requirements".
        - Add each requirement to the most appropriate category (Key) in the "Current Skills" dictionary.
        - If a requirement doesn't fit into any existing category, create a new, logical category key (e.g., "Cloud Platforms", "Tools", "Libraries").
        - Ensure there are NO duplicates in the lists.
        - Maintain a clean, professional structure and keep previous skills don't remove them.
        - The output must be a valid JSON dictionary representing the updated skills.
        - Do not include markdown formatting like ```json ... ```. Just the raw JSON.

        Example Output Format:
        {{
          "Programming Languages": ["Python", "Java", "C++"],
          "Web Technologies": ["HTML", "CSS", "React"],
          ...
        }}
        """

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )
                
                text_response = response.text.strip()
                if text_response.startswith("```"):
                    text_response = text_response.strip("`").replace("json", "").strip()
                
                try:
                    updated_skills = json.loads(text_response)
                    if isinstance(updated_skills, dict):
                        return updated_skills
                    else:
                        return current_skills # Fallback
                except json.JSONDecodeError:
                    return current_skills # Fallback

            except Exception as e:
                # print(f"Skill Tailoring Attempt {attempt + 1} failed: {e}")
                if "503" in str(e) or "429" in str(e):
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                return current_skills # Return original on failure
        
        return current_skills

if __name__ == "__main__":
    obj=GeminiService()
    try:
        print("\n--- Testing Resume Tailoring (Experience) ---")
        current_xp = """
        - Developed a chatbot using Python and NLTK.
        - Worked on SQL databases to store chat logs.
        """
        jd = """
        Looking for a GenAI Engineer with experience in RAG, Vector Databases (FAISS/Chroma), and LLM orchestration (LangChain). 
        Must be proficient in Python and SQL. Experience with cloud deployment is a plus.
        """
        context = [{"text": "Built RAG pipelines using LangChain."}, {"text": "Deployed models on AWS."}]
        
        tailored_points = obj.generate_tailored_resume_content( current_xp, jd)
        print("Tailored Points Output:", tailored_points)
        print("Type of Output:", type(tailored_points))

        # print("\n--- Testing Skill Tailoring ---")
        # current_skills = {
        #     "Programming Languages": ["Python", "access"],
        #     "Databases": ["SQL Server"]
        # }
        # job_reqs = ["AWS", "Docker", "Kubernetes", "React", "PostgreSQL"]
        
        # tailoring_skills = obj.tailor_technical_skills(current_skills, job_reqs)
        # print("Tailored Skills Output:", json.dumps(tailoring_skills, indent=2))

        # print("\n--- Testing Initial Email Generation (Structured) ---")
        # vendor = "TechCorp"
        # role = "AI Engineer"
        # jd = "We need an AI Engineer with Python, RAG, and LangChain experience."
        # context = [{"text": "Experienced in building RAG pipelines."}]
        
        # body, summary, reqs = obj.generate_initial_email_body(vendor, role, jd, context)
        # print("Email Body:", body[:50] + "...")
        # print("Summary:", summary)
        # print("Requirements:", reqs)
        # print("Type of Return:", type((body, summary, reqs)))

    except Exception as e:
        print(f"Test failed: {e}")
