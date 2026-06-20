def validate_missing_keywords(resume_text, ai_missing_keywords):
    """
    Fact-checks the AI. Searches the raw resume text to ensure the 
    'missing' keywords are actually missing.
    """
    # Convert text to lowercase for case-insensitive matching
    text_lower = resume_text.lower()
    
    truly_missing = []
    false_alarms = []
    
    for keyword in ai_missing_keywords:
        # If the keyword IS actually in the text, it's a hallucination
        if keyword.lower() in text_lower:
            false_alarms.append(keyword)
        else:
            truly_missing.append(keyword)
            
    return {
        "truly_missing": truly_missing,
        "false_alarms": false_alarms
    }