from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.intent_router import IntentRouter
from services.rag_pipeline import RAGPipeline
from services.text_to_sql import TextToSQL
from services.crud_handler import CRUDHandler

app = FastAPI(title="Smart Chatbot System")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
intent_router = IntentRouter()
rag_pipeline = RAGPipeline()
text_to_sql = TextToSQL()
crud_handler = CRUDHandler()

@app.post("/chat")
async def chat_endpoint(data: dict):
    message = data.get("message")
    intent = intent_router.route(message)
    
    if intent == "rag":
        response = rag_pipeline.process(message)
    elif intent == "sql":
        response = text_to_sql.process(message)
    else:
        response = crud_handler.process(message)
    
    return {"response": response}

@app.post("/upload")
async def upload_endpoint(data: dict):
    # Handle file upload
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)