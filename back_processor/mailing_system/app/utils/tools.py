from datetime import date
from datetime import datetime

class Tools:
    @staticmethod
    def get_todays_date():
        """
        Get today's date in YYYY-MM-DD format.
        """
        return date.today().strftime("%Y-%m-%d")

    @staticmethod
    def calculate_experience(start_year: int):
        """
        Calculate years of experience from a start year to now.
        
        Args:
            start_year: The year the candidate started working (e.g., 2015).
        """
        current_year = date.today().year
        return current_year - int(start_year)
    
    @staticmethod
    def get_company_info(company_name: str):
        """Placeholder for getting company info, maybe useful later"""
        return f"Information for {company_name} is not available yet."

    @staticmethod
    def get_linkedin_profile(requested: bool):
        """
        Get the candidate's LinkedIn profile URL.
        Use this tool if the job description specifically asks for a LinkedIn profile or URL.
        
        Args:
            requested: Boolean indicating if the LinkedIn profile was requested/mentioned in JD.
        """
        if requested:
            return "https://www.linkedin.com/in/harish-jamallamudi/" # Replace with actual if known, using placeholder based on name
        return ""

    @staticmethod
    def get_current_location(required_location: str = "St. Louis, MO"):
        """
        Get the candidate's current location from a list of available locations.
        Use this tool when the job description requires a specific location or asks for a local candidate.
        
        Args:
            required_location: The location requested in the job description (e.g., "Chicago", "New York"). 
                               If the job is remote or location isn't specified, this can be ignored/defaulted.
        """
        # List of available locations
        my_locations = [
            "St. Louis, MO",
            "Chicago, IL",
            "Dallas, TX",
            "San Francisco, CA",
            "New York, NY"
        ]
        
        if not required_location:
             return "St. Louis, MO"

        # Simple case-insensitive matching logic
        req_clean = required_location.lower().strip()
        
        # 1. Exact/Partial Match
        for loc in my_locations:
            if req_clean in loc.lower() or loc.lower().split(",")[0] in req_clean:
                return loc
                
        # 2. State Match (simplified)
        # Extract state abbreviation if possible (assumes "City, ST" format)
        # This is a basic heuristic.
        state_map = {
            "mo": "St. Louis, MO",
            "il": "Chicago, IL",
            "tx": "Dallas, TX",
            "ca": "San Francisco, CA",
            "ny": "New York, NY"
        }
        
        # Check if any state code is in the required location string
        import re
        # Look for 2-letter state codes
        match = re.search(r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b', req_clean.upper())
        if match:
             state_code = match.group(1).lower()
             if state_code in state_map:
                 return state_map[state_code]

        # Default fallback
        return "St. Louis, MO"
