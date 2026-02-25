from google import genai
from google.genai import types
import os
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from app.utils.tools import Tools, UserContext
from app.core.database import get_user_details



load_dotenv()

class InitialEmailResponse(BaseModel):
    job_description_summary: str
    job_requirements: List[str]
    email_body: str

class GeminiService:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            pass
        else:
            self.client = genai.Client(api_key=self.api_key)

    def generate_email_body(self, job_role: str, job_description: str, relevant_context: list[str], user_context: UserContext = None) -> str:
        """
        Generates a personalized email body using Gemini AI.
        """
        if not self.api_key:
            return "Error: Gemini API key not configured."

        if user_context is None:
            user_context = UserContext()

        # Load the user's data into the tool context so Gemini tool calls return real values
        Tools.set_user_context(
            name=user_context.name,
            email=user_context.email,
            phone=user_context.phone,
            linkedin_url=user_context.linkedin_url
        )

        context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])
        
        prompt = f"""
        You are a professional assistant helping a candidate apply for a job.
        
        Job Role: {job_role}
        
        Job Description:
        {job_description[:2000]}
        
        Candidate's Resume Context (Matched from Vector Store):
        {context_str}
        
        Task:
        Draft a concise, professional, and persuasive cold email body to the hiring manager/recruiter.
        - STRICTLY limit the body to exactly 3 sentences.
        - Analyze the resume context and job description to create a high-impact message.
        - Do not include the subject line in the output.
        - ABSOLUTELY NO HTML TAGS or <br>. Use actual newlines (\n) for line breaks.
        - Separate sentences with a single newline.

        For the sign-off (preceded by 2 newlines):
        - Call get_candidate_name() to get the candidate's name.
        - Call get_candidate_phone() to get the phone number (include if available).
        - Call get_candidate_email() to get the email address.
        - Call get_candidate_linkedin() with requested=True ONLY if the job description
          mentions LinkedIn or asks for a profile URL. Otherwise skip it.
        - Format exactly as:
            Best regards,
            [name from tool]
            [phone from tool, if any]
            [email from tool]
            [linkedin url from tool, if applicable]
        """

        tools = [
            Tools.get_todays_date,
            Tools.calculate_experience,
            # Tools.get_current_location,
            Tools.get_candidate_name,
            Tools.get_candidate_email,
            Tools.get_candidate_phone,
            Tools.get_candidate_linkedin,
        ]
        response = self.client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(tools=tools)
        )
        text_response = response.text
        if text_response:
            text_response = text_response.replace("<br>", "\n").replace("<br/>", "\n").replace("</br>", "\n")
        if text_response and "Best regards," in text_response and "\n\nBest regards," not in text_response:
            text_response = text_response.replace("Best regards,", "\n\nBest regards,")
        return text_response if text_response else ""


    def generate_initial_email_body(self, vendor_name: str, job_role: str, job_description: str, relevant_context: list[str], user_context: UserContext = None) -> tuple[str, str, list[str]]:
        """
        Generates an initial contact email body, JD summary, and requirements list using Gemini AI.
        Uses two separate Gemini calls:
          - Phase 1: tool-calling call to generate email_body (so LinkedIn/phone/name are fetched dynamically)
          - Phase 2: JSON-schema call to extract job_description_summary and job_requirements
        Returns: (email_body, job_description_summary, job_requirements)
        """
        if not self.api_key:
            return "Error: Gemini API key not configured.", "", []

        if user_context is None:
            user_context = UserContext()

        # Load the user's data into tool context so all get_candidate_* tools return real values
        Tools.set_user_context(
            name=user_context.name,
            email=user_context.email,
            phone=user_context.phone,
            linkedin_url=user_context.linkedin_url
        )

        context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])

        # ── PHASE 1: Email body — uses function calling tools ──────────────────
        email_prompt = f"""
        You are a professional assistant writing a cold job application email on behalf of a candidate.

        Job Role: {job_role}
        Vendor/Recruiter Name: {vendor_name}

        Job Description:
        {job_description[:3000]}

        Candidate's Resume Context:
        {context_str}

        Instructions:
        1. Write a 3-sentence cold email body:
           - Greet the vendor (e.g. "Hi {vendor_name},").
           - Write in first person as the candidate.
           - Match the pitch to the JD (AI/ML/Data Science focus if relevant, Data Engineering if applicable, otherwise request consideration).
           - No HTML tags, no subject line, no placeholders. Use \\n for line breaks.

        2. Use your available tools to fill in any candidate information the JD requests.
           - Call tools dynamically based on what the JD asks for — do not hardcode assumptions.
           - Use resume context for fields like education/graduation details.
           - If a field cannot be filled by any tool or the resume context, omit it entirely (do not leave a blank line).

        3. Always end with a sign-off (preceded by 2 newlines):
           Best regards,
           [candidate name from tool]
           [phone from tool, if available]
           [email from tool]
           [linkedin from tool, if available]

        4. If the JD contains a structured candidate information form (a list of "Label: value" lines),
           fill it using your tools and resume context, then append it after the sign-off.
           Only include lines you can fill — skip lines you cannot.
        """

        contact_tools = [
            Tools.get_todays_date,
            Tools.calculate_experience,
            # Tools.get_current_location,
            Tools.get_candidate_name,
            Tools.get_candidate_email,
            Tools.get_candidate_phone,
            Tools.get_candidate_linkedin,
        ]

        email_body = ""
        try:
            email_response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=email_prompt,
                config=types.GenerateContentConfig(tools=contact_tools)
            )
            email_body = email_response.text or ""
            email_body = email_body.replace("<br>", "\n").replace("<br/>", "\n").replace("</br>", "\n")
            if "Best regards," in email_body and "\n\nBest regards," not in email_body:
                email_body = email_body.replace("Best regards,", "\n\nBest regards,")
        except Exception as e:
            email_body = f"Error generating email: {e}"

        # ── PHASE 2: JD summary + requirements — uses JSON schema ──────────────
        analysis_prompt = f"""
        Analyze the following job description and extract structured information.

        Job Role: {job_role}

        Job Description:
        {job_description[:3000]}

        Extract:
        1. job_description_summary: A concise summary of the role and responsibilities (max 3 sentences).
        2. job_requirements: A list of STRICTLY technical skills, programming languages, databases,
           frameworks, and tools mentioned in the JD.
           Do NOT include soft skills, years of experience, or generic duties.
        """

        max_retries = 3
        retry_delay = 2
        jd_summary = ""
        requirements = []

        for attempt in range(max_retries):
            try:
                analysis_response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=analysis_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=InitialEmailResponse
                    )
                )
                data = analysis_response.parsed
                if not data:
                    json_data = json.loads(analysis_response.text)
                    jd_summary = json_data.get("job_description_summary", "")
                    requirements = json_data.get("job_requirements", [])
                else:
                    jd_summary = data.job_description_summary
                    requirements = data.job_requirements
                break

            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                jd_summary = ""
                requirements = []
                break

        return email_body, jd_summary, requirements




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
