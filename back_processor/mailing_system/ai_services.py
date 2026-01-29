from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
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
        - Highlight the candidate's experience relevant to the job description based on the resume context provided.
        - Keep it under 100 words.
        - Do not include the subject line in the output.
        - Do not include placeholders like "[Your Name]". The candidate's name is Harish Jamallamudi.
        - Sign off as:
        
        Best regards,
        Harish Jamallamudi
        """

        # try:
        response = self.client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt
        )
        return response.text
        # except Exception as e:
        #     print(f"Error generating content with Gemini: {e}")
        #     raise e # Re-raise for main.py to handle


    def generate_initial_email_body(self, vendor_name: str, job_role: str, job_description: str, relevant_context: list[str]) -> str:
        """
        Generates an initial contact email body using Gemini AI, with specific pivoting logic.
        """
        if not self.api_key:
            return "Error: Gemini API key not configured."

        context_str = "\n".join([c.get('text', '') if isinstance(c, dict) else str(c) for c in relevant_context])
        
        prompt = f"""
        You are a professional assistant helping a candidate apply for a job.
        
        Job Role: {job_role}
        Vendor Name: {vendor_name}
        
        Job Description:
        {job_description[:2000]}
        
        Candidate's Resume Context:
        {context_str}
        
        Instructions:
        Write a cold email body to the vendor ({vendor_name}).
        - I am good at AI/ML Engineering roles and Data Science roles.
        - If the job description matches my skills (AI/ML/Data Science), write a persuasive pitch highlighting my relevant experience from the resume context.
        - If the job description does NOT match well, politley request if they can consider me for any AI/ML Engineering or Data Science positions they might have.
        - if the job description is about data engineering, explain my profile as a data engineer.
        - Keep it under 300 words.
        - Do not include the subject line and "-" kind of lines in the body.
        - Do not use placeholders.
        - Sign off as:
        - Don't add anything like at vendor name.
        - if it is mail body, write it as a reply mail
        
        Best regards,
        Harish Jamallamudi
        +13146696026
        harishjamalladi@gmail.com
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating initial email with Gemini: {e}")
            return f"Error generating email: {e}"


    def get_Ai_Subject(self, job_role):
        print("Generating subject with gemini--latest...")
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
            print(f"Error generating subject with Gemini: {e}")
            return "Error generating subject."

if __name__ == "__main__":
    obj=GeminiService()
    try:
        print("Testing generation with gemini--latest...")
        data=obj.generate_email_body("AI Engineer","should now about RAG models",["Need to know about RAG models"])
        subject=obj.get_Ai_Subject("AI Engineer")
        print("Subject:", subject)
        print("Success:", data)
    except Exception as e:
        print(f"Test failed: {e}")
