"""
Automated Pytest Suite untuk RAG Pipeline T03 SmartStore AI
"""

import pytest
import shutil
from pathlib import Path
import sys
import os

# Memastikan modul src dapat diimpor
sys.path.insert(0, os.path.abspath("."))

from src.knowledge.loader import clean_text, load_single_file, detect_platform
from src.knowledge.chunker import chunk_documents
from src.knowledge.pipeline import ingest_documents, retrieve_documents, query_knowledge_base


@pytest.fixture(scope="module")
def sample_corpus_dir(tmp_path_factory):
    """Membuat folder korpus sementara untuk isolasi pengujian."""
    tmp_dir = tmp_path_factory.mktemp("test_corpus")
    
    # Berkas Tokopedia
    tokped_file = tmp_dir / "SOP_Tokopedia_Bebas_Ongkir.txt"
    tokped_file.write_text("SOP Tokopedia Bebas Ongkir. Syarat belanja minimal Rp70.000 per toko.", encoding="utf-8")
    
    # Berkas Shopee
    shopee_file = tmp_dir / "SOP_Shopee_Retur.md"
    shopee_file.write_text("# SOP Shopee Retur\n\nKlaim retur barang di Shopee wajib melampirkan video unboxing.", encoding="utf-8")
    
    # Berkas Regulasi
    reg_file = tmp_dir / "Permendag_31_2023.txt"
    reg_file.write_text("Permendag No 31 Tahun 2023 mengatur penyelenggaraan perdagangan melalui sistem elektronik.", encoding="utf-8")
    
    return str(tmp_dir)


@pytest.fixture(scope="module")
def sample_chroma_dir(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("test_chroma")
    return str(tmp_dir)


def test_01_text_cleaning():
    raw_text = " Teks   SOP   dengan   noise \r\n\n\n dan  spasi.  "
    cleaned = clean_text(raw_text)
    assert cleaned == "Teks SOP dengan noise\n\ndan spasi."


def test_02_platform_detection():
    assert detect_platform("SOP_Tokopedia_Ongkir.pdf") == "Tokopedia"
    assert detect_platform("SOP_Shopee_Garansi.md") == "Shopee"
    assert detect_platform("Permendag_31_2023.txt") == "Regulasi"


def test_03_metadata_extraction(sample_corpus_dir):
    files = list(Path(sample_corpus_dir).glob("*.txt"))
    docs = load_single_file(files[0])
    assert len(docs) > 0
    meta = docs[0].metadata
    assert "document_id" in meta
    assert "platform" in meta
    assert "category" in meta
    assert "page_number" in meta


def test_04_chunking_with_ids(sample_corpus_dir):
    docs = load_single_file(Path(sample_corpus_dir) / "SOP_Shopee_Retur.md")
    chunks = chunk_documents(docs, preset="small")
    assert len(chunks) >= 1
    assert "chunk_id" in chunks[0].metadata
    assert chunks[0].metadata["chunk_id"].endswith("_c0")


def test_05_ingestion_and_persistence(sample_corpus_dir, sample_chroma_dir):
    store = ingest_documents(
        corpus_dir=sample_corpus_dir,
        db_dir=sample_chroma_dir,
        chunk_preset="small",
        reset_db=True
    )
    assert store is not None


def test_06_in_domain_retrieval(sample_chroma_dir):
    res = retrieve_documents(
        query="Berapa syarat belanja minimal bebas ongkir Tokopedia?",
        top_k=2,
        threshold=0.30,
        db_dir=sample_chroma_dir
    )
    assert res["status"] == "SUCCESS"
    assert len(res["documents"]) > 0
    assert res["top_score"] >= 0.30


def test_07_out_of_domain_guardrail(sample_chroma_dir):
    res = query_knowledge_base(
        query="Bagaimana resep membuat martabak manis rasa cokelat?",
        top_k=1,
        threshold=0.60
    )
    assert res["status"] == "REJECTED_OUT_OF_DOMAIN"
    assert len(res["documents"]) == 0