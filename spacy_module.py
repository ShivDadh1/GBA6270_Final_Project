# spaCy module for classifying WebEx messages into ticket categories
import spacy
from typing import Dict, List

# Load the small English model. Ensure this is installed (see README).
nlp = None

def _ensure_model():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    return nlp

def classify_message(text: str) -> str:
    """
    Returns a simple category for the given text. This is rule-augmented and uses spaCy for tokens.
    Categories: VPN, Network, Email, Server, Application, Security, General
    """
    text_lower = text.lower()
    # Simple keyword rules (you can expand these)
    if "vpn" in text_lower:
        return "VPN"
    if "wifi" in text_lower or "wifi" in text_lower or "wireless" in text_lower or "ssid" in text_lower:
        return "Network"
    if "email" in text_lower or "outlook" in text_lower or "@domain" in text_lower:
        return "Email"
    if "server" in text_lower or "503" in text_lower or "502" in text_lower:
        return "Server"
    if "password" in text_lower or "login" in text_lower or "credential" in text_lower:
        return "Security"
    if "app" in text_lower or "application" in text_lower or "crash" in text_lower:
        return "Application"
    # Use spaCy to detect PRODUCT/ORG etc for hints
    doc = _ensure_model()(text)
    if any(ent.label_ in ("ORG", "PRODUCT") for ent in doc.ents):
        return "Application"
    return "General"

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Return a dict of entity types to list of entity strings; lightweight helper.
    """
    doc = _ensure_model()(text)
    entities = {}
    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)
    return entities
