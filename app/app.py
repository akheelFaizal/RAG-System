import os, io, csv, time
import streamlit as st
from dotenv import load_dotenv
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

from retriever import VectorStore
from ingest import ingest_repo
from rag_pipeline import answer_question
from evaluators import precision_at_k

load_dotenv()
st.set_page_config(page_title="Code Docs RAG (OpenAI)", layout="wide")

st.title("📚 Code Documentation RAG (OpenAI)")
st.caption("Index GitHub repos → retrieve relevant snippets → generate answers with code examples.")

with st.sidebar:
    st.header("Settings")
    repo_input = st.text_input("GitHub repo URL or local path", placeholder="https://github.com/org/repo or /path/to/repo")
    collection_name = st.text_input("Collection name", value="code-docs-openai")
    chroma_dir = st.text_input("Chroma directory", value=os.getenv("CHROMA_DIR", ".chroma"))
    max_chars = st.slider("Chunk size (chars)", 400, 2400, 1200, 100)
    overlap = st.slider("Chunk overlap (chars)", 0, 400, 200, 10)
    top_k = st.slider("Top-k results", 1, 10, 5, 1)
    st.markdown("---")
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set. Fill it in your .env or environment.")

tabs = st.tabs(["Index", "Ask", "Evaluation"])

# ---- Index Tab ----
with tabs[0]:
    st.subheader("Index Repository")
    st.write("Provide a GitHub URL or a local path, then click **Index Repository**.")
    vstore = None
    if st.button("Index Repository", type="primary", use_container_width=True):
        with st.spinner("Indexing..."):
            try:
                vstore = VectorStore(collection_name=collection_name, persist_dir=chroma_dir)
                count_before = vstore.count()
                count_after, paths = ingest_repo(repo_input, vstore, max_chars=max_chars, overlap=overlap)
                st.success(f"Indexed {count_after - count_before} chunks. Total in collection: {count_after}.")
                with st.expander("Files processed"):
                    st.write("\n".join(sorted(set(paths))))
            except Exception as e:
                st.error(f"Indexing failed: {e}")

# ---- Ask Tab ----
with tabs[1]:
    st.subheader("Ask about the codebase")
    question = st.text_input("Your question", placeholder="e.g., How does authentication middleware work? Show example usage.")
    if st.button("Search & Answer", type="primary", use_container_width=True, disabled=not question):
        with st.spinner("Retrieving and generating..."):
            try:
                vstore = VectorStore(collection_name=collection_name, persist_dir=chroma_dir)
                answer, contexts = answer_question(vstore, question, k=top_k)
                st.markdown("### Answer")
                st.write(answer)

                st.markdown("### Retrieved Context")
                for c in contexts:
                    path = c['meta'].get('path', '')
                    lang = c['meta'].get('lang', '')
                    st.markdown(f"**{path}** \n*language:* `{lang}` • *score:* `{c['score']:.3f}`")
                    code = c['doc']
                    # Syntax highlight
                    try:
                        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
                    except Exception:
                        lexer = guess_lexer(code)
                    fmt = HtmlFormatter(nowrap=False, full=False)
                    st.markdown(f"<div style='background:#0e1117;border-radius:8px;padding:12px;overflow:auto'>{highlight(code, lexer, fmt)}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to answer: {e}")

# ---- Evaluation Tab ----
with tabs[2]:
    st.subheader("Evaluate retrieval (Precision@k)")
    st.write("Upload a CSV with columns: `question,relevant_keywords` where `relevant_keywords` is a `|`-separated list (matched against retrieved file paths).")
    up = st.file_uploader("CSV file", type=["csv"])
    if up is not None:
        content = up.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(content))
        queries = []
        for row in reader:
            kws = [s.strip() for s in (row.get("relevant_keywords","").split("|")) if s.strip()]
            queries.append({"question": row.get("question",""), "relevant_keywords": kws})

        vstore = VectorStore(collection_name=collection_name, persist_dir=chroma_dir)
        def _ret(q, k=5):
            return vstore.query(q, k=k)

        p_at_k, details = precision_at_k(queries, _ret, k=top_k)
        st.write(f"**Precision@{top_k}:** {p_at_k:.3f}")
        st.json(details)
