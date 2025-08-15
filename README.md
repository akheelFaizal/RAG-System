# Code Documentation RAG with Syntax Understanding (OpenAI + Local Mode)

A Retrieval-Augmented Generation (RAG) system for software repositories that can now run **both with OpenAI** and **fully offline**.

---

## Features
- **Clones a GitHub repo** (or uses a local path).
- **Parses code & docs**, chunks them smartly.
- **Generates embeddings** using either:
  - **OpenAI** (`text-embedding-3-small`)
  - **Local SentenceTransformers** (`all-MiniLM-L6-v2`) — works without internet or API key.
- **Indexes embeddings** into a persistent **ChromaDB**.
- **Answers queries** using either:
  - **OpenAI GPT model** (`gpt-4o-mini`)
  - **Local HuggingFace model** (`distilgpt2`) — fully offline text generation.
- **Shows syntax-highlighted snippets** and file paths.

---

## Quickstart

### 1. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

## Running the App
```bash
streamlit run app/app.py
```

---

## Configuration Modes

### **OpenAI Online Mode**
```env
EMBEDDING_BACKEND=openai
OPENAI_API_KEY=sk-...   # Your API key here
CHROMA_DIR=.chroma
```
- Uses OpenAI embeddings + GPT-4o-mini for answering.

---

### **Local Offline Mode** (No API Key Needed)
```env
EMBEDDING_BACKEND=sentence-transformers
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DIR=.chroma
# Leave OPENAI_API_KEY blank
```
- Uses SentenceTransformers embeddings + local HuggingFace model (`distilgpt2`) for answering.

---

## What It Does
1. **Index**: Enter a GitHub URL or local path → chunks code/docs → writes embeddings to Chroma.
2. **Ask**: Type a question → retrieves top-k chunks → generates an answer using the selected backend.
3. **Evaluate (optional)**: Upload a CSV of `question,relevant_keyword` to compute Precision@k.

---

## Notes
- **Offline mode** is slower but avoids API usage and costs.
- **ChromaDB** persists data locally in `.chroma`, so you don’t need to re-index unless code changes.
- You can **switch between modes** by editing `.env` and restarting the app.

---