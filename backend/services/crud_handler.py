from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from services.text_to_sql import get_schema, execute_crud

load_dotenv()

CRUD_PROMPT = ChatPromptTemplate.from_template("""
Είσαι ειδικός SQL για SQLite.

Schema:
{schema}

Ο χρήστης θέλει να κάνει αλλαγές στη βάση:
"{question}"

Γράψε ΜΟΝΟ το SQL (INSERT / UPDATE / DELETE).
Χωρίς markdown, χωρίς εξήγηση.
""")

def handle_crud(question: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    schema = get_schema()
    chain = CRUD_PROMPT | llm
    sql = chain.invoke({"schema": schema, "question": question}).content.strip()
    result = execute_crud(sql)
    return f"SQL εκτελέστηκε:\n```sql\n{sql}\n```\n\n{result}"