import re

def anonymize_text(text):
    text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NOME]', text)
    text = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF]', text)
    text = re.sub(r'\d{2}/\d{2}/\d{4}', '[DATA]', text)
    return text

def clean_text(text):
    text = text.strip()
    text = text.replace("\n", " ")
    return text

def preprocess(text):
    text = anonymize_text(text)
    text = clean_text(text)
    return text