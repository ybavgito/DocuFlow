import os
from pdfminer.high_level import extract_text
from docx import Document as DocxDocument
import google.generativeai as genai
from dotenv import load_dotenv
from keybert import KeyBERT

# Load environment variables
load_dotenv()


# Configure the Gemini model
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

kw_model = KeyBERT()

def extract_text_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found!")

    if file_path.endswith(".pdf"):
        return extract_text(file_path)  # Extract text from PDF
    elif file_path.endswith(".docx"):
        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])  # Extract text from Word file
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()  # Extract text from text files

def tag_document(text):
    # Use Gemini LLM to generate tags
    response = model.generate_content(text)
    
    # Extract keywords from the response
    if hasattr(response, 'keywords'):
        keywords = response.keywords
    else:
        # Fallback to using KeyBERT if Gemini model does not return keywords
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=11)
        keywords = [kw[0] for kw in keywords]
    
    return keywords
