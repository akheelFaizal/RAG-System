import re
from typing import List

def sliding(text: str, max_chars: int, overlap: int) -> List[str]:
    out = []
    i = 0
    n = len(text)
    step = max_chars - overlap if max_chars > overlap else max_chars
    while i < n:
        start = max(0, i - (overlap if i != 0 else 0))
        end = min(i + max_chars, n)
        out.append(text[start:end])
        i += step
    return [c.strip() for c in out if c.strip()]

def split_markdown(md_text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    parts = re.split(r'(?m)^(#{1,6}\s.+)$', md_text)
    combined = []
    cur = ""
    for p in parts:
        if not p.strip():
            continue
        if p.startswith("#"):
            if cur:
                combined.append(cur.strip())
                cur = ""
        cur += p + "\n"
    if cur:
        combined.append(cur.strip())

    chunks = []
    for blob in combined:
        if len(blob) <= max_chars:
            chunks.append(blob)
        else:
            chunks.extend(sliding(blob, max_chars, overlap))
    return [c.strip() for c in chunks if c.strip()]

def split_code_by_blocks(code: str, lang: str = "", max_chars: int = 1200, overlap: int = 150) -> List[str]:
    pattern = r'(?m)^(def\s+\w+\(|class\s+\w+\(|[a-zA-Z_\$][\w\$]*\s*\([^)]*\)\s*{)'
    hits = [m.start() for m in re.finditer(pattern, code)]
    if not hits:
        return sliding(code, max_chars, overlap)
    hits = [0] + hits + [len(code)]
    chunks = []
    for i in range(len(hits)-1):
        seg = code[hits[i]:hits[i+1]]
        if len(seg) <= max_chars:
            chunks.append(seg)
        else:
            chunks.extend(sliding(seg, max_chars, overlap))
    return [c.strip() for c in chunks if c.strip()]

def autodetect_language(path: str) -> str:
    return (path.rsplit('.', 1)[-1] if '.' in path else '').lower()
