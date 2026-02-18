import io
import pdfplumber
import docx

def extract_text_from_bytes(file_content: bytes, filename: str) -> str:
    """
    Extracts text from a file (PDF or DOCX) given its content in bytes.
    """
    file_ext = filename.split('.')[-1].lower()
    
    if file_ext == 'pdf':
        return _extract_from_pdf(file_content)
    elif file_ext in ['docx', 'doc']:
        return _extract_from_docx(file_content)
    else:
        return ""

def _extract_from_pdf(file_content: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    return text

def _extract_from_docx(file_content: bytes) -> str:
    text = ""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""
    return text
