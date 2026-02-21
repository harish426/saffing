
import os
import sys
from dotenv import load_dotenv

# Ensure app is in path
sys.path.append(os.getcwd())

from app.services.ai_services import GeminiService

def test_tailoring():
    service = GeminiService()
    
    # Scenario: User has Telecom experience, JD is Healthcare
    current_xp = [
        "Analyzed call detail records for a Telecom company using Python and SQL to identify churn.",
        "Created dashboards to monitor network latency."
    ]
    
    jd = """
    Looking for a Data Analyst in the Healthcare sector. 
    Must know R and Tableau. 
    Experience with patient data analysis is a plus.
    """
    
    print("\n--- Testing Tailoring Logic ---")
    print(f"Original Experience: {current_xp}")
    print(f"Target JD: {jd}")
    
    tailored = service.generate_tailored_resume_content(current_xp, jd)
    
    print("\n--- Tailored Output ---")
    for point in tailored:
        print(f"- {point}")
        
    # Basic Checks
    joined_output = " ".join(tailored).lower()
    
    if "python" not in joined_output:
        print("\n[WARNING] 'Python' missing! (Should be preserved)")
    if "sql" not in joined_output:
        print("\n[WARNING] 'SQL' missing! (Should be preserved)")
        
    if "r " in joined_output or " r " in joined_output: # simple check for R language
        print("\n[FAIL] Found 'R' - Possible Hallucination (User knows Python, not R)")
    else:
        print("\n[PASS] 'R' not found.")

    if "tableau" in joined_output:
        print("\n[FAIL] Found 'Tableau' - Possible Hallucination (User didn't claim Tableau)")
    else:
        print("\n[PASS] 'Tableau' not found.")
        
    if "healthcare" in joined_output and "telecom" not in joined_output:
        print("\n[FAIL] Replaced 'Telecom' with 'Healthcare'? Check context.")
    elif "healthcare" in joined_output:
        print("\n[INFO] 'Healthcare' mentioned. Check if it's just framing (e.g. 'Applying data skills to Healthcare...').")
    
    if "telecom" in joined_output:
        print("\n[PASS] 'Telecom' preserved.")
    else:
        print("\n[WARNING] 'Telecom' context lost.")

if __name__ == "__main__":
    test_tailoring()
