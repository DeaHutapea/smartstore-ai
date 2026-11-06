"""Word-aware chunking dengan overlap (Milestone 3).

Strategi (rekursif: paragraf -> kalimat -> kata):
1. Teks dipecah per paragraf, lalu per kalimat; unit terkecil yang tidak boleh
   dipotong adalah KALIMAT, sehingga makna tidak terputus di tengah kalimat.
2. Kalimat dikumpulkan sampai ``chunk_words`` terlampaui.
3. Overlap: ``overlap_words`` kata terakhir (dibulatkan ke kalimat utuh) diulang
   di awal chunk berikutnya agar konteks lintas-batas tidak hilang.
4. Kalimat yang lebih panjang dari ``chunk_words`` dipotong per kata (fallback).
Ukuran dihitung dalam KATA (bukan karakter) supaya konsisten untuk bahasa Indonesia.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MERGE_TOLERANCE = 1.2  # sisa pendek boleh digabung selama chunk <= 120% ukuran target
_SENT_SPLIT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z0-9(\[\"“•-])")
_HEADING = re.compile(r"^\s*(?:#{1,4}\s+(?P<md>.+)|(?P<legal>(?:Pasal|BAB|Bagian|Paragraf)\s+[\dIVXLC]+[A-Za-z]?\b.*))\s*$")


@dataclass
class Chunk:
    index: int
    text: str
    word_count: int
    section: str  # heading terakhir (mis. "Pasal 14" / judul sub-bagian)


def _wc(s: str) -> int:
    return len(s.split())


def _units(text: str) -> list[tuple[str, str]]:
    """Pecah teks menjadi (kalimat, section). Section = heading terakhir yang terlihat."""
    units, section = [], ""
    for para in re.split(r"\n\s*\n|\n(?=\s*(?:#{1,4}\s|Pasal\s+\d|BAB\s))", text):
        para = para.strip()
        if not para:
            continue
        first = para.splitlines()[0]
        m = _HEADING.match(first)
        if m:
            section = (m.group("md") or m.group("legal") or "").strip()[:80]
        for sent in _SENT_SPLIT.split(para.replace("\n", " ")):
            if sent.strip():
                units.append((sent.strip(), section))
    return units


def _split_long(sentence: str, section: str, limit: int) -> list[tuple[str, str]]:
    words = sentence.split()
    return [(" ".join(words[i : i + limit]), section) for i in range(0, len(words), limit)]


def chunk_text(text: str, chunk_words: int = 180, overlap_words: int = 36, min_words: int = 20) -> list[Chunk]:
    """Pecah ``text`` menjadi chunk ~``chunk_words`` kata dengan overlap ``overlap_words``."""
    if overlap_words >= chunk_words:
        raise ValueError("overlap_words harus lebih kecil dari chunk_words")

    units: list[tuple[str, str]] = []
    for sent, sec in _units(text):
        units.extend(_split_long(sent, sec, chunk_words) if _wc(sent) > chunk_words else [(sent, sec)])

    chunks: list[Chunk] = []
    cur: list[tuple[str, str]] = []
    cur_words = 0

    def flush() -> None:
        body = " ".join(u[0] for u in cur).strip()
        chunks.append(Chunk(len(chunks), body, _wc(body), cur[0][1]))

    for unit in units:
        w = _wc(unit[0])
        if cur and cur_words + w > chunk_words:
            flush()
            # overlap: ambil kalimat-kalimat terakhir sampai <= overlap_words
            carry, carried = [], 0
            for u in reversed(cur):
                if carried + _wc(u[0]) > overlap_words:
                    break
                carry.insert(0, u)
                carried += _wc(u[0])
            cur, cur_words = carry, carried
        cur.append(unit)
        cur_words += w

    if cur:
        # sisa pendek digabung ke chunk sebelumnya (hindari chunk yatim)
        if chunks and cur_words < min_words and chunks[-1].word_count + cur_words <= chunk_words * MERGE_TOLERANCE:
            tail = " ".join(u[0] for u in cur if u[0] not in chunks[-1].text)
            if tail:
                chunks[-1].text += " " + tail
                chunks[-1].word_count = _wc(chunks[-1].text)
        else:
            flush()
    return chunks
