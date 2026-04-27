import spacy
import subprocess

def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

def extract_location(query: str):
    try:
        nlp = load_spacy_model()
        doc = nlp(query)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                return ent.text.strip()
        words = query.split()
        return words[-1] if words else None
    except Exception as e:
        print("Error extracting location:", str(e))
        return None