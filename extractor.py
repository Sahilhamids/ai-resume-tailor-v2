# pyrefly: ignore [missing-import]
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Loop through all the pages and extract text
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()
                
        return text
        
    except FileNotFoundError:
        return "Error: The file was not found. Please make sure 'dummy_resume.pdf' is in the same folder."
    except Exception as e:
        return f"An error occurred: {e}"

# Test the function
if __name__ == "__main__":
    # Pointing to the dummy file you added to the folder
    resume_text = extract_text_from_pdf("dummy_resume.pdf")
    
    print("--- EXTRACTED RESUME TEXT ---")
    print(resume_text)