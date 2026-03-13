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

        if isinstance(relevant_context, dict):
            context_str = json.dumps(relevant_context, indent=2)
        else:
            context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])
        
        prompt = f"""
        You are a professional assistant helping a candidate apply for a job.
        
        Job Role: {job_role}
        
        Job Description:
        {job_description[:2000]}
        
        Candidate's Resume Context (Matched from Vector Store):
        {context_str}
        
        Draft a professional and persuasive cold email body to the hiring manager/recruiter following this EXACT structure:
        
        1. Opening sentence: "I am interested in the {job_role} role."
        2. Experience summary: "With over [Years] of experience in [Domain], I bring strong expertise in [List 5-7 key technical skills/tools from resume relevant to JD]."
        3. Visa/Availability: "I am on [Visa Status from resume/context] and available to join immediately."
        
        4. Key Highlights Section:
           "Key Highlights of my profile:"
           - [Highlight 1: Specific technical achievement or project]
           - [Highlight 2: Specific technical achievement or project]
           - [Highlight 3: Specific technical achievement or project]
           - [Highlight 4: Specific technical achievement or project]
           - [Highlight 5: Specific technical achievement or project]
        
        5. Closing: "I believe my [Specific Expertise] makes me a strong fit for this role."
        
        Instructions:
        - Analyze the resume context and job description to fill in the details.
        - If Visa status is not clearly found, use 'H1B' as a default if likely, or omit that specific sentence if unsure, but try to follow the structure.
        - Do not include the subject line in the output.
        - ABSOLUTELY NO HTML TAGS or <br>. Use actual newlines (\n) for line breaks.

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
        if isinstance(relevant_context, dict):
            context_str = json.dumps(relevant_context, indent=2)
        else:
            context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])

        # ΓöÇΓöÇ PHASE 1: Email body ΓÇö uses function calling tools ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        email_prompt = f"""
        You are a professional assistant writing a cold job application email on behalf of a candidate.

        Job Role: {job_role}
        Vendor/Recruiter Name: {vendor_name}

        Job Description:
        {job_description[:3000]}

        Candidate's Resume Context:
        {context_str}

        Instructions:
        1. Write a cold email body following this EXACT structure:
           - Greet the vendor (e.g. "Hi {vendor_name},").
           - Opening sentence: "I am interested in the {job_role} role."
           - Experience summary: "With over [Years] of experience in [Domain], I bring strong expertise in [List 5-7 key technical skills/tools from resume relevant to JD]."
           - Visa/Availability: "I am on [Visa Status from resume/context] and available to join immediately."
           
           - Key Highlights Section:
             "Key Highlights of my profile:"
             - [Highlight 1: Specific technical achievement or project]
             - [Highlight 2: Specific technical achievement or project]
             - [Highlight 3: Specific technical achievement or project]
             - [Highlight 4: Specific technical achievement or project]
             - [Highlight 5: Specific technical achievement or project]
             
           - Closing: "I believe my [Specific Expertise] makes me a strong fit for this role."

        2. Use your available tools to fill in any candidate information the JD requests.
           - Call tools dynamically based on what the JD asks for — do not hardcode assumptions.
           - Use resume context for fields like education/graduation details.
           - If a field cannot be filled by any tool or the resume context, omit it entirely (do not leave a blank line).
        
        3. No HTML tags, no subject line, no placeholders. Use \n for line breaks.

        4. Always end with a sign-off (preceded by 2 newlines):
           Best regards,
           [candidate name from tool]
           [phone from tool, if available]
           [email from tool]
           [linkedin from tool, if available]

        5. If the JD contains a structured candidate information form (a list of "Label: value" lines),
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

        # ΓöÇΓöÇ PHASE 2: JD summary + requirements ΓÇö uses JSON schema ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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






    def generate_greeting_email(self, resume_data: dict, user_context: UserContext = None) -> str:
        """
        Generates a 300-word core content block based on resume data for a greeting email.
        Does NOT include greeting or signature.
        """
        if not self.api_key:
            return "Error: Gemini API key not configured."

        if user_context is None:
            user_context = UserContext()

        # Load the user's data into tool context (not strictly needed here but good practice)
        Tools.set_user_context(
            name=user_context.name,
            email=user_context.email,
            phone=user_context.phone,
            linkedin_url=user_context.linkedin_url
        )

        prompt = f"""
        You are a professional assistant writing the core content for a greeting email on behalf of a candidate.

        Candidate Name: {user_context.name}
        Candidate Resume Data:
        {json.dumps(resume_data, indent=2)}

        Task:
        Write a 200-word professional and detailed summary of the candidate's skills, experience, and knowledge, specifically focusing on their expertise in:
        - AI/ML (Machine Learning)
        - Agentic AI (LLM agents, planning, tool-use)
        - Data Science
        
        Additionally, mention that I am open to and highly interested in C2C (Corp-to-Corp) or C2H (Contract-to-Hire) roles.

        Instructions:
        - Write in the first person ("I").
        - Focus on specific technical achievements and tools mentioned in the resume data.
        - Ensure the tone is confident and professional.
        - **IMPORTANT**: Return ONLY the core body of the message. 
        - **DO NOT** include any greetings (like "Dear...", "Hi...").
        - **DO NOT** include any sign-offs or signatures (like "Best regards...", "Sincerely...").
        - No HTML tags. Use direct newlines for formatting paragraphs.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            email_content = response.text or ""
            email_content = email_content.replace("<br>", "\n").replace("<br/>", "\n").replace("</br>", "\n")
            return email_content.strip()
        except Exception as e:
            return f"Error generating greeting content: {e}"






    def get_Ai_Subject(self, description, existing_summary):
        # print("Generating subject with gemini--latest...")
        prompt = f"""
        You are a professional assistant helping a candidate to update their Resume summary.
        
        Job Description: {description}
        Existing Resume Summary: {existing_summary}
        
        Task:
        1. Identify the target role from the Job Description. The target role MUST be either "AI Engineer" or "Data Scientist". Choose the closest match.
        2. If the "Existing Resume Summary" already starts with this target role or accurately reflects it, return the "Existing Resume Summary" exactly as it is.
        3. Otherwise, update the "Existing Resume Summary" by ONLY changing the starting role name to the target role (either "AI Engineer" or "Data Scientist"), Don't change the rest of the summary.
        4. Keep the rest of the summary, its length, and its realistic tone exactly the same. Do not add keywords from the Job Description.
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
        You are an expert resume writer. Your task is to rewrite specific job experience points for the client to align with a target Job Description, WHILE STRICTLY PRESERVING THE TRUTH.
        
        Target Job Description:
        {job_description}

        Current Experience Points (Context):
        {current_content}
        
        Instructions:
        1. **Capability Highlighting**: Analyze the "Current Experience Points" and "Target Job Description". Rewrite the experience points to highlight the candidate's capabilities in specific areas the client is looking for. Details should be punchy and impact-oriented.
        
        2. **Technical Skill Mapping**: Map technical skills and tools the user actually used to contextually relevant alternatives specified in the JD.
            - Example: If the candidate used "AWS (S3, Lambda, EC2)" and the JD asks for "Azure", frame the experience using Azure service names like "Azure (Blob Storage, Azure Functions, VM Instances)" as they are direct functional equivalents.
            - Example: Map "Faiss" to "Pinecone" if both are used for vector search in the context.
            - **CRITICAL**: Only map tools that are functional equivalents. Preserve the underlying technical logic.
        
        3. **Domain Preservation**: **STRICTLY** preserve the industry/domain of work.
            - **DO NOT** change the industry the user worked in (e.g., Telecom, Healthcare, Finance) to match the company's domain in the JD.
            - If the user worked in "Healthcare" and the JD is for "Pharmaceutical", keep it as "Healthcare".
        
        4. **Keyword Integration**: Use keywords from the JD to *frame* the experience or as starting action verbs, while adhering to the mapping rules above.
        
        5. **Handling Gaps**: If a specific requirement from the JD is missing from the user's experience, find a relation to existing experience if possible, otherwise skip that point.
        
        6. **Formatting**:
            - The output must be a JSON list of strings, where each string is a bullet point.
            - Do not include markdown formatting like ```json ... ``` or bullet characters inside the strings.
            - Keep the same number of bullet points as the input.
            - Do not include symbols like "*" or "-" at the start of strings.
        
        Example Output Format:
        ["Spearheaded the development of scalable data pipelines using Azure Functions...", "Optimized SQL queries in a Healthcare context..."]
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
                        return [line.strip("-ΓÇó* ") for line in text_response.split('\n') if line.strip()]
                except json.JSONDecodeError:
                     # Fallback if not valid JSON
                    return [line.strip("-ΓÇó* ") for line in text_response.split('\n') if line.strip()]

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
