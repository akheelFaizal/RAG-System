import os, hashlib
from typing import Tuple, List, Dict
from utils.github_loader import clone_or_use_local
from utils.file_utils import walk_files, read_text, DOC_EXTS, CODE_EXTS
from utils.chunkers import split_markdown, split_code_by_blocks, autodetect_language
from retriever import VectorStore

def _doc_id(path: str, idx: int) -> str:
    return hashlib.sha1(f"{path}:{idx}".encode()).hexdigest()[:16]

def ingest_repo(repo_or_path: str, collection: VectorStore, max_chars: int = 1200, overlap: int = 200) -> Tuple[int, List[str]]:
    root = clone_or_use_local(repo_or_path)
    files = walk_files(root)
    ids, texts, metas = [], [], []
    added_paths = []

    for f in files:
        text = read_text(f)
        if not text.strip():
            continue
        ext = os.path.splitext(f)[1].lower()
        rel = os.path.relpath(f, root)

        if ext in DOC_EXTS:
            chunks = split_markdown(text, max_chars=max_chars, overlap=overlap)
            ftype = "doc"
        elif ext in CODE_EXTS:
            chunks = split_code_by_blocks(text, lang=autodetect_language(f), max_chars=max_chars, overlap=overlap)
            ftype = "code"
        else:
            continue

        for i, ch in enumerate(chunks):
            ids.append(_doc_id(rel, i))
            texts.append(ch)
            metas.append({"path": rel, "type": ftype, "lang": autodetect_language(f)})

        if len(texts) >= 256:
            collection.add(ids=ids, texts=texts, metadatas=metas)
            ids, texts, metas = [], [], []
        added_paths.append(rel)

    if texts:
        collection.add(ids=ids, texts=texts, metadatas=metas)

    return collection.count(), added_paths
