import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402

from knowledge.chunker import chunk_text  # noqa: E402
from knowledge.corpus_loader import Document, clean_text  # noqa: E402
from knowledge.retriever import Retriever  # noqa: E402
from knowledge.vector_store import VectorStore  # noqa: E402


class HashEmbedder:
    """Embedder palsu deterministik (bag-of-words hashing) agar test tidak butuh unduh model."""

    model_name = "hash-test"
    DIM = 256

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.DIM
        for tok in re.findall(r"\w+", text.lower()):
            v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % self.DIM] += 1.0
        n = sum(x * x for x in v) ** 0.5 or 1.0
        return [x / n for x in v]

    def embed_passages(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


SAMPLE = " ".join(f"Kalimat nomor {i} membahas kebijakan pengembalian dana pembeli." for i in range(60))


def test_chunks_respect_size_and_end_on_sentence():
    chunks = chunk_text(SAMPLE, chunk_words=50, overlap_words=10)
    assert len(chunks) > 1
    assert all(c.word_count <= 60 for c in chunks)
    assert all(c.text.endswith(".") for c in chunks)  # tidak memutus kalimat


def test_overlap_repeats_text_between_neighbours():
    chunks = chunk_text(SAMPLE, chunk_words=50, overlap_words=20)
    last_sentence = chunks[0].text.split(". ")[-1]
    assert last_sentence in chunks[1].text


def test_overlap_must_be_smaller_than_chunk():
    with pytest.raises(ValueError):
        chunk_text(SAMPLE, chunk_words=20, overlap_words=20)


def test_very_long_sentence_is_split_by_words():
    long = "kata " * 500 + "selesai."
    assert all(c.word_count <= 120 for c in chunk_text(long, chunk_words=100, overlap_words=10))  # toleransi merge 120%


def test_clean_text_removes_browser_noise_and_hyphenation():
    raw = "11/6/26, 2:04 PM Tokopedia Care\nperlin-\ndungan konsumen\nhttps://x.com/a 1/7\n"
    out = clean_text(raw)
    assert "Tokopedia Care" not in out and "perlindungan konsumen" in out and "https" not in out


def test_store_persists_and_returns_cosine_similarity(tmp_path):
    emb = HashEmbedder()
    store = VectorStore(emb, "test_kb", tmp_path)
    doc = Document("D1", "Refund", SAMPLE, {"doc_id": "D1", "title": "Refund", "category": "refund"})
    store.add_document(doc, chunk_text(SAMPLE, 50, 10), 50, 10)
    n = store.count()
    assert n > 1

    reopened = VectorStore(emb, "test_kb", tmp_path)  # persistensi: dibuka ulang dari disk
    assert reopened.count() == n
    hit = reopened.search("kebijakan pengembalian dana pembeli", k=1)[0]
    assert 0.0 < hit.similarity <= 1.0
    assert hit.metadata["doc_id"] == "D1" and hit.metadata["chunk_index"] >= 0
    assert reopened.search("x", k=1, where={"category": "tidak_ada"}) == []


def test_ood_threshold_rejects_unrelated_query(tmp_path):
    emb = HashEmbedder()
    store = VectorStore(emb, "test_kb_ood", tmp_path)
    doc = Document("D1", "Refund", SAMPLE, {"doc_id": "D1"})
    store.add_document(doc, chunk_text(SAMPLE, 50, 10), 50, 10)
    r = Retriever(store, threshold=0.5)
    assert r.retrieve("kebijakan pengembalian dana pembeli").in_domain
    assert not r.retrieve("resep nasi goreng seafood").in_domain
