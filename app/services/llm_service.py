import google.generativeai as genai
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ═══════════════════════════════════════════
# Legal Prompts - DE/EN
# ═══════════════════════════════════════════
SYSTEM_PROMPTS = {
    "de": """Du bist LexAI, ein spezialisierter KI-Assistent für die Analyse 
rechtlicher Dokumente. Du hilfst Anwälten, Juristen und Unternehmen dabei, 
Verträge, Gesetze und rechtliche Dokumente zu verstehen.

Deine Grundsätze:
- Antworte NUR auf Basis der bereitgestellten Dokumente
- Verwende präzise juristische Terminologie
- Weise auf wichtige Klauseln, Fristen und Risiken hin
- Gib KEINE allgemeine Rechtsberatung außerhalb der Dokumente
- Empfehle bei Unklarheiten einen qualifizierten Rechtsanwalt
- Antworte in der Sprache des Benutzers (Deutsch oder Englisch)
- Strukturiere deine Antworten klar mit Überschriften wenn nötig""",

    "en": """You are LexAI, a specialized AI assistant for legal document analysis.
You help lawyers, legal professionals, and businesses understand contracts, 
laws, and legal documents.

Your principles:
- Answer ONLY based on the provided documents
- Use precise legal terminology
- Highlight important clauses, deadlines, and risks
- Do NOT provide general legal advice outside the documents
- Recommend a qualified lawyer when in doubt
- Answer in the user's language (German or English)
- Structure your answers clearly with headings when needed"""
}

def generate_legal_answer(
    query: str,
    context_chunks: list[dict],
    language: str = "de"
) -> dict:
    """توليد إجابة قانونية متخصصة"""

    if not context_chunks:
        no_context = {
            "de": "Ich konnte keine relevanten Informationen in Ihren Dokumenten finden. Bitte laden Sie die entsprechenden Rechtsdokumente hoch.",
            "en": "I could not find relevant information in your documents. Please upload the relevant legal documents."
        }
        return {
            "answer": no_context.get(language, no_context["en"]),
            "sources": []
        }

    # بناء السياق مع ترقيم المصادر
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {i} - {chunk['source']}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # بناء الـ Prompt
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

    user_prompt = f"""
{system_prompt}

LEGAL DOCUMENT CONTEXT:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Answer based strictly on the provided context
- Cite which document/source supports each point
- Highlight any risks, deadlines, or important clauses
- If the context is insufficient, clearly state what's missing
"""

    response = model.generate_content(user_prompt)
    sources  = list(set(c["source"] for c in context_chunks))

    return {
        "answer": response.text,
        "sources": sources
    }