"""Loader korpus berbasis manifest + pembersihan teks (Data & Knowledge Layer, M3).

Alur: ``corpus_manifest.csv`` -> pilih dokumen (KEEP / KEEP_PROVISIONAL / REVISE)
-> ekstraksi teks (md/txt langsung, PDF via pypdf) -> pembersihan -> ``Document``.
Dokumen yang gagal (mis. PDF hasil scan tanpa teks) TIDAK diam-diam dilewati:
alasannya dicatat di ``LoadReport`` agar bisa masuk laporan.
"""

from __future__ import annotations

import csv
import difflib
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS_DIR = ROOT / "data" / "corpus"
DEFAULT_MANIFEST = DEFAULT_CORPUS_DIR / "corpus_manifest.csv"
INCLUDED_DECISIONS = ("KEEP", "KEEP_PROVISIONAL", "REVISE")
MIN_WORDS = 50  # di bawah ini dianggap gagal ekstraksi (PDF scan)


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    meta: dict


@dataclass
class LoadReport:
    loaded: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (doc_id, alasan)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------- pembersihan
_BROWSER_HEADER = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M\b.*$", re.M)
_URL_FOOTER = re.compile(r"^\s*https?://\S+(\s+[\w ]+)?(\s+\d+/\d+)?\s*$", re.M)
_PAGE_NUM = re.compile(r"^\s*[-–]?\s*\d{1,3}\s*[-–]?\s*$", re.M)
_EXTRACTION_NOTE = re.compile(r"^\s*\[?\(?catatan ekstraksi[^\n]*$", re.I | re.M)


def _norm_line(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip().lower())


def _strip_repeated_lines(pages: list[str], min_ratio: float = 0.3) -> list[str]:
    """Hapus header/footer: baris (digit dinormalisasi) yang muncul di >= 30% halaman."""
    if len(pages) < 3:
        return pages
    counts: Counter[str] = Counter()
    for page in pages:
        counts.update({_norm_line(l) for l in page.splitlines() if l.strip()})
    limit = max(2, int(len(pages) * min_ratio))
    noisy = {l for l, c in counts.items() if c >= limit and len(l) < 120}
    return ["\n".join(l for l in p.splitlines() if _norm_line(l) not in noisy) for p in pages]


# Boilerplate halaman bantuan (menu navigasi, feedback, artikel terkait, footer)
_CUT_FROM = re.compile(r"(Apakah kamu puas dengan artikelnya\?|^\s*Artikel Terkait\b).*", re.M | re.S)
_DROP_LINES = re.compile(
    r"^\s*(Hai, ada yang bisa kami bantu\?|Belanja di Shopee\b.*|Penawaran & Hadiah Pembayaran\b.*|Mencari\.\.\.|Kebijakan Pusat Bantuan"
    r"|Ketik kata kunci.*|Bantuan|Lihat|Semua|Topik|Masuk|Daftar|Kembali|Cari)\s*$",
    re.M,
)


_SHOPEE_NAV = re.compile(r"Penawaran & Hadiah\s+Pembayaran.*?ShopeePay\b", re.S)


def strip_web_boilerplate(text: str) -> str:
    text = _CUT_FROM.sub("", text)
    text = _SHOPEE_NAV.sub("", text)
    text = re.sub(r"Kebijakan SPayLater\s+Kebijakan SPinjam\s+Kebijakan Mitra Shopee\s+ShopeeFood\s+ShopeePay", "", text)
    text = re.sub(r"[\ue000-\uf8ff]", "", text)  # glyph ikon (private-use) dari web-print
    return _DROP_LINES.sub("", text)


def clean_text(text: str) -> str:
    """Pembersihan umum: noise web-print, nomor halaman, hyphenation, whitespace."""
    text = strip_web_boilerplate(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\ufeff", "")
    text = text.replace("\u00a0", " ").replace("\f", "\n")
    text = _BROWSER_HEADER.sub("", text)
    text = _URL_FOOTER.sub("", text)
    text = _PAGE_NUM.sub("", text)
    text = _EXTRACTION_NOTE.sub("", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)           # kata terpotong di akhir baris
    text = re.sub(r"(?<![\n.:;!?])\n(?!\n|\s*(?:\(\d+\)|[a-z]\.|\d+\.|#|[-*•]|Pasal|BAB|Bagian))", " ", text)  # satukan baris dalam paragraf
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ----------------------------------------------------------------- ekstraksi
def _read_pdf(path: Path) -> str:
    import pymupdf  # PyMuPDF: mempertahankan spasi antar baris (pypdf menempelkan kata)

    with pymupdf.open(str(path)) as pdf:
        pages = [page.get_text() for page in pdf]
    return "\n\f".join(_strip_repeated_lines(pages))


def _ocr_pdf(path: Path) -> str:  # opsional; butuh pypdfium2 + pytesseract + binary tesseract
    import pypdfium2 as pdfium
    import pytesseract

    pdf = pdfium.PdfDocument(str(path))
    out = []
    for page in pdf:
        img = page.render(scale=3).to_pil()
        try:
            out.append(pytesseract.image_to_string(img, lang="ind+eng"))
        except pytesseract.TesseractError:
            out.append(pytesseract.image_to_string(img, lang="eng"))
    return "\n\f".join(out)


def extract_text(path: Path, use_ocr: bool = False) -> str:
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        return path.read_text(encoding="utf-8-sig")
    if suffix == ".pdf":
        raw = _read_pdf(path)
        if use_ocr and len(raw.split()) < MIN_WORDS:
            raw = _ocr_pdf(path)
        return raw
    raise ValueError(f"Format tidak didukung: {path.name}")


def strip_md_front_matter(text: str) -> str:
    """Buang blok metadata (Judul/Sumber/URL/Tanggal) sebelum '## ISI DOKUMEN'."""
    m = re.search(r"^##\s*ISI DOKUMEN\s*$", text, re.M | re.I)
    return text[m.end():] if m else text


# --------------------------------------------------------------------- loader
def _resolve_file(corpus_dir: Path, folder: str, name: str, report: LoadReport) -> Path | None:
    for base in (corpus_dir / folder, *[p for p in corpus_dir.iterdir() if p.is_dir()]):
        if (base / name).is_file():
            return base / name
    candidates = [f for p in corpus_dir.rglob("*") if p.is_file() for f in [p]]
    close = difflib.get_close_matches(name, [c.name for c in candidates], n=1, cutoff=0.8)
    if close:
        found = next(c for c in candidates if c.name == close[0])
        report.warnings.append(f"Nama file manifest '{name}' tidak persis; memakai '{found.name}'. Perbaiki manifest.")
        return found
    return None


def load_corpus(
    manifest_path: Path | str = DEFAULT_MANIFEST,
    corpus_dir: Path | str = DEFAULT_CORPUS_DIR,
    use_ocr: bool = False,
) -> tuple[list[Document], LoadReport]:
    manifest_path, corpus_dir = Path(manifest_path), Path(corpus_dir)
    report, docs = LoadReport(), []
    with manifest_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        doc_id = row["document_id"]
        if row["decision"] not in INCLUDED_DECISIONS:
            report.skipped.append((doc_id, f"decision={row['decision']}"))
            continue
        path = _resolve_file(corpus_dir, row["suggested_folder"], row["file_name"], report)
        if path is None:
            report.skipped.append((doc_id, "file tidak ditemukan"))
            continue
        raw = extract_text(path, use_ocr=use_ocr)
        if path.suffix.lower() == ".md":
            raw = strip_md_front_matter(raw)
        text = clean_text(raw)
        if len(text.split()) < MIN_WORDS:
            report.skipped.append((doc_id, "teks kosong/terlalu pendek (kemungkinan PDF scan)"))
            continue
        meta = {
            "doc_id": doc_id,
            "title": row["title"],
            "platform": row["platform"],
            "category": row["category"],
            "doc_type": "regulation" if doc_id.startswith("REG") else "marketplace_policy",
            "source_file": path.name,
            "source_url": row.get("source_url", ""),
            "access_date": row.get("access_date", ""),
            "validity_status": row.get("validity_status", ""),
            "decision": row["decision"],
        }
        docs.append(Document(doc_id, row["title"], text, meta))
        report.loaded.append(doc_id)
    return docs, report
