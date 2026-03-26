import os
import re
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

load_dotenv()

CHROMA_PATH = "./db/chroma_db"

def _get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")

# ── Καθαρισμός κειμένου ──────────────────────────────────
def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'-\n(\w)', r'\1', text)   # ένωσε σπασμένες λέξεις
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # αφαίρεσε μόνους αριθμούς σελίδας
    return text.strip()

# ── Έλεγχος αν PDF είναι scanned ─────────────────────────
def is_scanned_pdf(file_path: str) -> bool:
    try:
        import fitz  # pymupdf
        doc = fitz.open(file_path)
        text_total = ""
        for i, page in enumerate(doc):
            if i >= 3:  # έλεγξε μόνο τις 3 πρώτες σελίδες
                break
            text_total += page.get_text()
        doc.close()
        # Αν υπάρχουν λιγότεροι από 100 χαρακτήρες → πιθανώς scanned
        return len(text_total.strip()) < 100
    except:
        return False

# ── OCR για scanned PDFs ─────────────────────────────────
def load_scanned_pdf(file_path: str) -> list[Document]:
    try:
        import pytesseract
        from pdf2image import convert_from_path
        from PIL import Image

        # Ορισμός path για Windows
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        print(f"OCR processing: {file_path}")
        pages = convert_from_path(file_path, dpi=300)
        docs = []

        for i, page_img in enumerate(pages):
            # OCR με Ελληνικά + Αγγλικά
            text = pytesseract.image_to_string(
                page_img,
                lang="ell+eng",
                config="--psm 6"
            )
            text = clean_text(text)
            if len(text.strip()) > 30:
                docs.append(Document(
                    page_content=text,
                    metadata={"source": file_path, "page": i}
                ))

        print(f"OCR completed: {len(docs)} pages extracted")
        return docs

    except Exception as e:
        print(f"OCR error: {e}")
        return []

# ── Φόρτωση κανονικού PDF ────────────────────────────────
def load_normal_pdf(file_path: str) -> list[Document]:
    try:
        import fitz
        doc = fitz.open(file_path)
        docs = []

        for i, page in enumerate(doc):
            # Εξαγωγή με διατήρηση layout
            text = page.get_text("text")
            text = clean_text(text)
            if len(text.strip()) > 30:
                docs.append(Document(
                    page_content=f"[Σελίδα {i+1}]\n{text}",
                    metadata={"source": file_path, "page": i}
                ))

        doc.close()
        return docs

    except Exception as e:
        print(f"PyMuPDF error: {e}, falling back to PyPDF")
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        for d in docs:
            d.page_content = clean_text(d.page_content)
        return docs

# ── Ingest ───────────────────────────────────────────────
def ingest_file(file_path: str) -> int:
    if file_path.endswith(".pdf"):
        if is_scanned_pdf(file_path):
            print("Detected scanned PDF — using OCR")
            docs = load_scanned_pdf(file_path)
        else:
            print("Detected normal PDF — using PyMuPDF")
            docs = load_normal_pdf(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()

    if not docs:
        raise ValueError("Δεν ήταν δυνατή η εξαγωγή κειμένου από το αρχείο.")

    # Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", "! ", "? ", " "]
    )
    chunks = splitter.split_documents(docs)

    # Φίλτραρε πολύ μικρά chunks
    chunks = [c for c in chunks if len(c.page_content.strip()) > 30]

    if not chunks:
        raise ValueError("Δεν βρέθηκε χρήσιμο κείμενο στο αρχείο.")

    Chroma.from_documents(
        documents=chunks,
        embedding=_get_embeddings(),
        persist_directory=CHROMA_PATH,
        collection_name="documents"
    )

    print(f"Indexed {len(chunks)} chunks")
    return len(chunks)

# ── Retrieval ────────────────────────────────────────────
def retrieve(question: str, k: int = 6) -> list[str]:
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=_get_embeddings(),
        collection_name="documents"
    )

    docs = vectorstore.max_marginal_relevance_search(
        question,
        k=k,
        fetch_k=20,
        lambda_mult=0.7
    )
    return [doc.page_content for doc in docs]

# ── Delete ───────────────────────────────────────────────
def delete_collection():
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=_get_embeddings(),
        collection_name="documents"
    )
    vectorstore.delete_collection()