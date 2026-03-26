import os
import json
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from services.intent_router import route
from services.rag_pipeline import ingest_file, retrieve
from services.text_to_sql import get_schema, execute_select, ingest_csv
from services.crud_handler import handle_crud

load_dotenv()
app = FastAPI()
client = AsyncOpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Upload ────────────────────────────────────────────────
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs("./uploads", exist_ok=True)
    path = f"./uploads/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if file.filename.endswith(".csv"):
        table = file.filename.replace(".csv", "").replace("-", "_")
        rows = ingest_csv(path, table)
        return {"message": f"CSV φορτώθηκε ως table '{table}' ({rows} γραμμές)"}
    else:
        chunks = ingest_file(path)
        return {"message": f"Έγγραφο φορτώθηκε ({chunks} chunks)"}


# ── Chat ──────────────────────────────────────────────────
@app.post("/chat")
async def chat(question: str = Form(...)):
    intent = route(question)

    async def stream_response(system: str, user: str):
        yield f"data: {json.dumps({'type': 'intent', 'value': intent})}\n\n"

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            stream=True,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ]
        )
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'type': 'text', 'value': delta})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    # ── RAG ──
    if intent == "RAG":
        chunks = retrieve(question)
        context = "\n\n---\n\n".join(chunks)
        rag_system = (
            "Είσαι βοηθός που απαντά ερωτήσεις βάσει εγγράφων. "
            "Χρησιμοποίησε ΜΟΝΟ τις πληροφορίες από το παρακάτω context. "
            "Αν η απάντηση βρίσκεται στο context, δώσε την αναλυτικά με αναφορά στη σελίδα αν υπάρχει. "
            "Αν δεν βρίσκεις αρκετές πληροφορίες πες το ξεκάθαρα. "
            "Απάντα στην ίδια γλώσσα με την ερώτηση.\n\n"
            f"Context:\n{context}"
        )
        return StreamingResponse(
            stream_response(rag_system, question),
            media_type="text/event-stream"
        )

    # ── SQL ──
    if intent == "SQL":
        schema = get_schema()
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        sql_prompt = ChatPromptTemplate.from_template("""
Schema:
{schema}

Γράψε SQL για: {question}
Μόνο το SQL query, χωρίς markdown.
""")
        chain = sql_prompt | llm
        sql = chain.invoke({"schema": schema, "question": question}).content.strip()

        try:
            result = execute_select(sql)
            result_str = format_sql_result(result)
        except Exception as e:
            result_str = f"Σφάλμα εκτέλεσης SQL: {e}"

        async def stream_sql():
            yield f"data: {json.dumps({'type': 'intent', 'value': 'SQL'})}\n\n"
            yield f"data: {json.dumps({'type': 'sql', 'value': sql})}\n\n"

            sql_system = "Παρουσίασε τα παρακάτω αποτελέσματα βάσης δεδομένων ξεκάθαρα στον χρήστη."
            sql_user   = f"Ερώτηση: {question}\n\nΑποτέλεσμα:\n{result_str}"

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                stream=True,
                messages=[
                    {"role": "system", "content": sql_system},
                    {"role": "user",   "content": sql_user},
                ]
            )
            async for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield f"data: {json.dumps({'type': 'text', 'value': delta})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return StreamingResponse(stream_sql(), media_type="text/event-stream")

    # ── CRUD ──
    if intent == "CRUD":
        result = handle_crud(question)

        async def stream_crud():
            yield f"data: {json.dumps({'type': 'intent', 'value': 'CRUD'})}\n\n"
            yield f"data: {json.dumps({'type': 'text', 'value': result})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return StreamingResponse(stream_crud(), media_type="text/event-stream")

    # ── UNKNOWN ──
    async def stream_unknown():
        yield f"data: {json.dumps({'type': 'intent', 'value': 'UNKNOWN'})}\n\n"
        yield f"data: {json.dumps({'type': 'text', 'value': 'Δεν κατάλαβα την ερώτησή σου. Δοκίμασε να ρωτήσεις για τα δεδομένα σου.'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(stream_unknown(), media_type="text/event-stream")


# ── Helper ────────────────────────────────────────────────
def format_sql_result(result: dict) -> str:
    if not result["rows"]:
        return "Δεν βρέθηκαν αποτελέσματα."
    header = " | ".join(result["columns"])
    rows   = "\n".join(" | ".join(str(v) for v in row) for row in result["rows"])
    return f"{header}\n{rows}\n\nΣύνολο: {result['count']} γραμμές"