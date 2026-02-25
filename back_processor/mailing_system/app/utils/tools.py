from datetime import date
import re


class UserContext:
    """
    Holds the current user's contact info so tool functions can return live DB data.
    Populated via Tools.set_user_context() before each Gemini call.
    """
    def __init__(self, name="", email="", phone="", linkedin_url=""):
        self.name = name
        self.email = email
        self.phone = phone
        self.linkedin_url = linkedin_url


# Module-level context — set before each Gemini call
_current_user_context = UserContext()


class Tools:

    @staticmethod
    def set_user_context(name: str = "", email: str = "", phone: str = "", linkedin_url: str = ""):
        """
        Populate the user context before calling any Gemini email generation method.
        This makes all contact-info tools return real DB values.
        """
        global _current_user_context
        _current_user_context = UserContext(name=name, email=email, phone=phone, linkedin_url=linkedin_url)

    # ── Contact Info Tools (called by Gemini during email generation) ──────────

    @staticmethod
    def get_candidate_name() -> str:
        """
        Get the candidate's full name.
        Call this when you need the candidate's name for the email body or sign-off.
        """
        return _current_user_context.name

    @staticmethod
    def get_candidate_email() -> str:
        """
        Get the candidate's job/contact email address.
        Call this to add the candidate's email to the email sign-off.
        """
        return _current_user_context.email

    @staticmethod
    def get_candidate_phone() -> str:
        """
        Get the candidate's phone number.
        Call this to add the candidate's phone number to the email sign-off.
        Returns an empty string if no phone number is set.
        """
        return _current_user_context.phone

    @staticmethod
    def get_candidate_linkedin(requested: bool) -> str:
        """
        Get the candidate's LinkedIn profile URL.
        Only call this tool if the job description specifically asks for a LinkedIn
        profile, mentions 'LinkedIn', or if including a profile URL would be appropriate.

        Args:
            requested: Set to True if the job description or context asks for LinkedIn.
        """
        if requested and _current_user_context.linkedin_url:
            return _current_user_context.linkedin_url
        return ""

    # ── Utility Tools ──────────────────────────────────────────────────────────

    @staticmethod
    def get_todays_date() -> str:
        """
        Get today's date in YYYY-MM-DD format.
        """
        return date.today().strftime("%Y-%m-%d")

    @staticmethod
    def calculate_experience(start_year: int) -> int:
        """
        Calculate years of experience from a start year to now.

        Args:
            start_year: The year the candidate started working (e.g., 2019).
        """
        return date.today().year - int(start_year)

    @staticmethod
    def get_current_location(required_location: str = "") -> str:
        """
        Get the candidate's current location.
        Use this when the job description requires a specific location or a local candidate.

        Args:
            required_location: The location mentioned in the JD (e.g., "Chicago", "New York").
                               Pass empty string if the job is remote or location is unspecified.
        """
        my_locations = [
            "St. Louis, MO",
            "Chicago, IL",
            "Dallas, TX",
            "San Francisco, CA",
            "New York, NY"
        ]

        if not required_location:
            return "St. Louis, MO"

        req_clean = required_location.lower().strip()

        for loc in my_locations:
            if req_clean in loc.lower() or loc.lower().split(",")[0] in req_clean:
                return loc

        state_map = {
            "mo": "St. Louis, MO",
            "il": "Chicago, IL",
            "tx": "Dallas, TX",
            "ca": "San Francisco, CA",
            "ny": "New York, NY"
        }

        match = re.search(
            r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b',
            req_clean.upper()
        )
        if match:
            state_code = match.group(1).lower()
            if state_code in state_map:
                return state_map[state_code]

        return "St. Louis, MO"
