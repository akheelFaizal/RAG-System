import os
import tempfile
from git import Repo

def clone_or_use_local(repo_or_path: str) -> str:
    if os.path.isdir(repo_or_path):
        return os.path.abspath(repo_or_path)
    tmp = tempfile.mkdtemp(prefix="repo_")
    Repo.clone_from(repo_or_path, tmp, depth=1)
    return tmp
