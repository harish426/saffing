import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict, Any

load_dotenv()

class JDRules(BaseModel):
    required_skills: List[str]
    expected_tasks: List[str]
    key_role_attributes: List[str]

class GeminiServiceFresher:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def analyze_jd(self, jd: str) -> JDRules:
        """Analyzes JD to extract skills and tasks."""
        if not self.client:
            return JDRules(required_skills=[], expected_tasks=[], key_role_attributes=[])

        prompt = f"""
        Analyze the following Job Description (JD) and extract:
        1. required_skills: A list of specific technical skills, tools, and technologies.
        2. expected_tasks: Key responsibilities or tasks the candidate will perform.
        3. key_role_attributes: Important qualities or specific focus areas of the role (e.g., "high-availability", "real-time").

        JD:
        {jd}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=JDRules
                )
            )
            return response.parsed
        except Exception as e:
            print(f"Error analyzing JD: {e}")
            return JDRules(required_skills=[], expected_tasks=[], key_role_attributes=[])

    def tailor_experience(self, experience_list: List[Dict[str, Any]], jd_rules: JDRules, indices_to_tailor: List[int] = None) -> List[Dict[str, Any]]:
        """Tailors professional experience bullet points based on JD analysis. indices_to_tailor is 1-based."""
        if not self.client or not experience_list:
            return experience_list

        tailored_exp = []
        for i, job in enumerate(experience_list):
            current_idx = i + 1
            if indices_to_tailor is not None and current_idx not in indices_to_tailor:
                tailored_exp.append(job)
                continue

            current_resps = job.get("responsibilities", [])
            
            # Additional context for seniority/progression
            progression_instr = ""
            if current_idx == 1:
                progression_instr = "HIGHLIGHT that you learned and mastered key skills REQUIRED by the JD here. Show growth and application of advanced concepts."
            elif current_idx == 3:
                progression_instr = "FOCUS on foundational skills learned here. KEEP the complexity at a 'fresher' or 'junior' level. DO NOT over-engineer the achievements; keep them realistic for an entry-level role."

            prompt = f"""
            You are an ATS keyword specialist. Your ONLY job is to make MINIMAL, SURGICAL edits to the 
            candidate's existing bullet points so they match JD requirements — nothing more.

            === JD REQUIREMENTS ===
            Required Skills:   {json.dumps(jd_rules.required_skills)}
            Expected Tasks:    {json.dumps(jd_rules.expected_tasks)}
            Key Attributes:    {json.dumps(jd_rules.key_role_attributes)}

            === CANDIDATE'S EXISTING BULLETS (treat these as the source of truth) ===
            {json.dumps(current_resps)}

            Role Progression Note: {progression_instr}

            === STRICT EDITING RULES ===

            RULE 1 — EDIT OR REFRAME EVERY BULLET FOR JD FIT:
            For each bullet, decide which of the two paths applies:

            PATH A — GOOD FIT (bullet already relates to a JD requirement):
              Preserve the core action and context. Make surgical keyword swaps or light edits
              to align wording with JD terminology. Keep the same approximate length (±5 words).

            PATH B — POOR FIT (bullet has little or no connection to any JD requirement):
              Do NOT leave it unchanged. Instead, REFRAME it:
              • Keep the candidate's actual underlying activity as a factual anchor (do not fabricate).
              • Reorient the sentence so it emphasises the aspect of that activity most relevant to the JD.
              • You may restructure the sentence, change the opening verb, and shift emphasis —
                but every claim must still be grounded in what the candidate actually did.
              • Example: original "assisted with internal documentation" + JD focuses on data workflows
                → reframe as "structured internal documentation to support data reporting workflows".

            RULE 2 — WORD COUNT GUIDANCE:
            Target ±8 words of the input bullet's word count. Reframed bullets (Path B) may use
            the full range; edited bullets (Path A) should stay tighter (±5 words).

            RULE 3 — KEYWORD INJECTION:
            - Use exact JD terminology wherever possible — do not paraphrase skill names.
            - If Tool A (candidate) and Tool B (JD) are the same category, write "Tool B (via Tool A)".
            - Prioritise injecting skills that are missing from other bullets to maximise JD coverage.
            - Never force a keyword into a bullet where it makes no logical sense.

            RULE 4 — TOOL REMAPPING:
            If candidate used Tool A and JD asks for Tool B (same category), write "Tool B (via Tool A)".
            This is the only acceptable expansion — it adds ≤4 words.

            RULE 5 — SOFT SKILLS:
            If the original bullet already implies a soft skill (e.g., "coordinated with team"), keep that 
            language. Do not strip soft skill context when inserting technical keywords.
            Do NOT add soft skill sentences that weren't there — that increases word count.

            RULE 6 — NO FABRICATION:
            Do not add metrics, outcomes, or achievements that are not in the original bullet.

            RULE 7 — SAME BULLET COUNT:
            Output exactly the same number of bullets as input. No merging, no splitting.

            RULE 8 — HUMAN TONE:
            Avoid AI giveaway phrases: "leveraged", "spearheaded", "utilized", "synergized", "streamlined".
            Use plain action verbs the candidate already used.

            OUTPUT: A JSON array of strings — one string per bullet, in the same order as input.
            No markdown fences, no commentary, no explanation. Raw JSON only.
            """

            try:
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.strip("`").replace("json", "").strip()
                
                new_resps = json.loads(text)
                if isinstance(new_resps, list):
                    job["responsibilities"] = new_resps
            except Exception as e:
                print(f"Error tailoring experience for {job.get('client')}: {e}")
            
            tailored_exp.append(job)
        
        return tailored_exp

    def tailor_skills(self, current_skills: Dict[str, Any], jd_skills: List[str]) -> Dict[str, Any]:
        """Merges JD skills into the current skills dictionary."""
        if not self.client:
            return current_skills

        prompt = f"""
        Merge the following "JD Required Skills" into the "Current Skills" dictionary.
        
        Current Skills:
        {json.dumps(current_skills, indent=2)}
        
        JD Required Skills:
        {json.dumps(jd_skills, indent=2)}
        
        Instructions:
        - Analyze the "JD Required Skills".
        - **STRICTLY ONLY** add specific tools and software names (e.g., "Figma", "React", "PostgreSQL").
        - **DO NOT** add descriptions of work done, activities, or process-oriented skills like "Building applications", "Product design", "UI/UX design", "Rapid prototyping", or "Project management".
        - Place new tools/software into the most appropriate existing category and don't repeat the same skill in multiple categories.
        - Avoid duplicates.
        - Maintain previous skills; do not remove any existing data.
        - Output ONLY the updated JSON dictionary.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.strip("`").replace("json", "").strip()
            
            updated_skills = json.loads(text)
            return updated_skills if isinstance(updated_skills, dict) else current_skills
        except Exception as e:
            print(f"Error tailoring skills: {e}")
            return current_skills

    def generate_cover_letter(self, resume_data: Dict[str, Any], jd: str) -> str:
        """Generates a professional cover letter based on resume and JD."""
        if not self.client:
            return "AI service unavailable."

        name = resume_data.get("personal_info", {}).get("name", "Harish Jamallamudi")

        prompt = f"""
        You are an expert career coach. Write a professional, compelling cover letter for the candidate below.

        Candidate Name: {name}

        Full Resume (read ALL sections before writing):
        {json.dumps(resume_data, indent=2)}

        Job Description (JD):
        {jd}

        STEP 1 — RELEVANCE SCAN (do this silently before writing):
        - Read every entry in professional_experience, projects, and education.
        - Identify the 2-3 experiences or projects that best match what the JD is asking for.
        - Consider ALL entries equally — do NOT default to the most recent role just because it is first.

        STEP 2 — WRITE THE COVER LETTER using the relevant entries you found:
        1. Open with "Dear Hiring Manager,"
        2. First paragraph: Introduce yourself and state why you are excited about this specific role, connecting it to the most relevant experience or project you found.
        3. Second paragraph: Highlight 2-3 concrete examples from the resume (could be thesis, a project, or a past job) that directly address the JD's requirements. Use natural language describing WHAT you built/researched and HOW it relates. Do NOT invent or add any metrics, percentages, or numbers unless they are explicitly written in the resume data above.
        4. Third paragraph: Show understanding of the company's goals and how your skills will add real value.
        5. Close professionally: "Sincerely, {name}"

        RULES:
        - Do NOT include phone numbers, email addresses, or URLs in the letter body.
        - Do NOT fabricate any metric, percentage, or improvement figure not already in the resume.
        - Do NOT focus exclusively on the most recent job. Select the experiences and projects that best fit the JD.
        - Length: 3-4 paragraphs, concise and specific.
        - Tone: Confident, professional, enthusiastic but grounded in real experience.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return "Failed to generate cover letter."

    def answer_question(self, resume_data: Dict[str, Any], jd: str, question: str) -> str:
        """Answers interview-style questions using resume data and JD context."""
        if not self.client:
            return "AI service unavailable."

        prompt = f"""
        You are a career coach helping a candidate answer an interview question.

        Interview Question: "{question}"

        Full Resume (read ALL sections carefully):
        {json.dumps(resume_data, indent=2)}

        Job Description context:
        {jd}

        STEP 1 — RELEVANCE SCAN (do this silently, do NOT include it in the output):
        - Read every entry in professional_experience AND projects AND education.
        - Map the question's theme to the most relevant experience:
            * Questions about personal challenge, difficult problem, or perseverance  → look at thesis/research projects first.
            * Questions about teamwork or collaboration → look at group projects or internships.
            * Questions about technical skills or pipelines → pick the experience that actually used those skills.
            * Questions about why this company / motivation → draw on education goals and most relevant projects.
        - Choose the SINGLE most relevant story. Do NOT always default to the most recent job.

        STEP 2 — WRITE THE ANSWER using only the experience you selected:
        1. Briefly state WHAT the situation/project was (1-2 sentences, name it specifically).
        2. Explain the challenge or task you faced.
        3. Describe what YOU did to address it.
        4. State the outcome in natural language — describe what was achieved, learned, or delivered.
        5. Connect it briefly to what this role needs.

        RULES:
        - Maximum 150 words.
        - Do NOT invent or fabricate any percentage, metric, or improvement figure unless it appears verbatim in the resume data above.
        - Do NOT default to the most recent role if another experience is more relevant to the question.
        - Write in first person, professional and confident tone.
        - No bullet points — write in flowing prose.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Failed to answer question."

    def process_builder_request(self, resume_data: Dict[str, Any], jd: str, question: str) -> Dict[str, Any]:
        """Classifies and processes a builder request (Tailor, Cover Letter, or Q&A)."""
        if not self.client:
            return {"type": "error", "content": "AI service unavailable."}

        # Step 1: Classify the intent
        classify_prompt = f"""
        Classify the user intent based on the following question:
        "{question}"
        
        Possible classes:
        - "cover_letter": If the user asks for a cover letter or to write one.
        - "question": If the user asks an interview-style question like "why this company", "strengths", etc.
        - "tailor": If the user asks to change, update, or tailor the resume.
        
        Output ONLY the class name.
        """

        try:
            class_resp = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=classify_prompt
            )
            intent = class_resp.text.strip().lower()

            if "cover_letter" in intent:
                content = self.generate_cover_letter(resume_data, jd)
                return {"type": "text", "content": content, "intent": "cover_letter"}
            elif "question" in intent:
                content = self.answer_question(resume_data, jd, question)
                return {"type": "text", "content": content, "intent": "question"}
            else:
                # Default to tailoring
                tailored_data = self.generate_tailored_resume_data(resume_data, jd, exp_to_tailor=[1, 3])
                return {"type": "resume", "content": tailored_data, "intent": "tailor"}

        except Exception as e:
            print(f"Error processing builder request: {e}")
            return {"type": "error", "content": str(e)}

    def generate_tailored_resume_data(self, resume_data: Dict[str, Any], jd: str, exp_to_tailor: List[int] = None) -> Dict[str, Any]:
        """Main orchestrator for tailoring resume data. exp_to_tailor: list of 1-based indices."""
        # Detect nested "data" structure
        if "data" in resume_data:
            actual_data = resume_data["data"]
            is_nested = True
        else:
            actual_data = resume_data
            is_nested = False

        # 1. Analyze JD
        jd_rules = self.analyze_jd(jd)

        # 2. Tailor Skills
        if "technologies" in actual_data:
            actual_data["technologies"] = self.tailor_skills(actual_data["technologies"], jd_rules.required_skills)

        # 3. Tailor Experience
        if "professional_experience" in actual_data:
            actual_data["professional_experience"] = self.tailor_experience(actual_data["professional_experience"], jd_rules, indices_to_tailor=exp_to_tailor)

        # 4. Tailor Projects (Keeping current behavior or making it selective if needed)
        if "projects" in actual_data:
            actual_data["projects"] = self.tailor_experience(actual_data["projects"], jd_rules)

        if is_nested:
            resume_data["data"] = actual_data
            return resume_data
        return actual_data

if __name__ == "__main__":
    # Quick sanity check
    svc = GeminiServiceFresher()
    sample_jd = """
    Looking for a Python developer with experience in FastAPI and React. 
    Expertise in UI/UX design, building applications from scratch, and rapid prototyping is highly desired.
    Knowledge of PostgreSQL and Figma is required.
    """
    sample_resume = {
        "technologies": {
            "Programming": ["Python", "JavaScript"],
            "Databases": ["MongoDB"]
        },
        "professional_experience": [{"client": "Test Co", "responsibilities": ["Wrote code."]}]
    }
    # 1. Test Skill Tailoring
    print("\n--- Testing Skill Tailoring ---")
    result = svc.generate_tailored_resume_data(sample_resume, sample_jd)
    print("Updated Technologies:")
    print(json.dumps(result["technologies"], indent=2))

    # 2. Test Cover Letter
    print("\n--- Testing Cover Letter Generation ---")
    cl = svc.generate_cover_letter(sample_resume, sample_jd)
    print("Cover Letter Snippet:")
    print(cl[:500] + "...")
