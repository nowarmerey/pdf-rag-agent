import google.generativeai as genai
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ═══════════════════════════════════════════════════════
# System Prompts - Legal AI (DE/EN)
# ═══════════════════════════════════════════════════════
SYSTEM_PROMPTS = {
    "de": """Du bist LexAI, ein hochspezialisierter KI-Assistent für Rechtsanalyse.
Du unterstützt Anwälte, Unternehmen und Privatpersonen bei der Analyse 
und dem Verständnis von Rechtsdokumenten jeder Art.

## Deine Kernkompetenzen:
- Vertragsrecht (Miet-, Arbeits-, Kaufverträge)
- Gesellschaftsrecht & Unternehmensrecht  
- Aufenthalts- & Migrationsrecht
- Zivilrecht & Prozessrecht
- Datenschutzrecht (DSGVO)
- Allgemeine Rechtsanalyse

## Deine Arbeitsweise:
1. Analysiere den bereitgestellten Dokumentenkontext GENAU
2. Identifiziere relevante Klauseln, Paragrafen und rechtliche Begriffe
3. Erkläre komplexe Rechtsbegriffe in verständlicher Sprache
4. Weise AKTIV auf Risiken, Fristen und wichtige Klauseln hin
5. Strukturiere Antworten mit klaren Überschriften
6. Zitiere immer die Quelle (Dokument + Abschnitt)

## Antwortformat:
- Beginne mit einer direkten Antwort auf die Frage
- Füge relevante Zitate aus dem Dokument hinzu
- Liste wichtige Punkte mit Bulletpoints auf
- Beende mit einer Zusammenfassung oder Empfehlung

## Wichtige Regeln:
- Antworte NUR auf Basis der bereitgestellten Dokumente
- Weise bei unklaren Punkten auf einen Rechtsanwalt hin
- Antworte in der Sprache des Benutzers (DE/EN)
- Sei präzise aber verständlich
- Verwende juristische Fachbegriffe mit Erklärungen""",

    "en": """You are LexAI, a highly specialized AI assistant for legal analysis.
You support lawyers, businesses, and individuals in analyzing 
and understanding legal documents of any kind.

## Your Core Competencies:
- Contract Law (rental, employment, commercial contracts)
- Corporate & Business Law
- Immigration & Residence Law
- Civil Law & Procedural Law
- Data Protection Law (GDPR)
- General Legal Analysis

## Your Working Method:
1. Analyze the provided document context PRECISELY
2. Identify relevant clauses, paragraphs, and legal terms
3. Explain complex legal concepts in understandable language
4. ACTIVELY highlight risks, deadlines, and important clauses
5. Structure answers with clear headings
6. Always cite the source (document + section)

## Response Format:
- Start with a direct answer to the question
- Add relevant quotes from the document
- List important points with bullet points
- End with a summary or recommendation

## Important Rules:
- Answer ONLY based on the provided documents
- Refer to a lawyer for unclear points
- Answer in the user's language (DE/EN)
- Be precise but understandable
- Use legal terminology with explanations"""
}

# ═══════════════════════════════════════════════════════
# Legal Categories for better context
# ═══════════════════════════════════════════════════════
LEGAL_KEYWORDS = {
    "contract": ["vertrag", "contract", "klausel", "clause", "kündigung", "termination"],
    "immigration": ["aufenthalt", "visum", "visa", "aufenthaltserlaubnis", "residence"],
    "corporate": ["gesellschaft", "gmbh", "ag", "corporation", "satzung", "articles"],
    "gdpr": ["dsgvo", "gdpr", "datenschutz", "data protection", "personendaten"],
    "civil": ["klage", "lawsuit", "schadensersatz", "damages", "haftung", "liability"]
}

def _detect_legal_category(query: str) -> str:
    """تحديد نوع القضية القانونية"""
    query_lower = query.lower()
    for category, keywords in LEGAL_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            return category
    return "general"

def generate_legal_answer(
    query: str,
    context_chunks: list[dict],
    language: str = "de"
) -> dict:
    """توليد إجابة قانونية متخصصة ومنظمة"""

    if not context_chunks:
        no_context = {
            "de": """## ⚠️ Keine relevanten Dokumente gefunden

Ich konnte keine relevanten Informationen in Ihren Dokumenten finden.

**Mögliche Lösungen:**
- Laden Sie die entsprechenden Rechtsdokumente hoch
- Stellen Sie sicher, dass die Dokumente lesbaren Text enthalten
- Formulieren Sie Ihre Frage präziser""",

            "en": """## ⚠️ No Relevant Documents Found

I could not find relevant information in your documents.

**Possible Solutions:**
- Upload the relevant legal documents
- Make sure the documents contain readable text
- Rephrase your question more precisely"""
        }
        return {
            "answer": no_context.get(language, no_context["en"]),
            "sources": [],
            "category": "none"
        }

    # تحديد نوع القضية
    category = _detect_legal_category(query)

    # بناء السياق مع ترقيم
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Quelle {i} / Source {i} — {chunk['source']}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # بناء الـ Prompt الكامل
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

    user_prompt = f"""{system_prompt}

════════════════════════════════════
DOKUMENTENKONTEXT / DOCUMENT CONTEXT
════════════════════════════════════
{context}

════════════════════════════════════
RECHTLICHE ANFRAGE / LEGAL QUERY
════════════════════════════════════
Kategorie / Category: {category}
Frage / Question: {query}

════════════════════════════════════
ANWEISUNGEN / INSTRUCTIONS
════════════════════════════════════
1. Beantworte die Frage basierend NUR auf dem obigen Kontext
2. Strukturiere deine Antwort mit Markdown (##, **, -, >)
3. Zitiere relevante Passagen aus den Dokumenten
4. Weise auf Risiken oder wichtige Fristen hin
5. Falls der Kontext unzureichend ist, erkläre was fehlt
"""

    response = model.generate_content(user_prompt)
    sources  = list(set(c["source"] for c in context_chunks))

    return {
        "answer":   response.text,
        "sources":  sources,
        "category": category
    }