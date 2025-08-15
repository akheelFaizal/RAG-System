import os
from typing import List

DOC_EXTS = {'.md', '.rst', '.txt'}
CODE_EXTS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.kt', '.go', '.rb', '.rs',
    '.cpp', '.hpp', '.c', '.h', '.php', '.cs', '.scala', '.swift', '.m', '.mm',
    '.sh', '.yaml', '.yml'
}
IGNORE_DIRS = {'.git', '.github', '.venv', 'node_modules', 'dist', 'build', '.next', '.cache', '__pycache__'}

def is_interesting_file(path: str) -> bool:
    _, ext = os.path.splitext(path.lower())
    return ext in DOC_EXTS or ext in CODE_EXTS

def walk_files(root: str) -> List[str]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith('.')]
        for f in filenames:
            full = os.path.join(dirpath, f)
            if is_interesting_file(full):
                files.append(full)
    return files

def read_text(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ""
