from app.services.ai_services import GeminiService
from app.utils.tools import Tools
import os

if __name__ == "__main__":
    print("Initializing GeminiService...")
    service = GeminiService()
    if not service.api_key:
        print("API Key not found. Please set GEMINI_API_KEY in .env")
    else:
        print("--- Testing Tool Integration ---")
        
        # Test Case 1: LinkedIn Request
        print("\n[Test 1] LinkedIn Request")
        role = "Senior Python Developer"
        desc = """
        Looking for a Python developer.
        Please include your LinkedIn profile link in the application.
        """
        context = [{"text": "Qualified python developer."}]
        
        try:
            body = service.generate_email_body(role, desc, context)
            print("Generated Body:")
            print(body)
            if "linkedin.com" in body:
                print("[SUCCESS] LinkedIn link found in body.")
            else:
                print("[WARNING] LinkedIn link NOT found in body.")
        except Exception as e:
            print(f"[ERROR] {e}")

        # Test Case 2: Smart Location Logic (Direct Tool Test)
        print("\n[Test 2] Smart Location Logic (Direct Tool Test)")
        test_inputs = [
            ("New York", "New York, NY"),
            ("Chicago loop", "Chicago, IL"),
            ("Austin, Texas", "Dallas, TX"), # Should might fail or default to St. Louis if logic isn't perfect, let's see. 
                                            # Wait, I didn't add Austin to the list, only Dallas. 
                                            # Let's test if Dallas works for TX input.
            ("Dallas", "Dallas, TX"),
            ("San Fran", "San Francisco, CA"),
            ("Remote", "St. Louis, MO"), # Default
        ]
        
        for req, expected in test_inputs:
            res = Tools.get_current_location(req)
            print(f"Input: '{req}' -> Output: '{res}'")
            # Loose check for expected city
            if expected.split(",")[0] in res:
                 print(f"  [OK] Matches {expected}")
            else:
                 print(f"  [?] Mismatch? Expected {expected}")

        # Test Case 3: AI Integration for Location
        print("\n[Test 3] AI Integration for Location")
        desc_loc = """
        Looking for a Data Scientist in New York.
        Must be local to NY.
        """
        try:
            body = service.generate_email_body(role, desc_loc, context)
            print("Generated Body:")
            print(body)
            if "New York" in body:
                print("[SUCCESS] 'New York' location found in body.")
            else:
                print("[WARNING] 'New York' location NOT found in body.")
        except Exception as e:
            print(f"[ERROR] {e}")
