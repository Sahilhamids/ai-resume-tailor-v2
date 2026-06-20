# pyrefly: ignore [missing-import]
import fitz  # This is the import name for the PyMuPDF library

def extract_text_from_pdf(pdf_bytes):
    """
    Extracts text from PDF bytes using PyMuPDF (fitz).
    This is compatible with FastAPI's file upload process.
    """
    text = ""
    try:
        # Open the PDF directly from the byte stream
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            # Iterate through each page and extract text
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
# Updated Test block for extractor.py
# Updated Test block for extractor.py
if __name__ == "__main__":
    # Open the file in binary mode to get the bytes
    with open("dummy_resume.pdf", "rb") as f:
        pdf_bytes = f.read()
    
    # Now pass the bytes to the function
    resume_text = extract_text_from_pdf(pdf_bytes)
    
    print("--- EXTRACTED RESUME TEXT ---")
    print(resume_text)