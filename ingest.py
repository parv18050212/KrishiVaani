import os
import json
import re
import time
from typing import Dict, Any, List
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai
from PyPDF2 import PdfReader

# -----------------------
# Load environment
# -----------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "rag_documents")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# -----------------------
# Clients
# -----------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# -----------------------
# Helper Functions
# -----------------------

def clean_text(text: str) -> str:
    """Remove null characters and normalize whitespace."""
    return re.sub(r'\x00', '', text).strip()

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = clean_text(text).replace("\n", " ")
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def embed_texts(texts: List[str], retries: int = 3, delay: int = 5) -> List[List[float]]:
    vectors = []
    for t in texts:
        attempt = 0
        while attempt < retries:
            try:
                r = genai.embed_content(model=GEMINI_EMBEDDING_MODEL, content=t)
                vectors.append(r["embedding"])
                break
            except Exception as e:
                attempt += 1
                print(f"⚠ Error embedding text (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(delay * attempt)
                else:
                    raise
    return vectors

def insert_documents(chunks: List[str], vectors: List[List[float]], metadata: Dict[str, Any]):
    rows = []
    for c, v in zip(chunks, vectors):
        clean_chunk = clean_text(c)
        clean_metadata = {k: clean_text(str(v)) for k, v in metadata.items()}
        rows.append({
            "document_text": clean_chunk,
            "embedding": v,
            "metadata": clean_metadata
        })
    try:
        res = supabase.table(SUPABASE_TABLE).insert(rows).execute()
        if hasattr(res, 'error') and res.error:
            raise Exception(f"Supabase insert error: {res.error.message}")
        print(f"✅ Inserted {len(rows)} chunks into Supabase.")
    except Exception as e:
        print(f"❌ Supabase insert failed: {e}")
        raise

def ingest_pdf(file_path: str, metadata: Dict[str, Any]):
    print(f"📄 Reading PDF: {file_path}")
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        all_text = []
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            if txt.strip():
                all_text.append(txt.strip())

    if not all_text:
        print(f"⚠ No text found in {file_path}")
        return

    combined = "\n\n".join(all_text)
    chunks = chunk_text(combined)
    print(f"🔍 {len(chunks)} chunks created from {file_path}")

    vectors = embed_texts(chunks)
    insert_documents(chunks, vectors, metadata)

# -----------------------
# Bulk ingestion from 'content' folder
# -----------------------
if __name__ == "__main__":
    content_folder = "content"
    if not os.path.exists(content_folder):
        print(f"❌ Folder '{content_folder}' does not exist. Please create it and add PDFs.")
        exit(1)

    # Default metadata for bulk ingestion
    default_metadata = {"source": "bulk_ingest"}

    pdf_files = [f for f in os.listdir(content_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("❌ No PDF files found in 'content/' folder.")
        exit(1)

    print(f"🔍 Found {len(pdf_files)} PDF files. Starting ingestion...")

    for pdf in pdf_files:
        pdf_path = os.path.join(content_folder, pdf)
        try:
            ingest_pdf(pdf_path, default_metadata)
        except Exception as e:
            print(f"❌ Failed to process {pdf}: {e}")

    print("✅ Bulk ingestion completed.")
