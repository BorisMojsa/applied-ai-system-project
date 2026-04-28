from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


@dataclass(frozen=True)
class RetrievedChunk:
    doc_path: str
    title: str
    chunk_text: str
    score: float


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_title(md_text: str, fallback: str) -> str:
    fm = re.search(r"^title:\s*(.+)\s*$", md_text, flags=re.MULTILINE)
    if fm:
        return fm.group(1).strip()
    for line in md_text.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return fallback


def _chunk_markdown(md_text: str, max_chars: int = 900) -> List[str]:
    blocks: List[str] = []
    buf: List[str] = []
    size = 0

    for line in md_text.splitlines():
        buf.append(line)
        size += len(line) + 1
        if size >= max_chars:
            blocks.append("\n".join(buf).strip())
            buf, size = [], 0

    if buf:
        blocks.append("\n".join(buf).strip())

    return [b for b in blocks if b]


def load_knowledge_base(kb_dir: str | os.PathLike) -> List[Tuple[str, str, str]]:
    """
    Returns a list of (doc_path, title, chunk_text) tuples.
    Keeps things simple: markdown files are chunked into small passages.
    """
    kb_path = Path(kb_dir)
    docs: List[Tuple[str, str, str]] = []
    for md in sorted(kb_path.glob("*.md")):
        text = _read_text(md)
        title = _extract_title(text, fallback=md.name)
        for chunk in _chunk_markdown(text):
            docs.append((str(md), title, chunk))
    return docs


def retrieve(
    query: str,
    documents: Sequence[Tuple[str, str, str]],
    top_k: int = 3,
) -> List[RetrievedChunk]:
    """
    Lightweight retrieval using TF-IDF cosine similarity.
    Dependencies are imported lazily so the baseline recommender can still run
    even if the RAG extras aren't installed.
    """
    query = (query or "").strip()
    if not query or not documents:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "RAG retrieval requires scikit-learn. Install it with `pip install scikit-learn`."
        ) from e

    corpus = [d[2] for d in documents]
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(corpus)
    q = vectorizer.transform([query])
    sims = cosine_similarity(q, X).ravel()

    ranked_idx = sims.argsort()[::-1][: max(1, top_k)]
    results: List[RetrievedChunk] = []
    for idx in ranked_idx:
        doc_path, title, chunk_text = documents[int(idx)]
        results.append(
            RetrievedChunk(
                doc_path=doc_path,
                title=title,
                chunk_text=chunk_text,
                score=float(sims[int(idx)]),
            )
        )
    return results


def parse_synonym_map(chunks: Iterable[str]) -> Dict[str, List[str]]:
    """
    Parse lines like `- happy: upbeat, cheerful, ...` into a synonym map.
    Keys are canonical labels; values are lowercased synonyms including the key.
    """
    out: Dict[str, List[str]] = {}
    for chunk in chunks:
        for line in chunk.splitlines():
            m = re.match(r"^\s*-\s*([a-zA-Z0-9_ -]+)\s*:\s*(.+)\s*$", line.strip())
            if not m:
                continue
            key = m.group(1).strip().lower()
            syns = [s.strip().lower() for s in m.group(2).split(",") if s.strip()]
            syns = sorted({key, *syns})
            out[key] = syns
    return out

