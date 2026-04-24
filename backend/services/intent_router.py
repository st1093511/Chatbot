from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

ROUTER_PROMPT = ChatPromptTemplate.from_template("""
Κατηγοριοποίησε την ερώτηση σε ΑΚΡΙΒΩΣ μία κατηγορία:

- RAG       → ερώτηση σε ανεπεξέργαστο κείμενο / έγγραφα / PDF
- SQL       → ερώτηση που χρειάζεται αριθμητική, φίλτρα, ή aggregation σε δομημένα δεδομένα
- CRUD      → εισαγωγή, τροποποίηση ή διαγραφή δεδομένων
- UNKNOWN   → τίποτα από τα παραπάνω

Ερώτηση: "{question}"

Απάντησε με μία λέξη ΜΟΝΟ: RAG, SQL, CRUD, ή UNKNOWN
""")

def route(question: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    chain = ROUTER_PROMPT | llm
    intent = chain.invoke({"question": question}).content.strip().upper()
    if intent not in ("RAG", "SQL", "CRUD", "UNKNOWN"):
        return "UNKNOWN"
    return intent