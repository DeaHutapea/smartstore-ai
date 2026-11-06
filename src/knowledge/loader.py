"""
Document Loader & Preprocessing Teks (PDF, MD, TXT)
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader


class Document:
    """Dataclass pembungkus teks dan metadata dokumen terstruktur."""
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self) -> str:
        return f"<Document id='{self.metadata.get('document_id')}' platform='{self.metadata.get('platform')}'>"


def clean_text(text: str) -> str:
    """
    Membersihkan noise ekstraksi dokumen:
    - Menghapus karakter kontrol tak terlihat (\x00-\x1f).
    - Normalisasi spasi dan baris baru berlebih.
    - Mempertahankan entitas angka, klausa hukum, dan istilah e-commerce.
    """
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def detect_platform(filename: str, content: str = "") -> str:
    """Mendeteksi platform asal dokumen berdasarkan nama berkas dan konten."""
    fn_lower = filename.lower()
    if any(k in fn_lower for k in ["tokopedia", "tokped"]):
        return "Tokopedia"
    elif "shopee" in fn_lower:
        return "Shopee"
    elif any(k in fn_lower for k in ["permendag", "uu_", "pp_", "peraturan", "regulasi"]):
        return "Regulasi"
    
    cnt_lower = content[:500].lower()
    if "tokopedia" in cnt_lower:
        return "Tokopedia"
    elif "shopee" in cnt_lower:
        return "Shopee"
    elif any(k in cnt_lower for k in ["pasal", "undang-undang", "peraturan menteri"]):
        return "Regulasi"
        
    return "General"


def extract_category(filename: str) -> str:
    """Mengekstrak kategori dokumen dari nama berkas (misal: SOP_01_Ketentuan_Gratis_Ongkir.pdf)."""
    parts = Path(filename).stem.split("_")
    if len(parts) >= 3:
        return parts[2] if len(parts[2]) > 2 else "_".join(parts[2:])
    elif len(parts) == 2:
        return parts[1]
    return "General"


def load_single_file(file_path: str | Path) -> List[Document]:
    """Membaca satu berkas (.pdf, .md, .txt) dan mengekstrak 7 atribut metadata terstruktur."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    ext = path.suffix.lower()
    filename = path.name
    doc_id = path.stem.replace(" ", "_")
    category = extract_category(filename)
    documents: List[Document] = []

    if ext == ".pdf":
        reader = PdfReader(str(path))
        for page_idx, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned = clean_text(raw_text)
            if len(cleaned) > 20:
                platform = detect_platform(filename, cleaned)
                metadata = {
                    "document_id": doc_id,
                    "document_name": filename,
                    "source": str(path),
                    "category": category,
                    "platform": platform,
                    "page_number": page_idx,
                }
                documents.append(Document(page_content=cleaned, metadata=metadata))

    elif ext in [".md", ".txt"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        cleaned = clean_text(raw_text)
        if len(cleaned) > 20:
            platform = detect_platform(filename, cleaned)
            metadata = {
                "document_id": doc_id,
                "document_name": filename,
                "source": str(path),
                "category": category,
                "platform": platform,
                "page_number": 1,
            }
            documents.append(Document(page_content=cleaned, metadata=metadata))

    return documents


def load_documents_from_dir(corpus_dir: str | Path) -> List[Document]:
    """Membaca secara otomatis seluruh berkas PDF, MD, dan TXT dari folder korpus."""
    target_dir = Path(corpus_dir)
    if not target_dir.exists():
        raise FileNotFoundError(f"Folder korpus '{corpus_dir}' tidak ditemukan.")

    all_docs: List[Document] = []
    supported_exts = {".pdf", ".md", ".txt"}

    for file_path in sorted(target_dir.glob("**/*")):
        if file_path.is_file() and file_path.suffix.lower() in supported_exts:
            docs = load_single_file(file_path)
            all_docs.extend(docs)

    return all_docs