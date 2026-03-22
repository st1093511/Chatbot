# Smart Chatbot System

Ένα έξυπνο σύστημα συνομιλίας που χρησιμοποιεί RAG και Text-to-SQL για αναζήτηση και διαχείριση πληροφοριών.

## Δομή Project

```
project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── services/
│   │   ├── intent_router.py
│   │   ├── rag_pipeline.py
│   │   ├── text_to_sql.py
│   │   └── crud_handler.py
│   └── db/
│       └── (auto-generated)
└── frontend/
```

## Εγκατάσταση Backend

1. `cd backend`
2. `pip install -r requirements.txt`
3. Δημιουργήστε `.env` με `OPENAI_API_KEY=your_key`
4. `python main.py`

## Χρήση

Το backend τρέχει στο http://localhost:8000