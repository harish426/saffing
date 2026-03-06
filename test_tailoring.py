import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.ai_services import GeminiService

def test_tailoring():
    service = GeminiService()
    
    current_xp = [
        "Architected and implemented a RAG-based document retrieval system for charter flight operations using LangChain and Faiss.",
        "Optimized database queries in SQL Server to improve search performance by 40%."
    ]
    
    jd = """
    We are looking for a GenAI Engineer to build AI agents using crewAI. 
    Experience with vector databases like ChromaDB and LLM orchestration tools is required.
    Domain: Healthcare.
    """
    
    print("Testing Resume Tailoring...")
    tailored_points = service.generate_tailored_resume_content(current_xp, jd)
    
    print("\nOriginal XP:")
    for p in current_xp:
        print(f"- {p}")
        
    print("\nTailored XP:")
    for p in tailored_points:
        print(f"- {p}")

    # Check for crewAI swap
    has_crewai = any("crewAI" in p for p in tailored_points)
    # Check for domain preservation
    has_charter = any("charter" in p.lower() for p in tailored_points)
    has_healthcare = any("healthcare" in p.lower() for p in tailored_points)
    
    print(f"\nResults:")
    print(f"Tool swapped (LangChain -> crewAI): {has_crewai}")
    print(f"Domain preserved (kept 'charter'): {has_charter}")
    print(f"Domain not changed to 'healthcare': {not has_healthcare}")

if __name__ == "__main__":
    test_tailoring()
