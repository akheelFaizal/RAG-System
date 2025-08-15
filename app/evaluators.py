from typing import List, Dict, Tuple

def precision_at_k(queries: List[Dict], retrieve_fn, k: int = 5) -> Tuple[float, List[Dict]]:
    correct = 0
    details = []
    for q in queries:
        docs, metas, dists = retrieve_fn(q['question'], k=k)
        paths = [m.get('path', '') for m in metas]
        # If ANY expected keyword appears in ANY retrieved path, count as hit
        expected = q.get('relevant_keywords', [])
        hit = any(any(kw.lower() in p.lower() for kw in expected) for p in paths) if expected else False
        correct += 1 if hit else 0
        details.append({'question': q['question'], 'retrieved_paths': paths, 'hit': hit})
    return (correct / max(1, len(queries))), details
