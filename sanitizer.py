import re

def sanitize_text(text):
    """
    Scans the extracted text and redacts sensitive PII using Regex.
    """
    # 1. Redact Emails
    # Looks for standard email formats (e.g., name@domain.com)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, '[EMAIL REDACTED]', text)
    
    # 2. Redact Phone Numbers
    # Looks for standard 10-digit formats: 123-456-7890, (123) 456 7890, etc.
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, '[PHONE REDACTED]', text)
    
    # 3. Redact LinkedIn/GitHub URLs (Optional but good for complete anonymity)
    url_pattern = r'(https?://[^\s]+)'
    text = re.sub(url_pattern, 'https://www.merriam-webster.com/dictionary/redacted', text)
    
    return text