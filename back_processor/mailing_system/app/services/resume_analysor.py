from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

load_dotenv()

# Pydantic Models for Resume Structure

class PersonalInfo(BaseModel):
    name: str = Field(description="Full Name")
    title: str = Field(description="Professional Title like 'Sr. Data Scientist'")
    email: str = Field(description="Email Address")
    phone: str = Field(description="Phone Number")
    linkedin: str = Field(description="LinkedIn Profile URL")

class ProfessionalSummary(BaseModel):
    overview: str = Field(description="A paragraph summarizing professional experience")
    key_highlights: List[str] = Field(description="List of key professional achievements or highlights")

class EducationItem(BaseModel):
    degree: str = Field(description="Degree Name, e.g., 'Masters in Computer Science'")
    institution: str = Field(description="University or Institution Name")
    location: str = Field(description="Location of the institution")

class TechnologyCategory(BaseModel):
    category: str = Field(description="Category name. MUST BE THE EXACT HEADER FROM THE RESUME (e.g. 'Languages', 'Python Libraries/Frameworks'). DO NOT CHANGE IT.")
    skills: List[str] = Field(description="List of skills in this category")

class ExperienceItem(BaseModel):
    client: str = Field(description="Company or Client Name")
    location: str = Field(description="Location of the job")
    role: str = Field(description="Job Title/Role")
    duration: str = Field(description="Duration of employment, e.g., 'Jan 2020 - Present'")
    responsibilities: List[str] = Field(description="List of responsibilities and achievements")
class certification(BaseModel):
    name: str = Field(description="Name of the certification")
    institution: str = Field(description="Institution that issued the certification")
class ProjectItem(BaseModel):
    name: str = Field(description="Name of the project")
    description: List[str] = Field(description="Description of the project")

class ResumeSchema(BaseModel):
    personal_info: PersonalInfo
    professional_summary: ProfessionalSummary
    education: EducationItem # Assuming single entry based on json, can be list if needed but matching resume.json structure
    technologies: List[TechnologyCategory] = Field(description="List of technology categories. STRICTLY use the EXACT headers from rule #6.")
    professional_experience: List[ExperienceItem]
    certifications: List[certification]
    projects: List[ProjectItem]



class ResumeAnalysor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def parse_resume_to_json(self, resume_text: str) -> dict:
        """
        Parses resume text into a structured JSON dictionary matching ResumeSchema.
        Strictly returns empty strings/lists for missing fields.
        """
        if not self.client:
            return {"error": "Gemini API key not configured"}

        prompt = f"""
        You are an expert resume parser. Your task is to extract structured information from the provided resume text.
        
        Resume Text:
        {resume_text}
        
        Instructions:
        1. Extract information strictly into the requested JSON schema.
        2. IF A FIELD IS MISSING in the text, return an empty string "" for string fields, or an empty list [] for list fields.
        3. DO NOT OMIT KEYS. All keys must be present.
        4. maintain the exact structure provided in the schema.
        5. For Lists, split items logically.
        6. **TECHNOLOGIES STRATEGY**: 
           - For Technologies there might be already existing category and skills in the resume text. Makue sure to use all already present categories and skills. 
           - If there are no categories and skills in the resume text, then create categories and skills based on the resume text.
           - 
       
        7. **EXPERIENCE & SUMMARY STRATEGY**:
            a. **EXTRACT VERBATIM**: First, extract ALL existing bullet points from the resume text for:
               - `professional_summary.key_highlights`
               - `professional_experience.responsibilities`
               **Do not summarize, shorten, or remove any original points, but you can rephrase them to make them more professional and impactful.**
            b. **COUNT & ENHANCE**:
                - For each section (Summary or Experience Role), if it has **FEWER THAN 5 points**:
                  - Generate *additional* high-impact, professional, and relevant bullet points to stick to the facts but improve the profile's density. 
                  - Add enough to reach approximately 8 points.
                - If a section has **8 OR MORE points**:
                  - Keep them and improve them professionally. Heavily prioritize preserving the original content.
            c. **QUALITY**: Any generated points must be credible, specific, and aligned with the role's title and context.
            d. **COMBINE**: The final lists MUST contain [All Original Points] + [Any New Generated Points].
            e. **PROJECTS & CERTIFICATIONS STRATEGY**:
                - For Projects and Certifications there might be already existing projects and certifications in the resume text. Makue sure to use all already present projects and certifications. 
                - If there are no projects and certifications in the resume text, just discard don't add any projects and certifications. keep all the points if exists.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ResumeSchema
                )
            )
            
            # Helper function to recursively ensure missing fields are empty strings/lists (Gemini might omit them if null)
            # However, response_schema usually forces strict structure.
            # parsed = response.parsed # This would be an object of ResumeSchema
            
            # To return dict:
            parsed_json = json.loads(response.text)
            
            # To return dict:
            parsed_json = json.loads(response.text)
            print("DEBUG: Raw Technologies from Gemini:", json.dumps(parsed_json.get("technologies"), indent=2))
            
            # Write debug to file
            with open("debug_raw_response.json", "w") as f:
                json.dump(parsed_json, f, indent=2)

            # Transform technologies list to dict for frontend compatibility
            if "technologies" in parsed_json and isinstance(parsed_json["technologies"], list):
                tech_dict = {}
                for item in parsed_json["technologies"]:
                    if "category" in item and "skills" in item:
                        tech_dict[item["category"]] = item["skills"]
                parsed_json["technologies"] = tech_dict
                
            return parsed_json

        except Exception as e:
            print(f"Error parsing resume with Gemini: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    from app.core.database import SessionLocal
    from app.models.models import Resume 
    from app.utils.resume_parser import extract_text_from_bytes
    import os

    # Test
    analyzer = ResumeAnalysor()
    
    db = SessionLocal()
    try:
        # Get latest resume (assuming createdAt is reliable, otherwise just first)
        latest_resume = db.query(Resume).order_by(Resume.createdAt.desc()).first()
        
        if latest_resume and latest_resume.content:
            print(f"Found resume: {latest_resume.filename} (ID: {latest_resume.id})")
            
            # Extract text
            text = extract_text_from_bytes(latest_resume.content, latest_resume.filename)
            
            if text:
                print("Successfully extracted text. Parsing with Gemini...")
                parsed_json = analyzer.parse_resume_to_json(text)
                
                # # Save to data/resume/resume.json
                # base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                # output_path = os.path.join(base_dir, "data", "resume", "resume.json")
                
                # # Ensure directory exists
                # os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # with open(output_path, "w", encoding="utf-8") as f:
                #     json.dump(parsed_json, f, indent=2)
                
                # print(f"Successfully saved parsed resume to: {output_path}")

                # Save back to Database
                latest_resume.resumeData = parsed_json
                db.commit()
                print("Successfully updated 'resumeData' in the database.")

            else:
                print("Failed to extract text from resume content.")
        else:
            print("No resume found in database.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

