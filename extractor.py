import fitz

def extract_text_from_pdf(pdf_bytes):
    text = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

# Test the function
if __name__ == "__main__":
    # Pointing to the dummy file you added to the folder
    resume_text = extract_text_from_pdf("dummy_resume.pdf")
    
    print("--- EXTRACTED RESUME TEXT ---")
    print(resume_text)