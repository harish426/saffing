import os
import sys
import json

# Add the directory to sys.path to import ai_services
sys.path.append(r'd:\freelancing\Staffing\development\back_processor\mailing_system')

from app.services.ai_services import GeminiService

def test_resume_tailoring():
    service = GeminiService()
    
    print("\n--- Testing generate_tailored_resume_content (Skill Mapping & Domain Preservation) ---")
    
    # Test case 1: AWS to Azure mapping in Healthcare domain
    current_content = [
        "Architected a serverless data processing pipeline using AWS Lambda and S3 in a Healthcare environment.",
        "Optimized DynamoDB queries to reduce latency for patient record retrieval.",
        "Implemented secure data ingestion from medical devices using AWS IoT Core."
    ]
    
    job_description = """
    Looking for a Cloud Engineer with expertise in Microsoft Azure. 
    Required skills: Azure Functions, Azure Blob Storage, Azure Cosmos DB.
    Experience in Pharmaceutical industry is a plus.
    """
    
    print("Input Content:")
    for point in current_content:
        print(f" - {point}")
    
    print("\nTarget JD (Condensed): Azure (Functions, Blob Storage, Cosmos DB), Pharma industry.")
    
    tailored_points = service.generate_tailored_resume_content(current_content, job_description)
    
    print("\nTailored Result:")
    if isinstance(tailored_points, list):
        for point in tailored_points:
            print(f" - {point}")
    else:
        print("Error: Output is not a list:", tailored_points)

    # Simple validation checks
    azure_keywords = ["Azure Functions", "Azure Blob Storage", "Cosmos DB", "Azure"]
    healthcare_found = any("Healthcare" in p for p in tailored_points)
    pharma_found = any("Pharmaceutical" in p for p in tailored_points)
    azure_found = any(any(kw in p for kw in azure_keywords) for p in tailored_points)
    
    print("\nValidation:")
    print(f" - Healthcare preserved: {healthcare_found}")
    print(f" - Pharmaceutical (wrongly) injected: {pharma_found}")
    print(f" - Azure services mapped: {azure_found}")

if __name__ == "__main__":
    test_resume_tailoring()
