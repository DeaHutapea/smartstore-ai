"""
Recursive Word-Aware Text Splitter dengan Metadata chunk_id Unik
"""

from __future__ import annotations
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .loader import Document
from .config import get_chunk_config, ChunkConfig


def chunk_documents(
    documents: List[Document],
    preset: str = "medium",
    custom_size: Optional[int] = None,
    custom_overlap: Optional[int] = None
) -> List[Document]:
    """
    Membagi dokumen menjadi potongan teks rekursif peka kata (word-aware)
    dan menyematkan metadata 'chunk_id' unik.
    """
    config: ChunkConfig = get_chunk_config(preset, custom_size, custom_overlap)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", " ", ""]
    )

    chunked_docs: List[Document] = []

    for doc in documents:
        raw_chunks = splitter.split_text(doc.page_content)
        doc_id = doc.metadata.get("document_id", "doc")
        page_num = doc.metadata.get("page_number", 1)
        
        for idx, chunk_text in enumerate(raw_chunks):
            meta = dict(doc.metadata)
            meta["chunk_id"] = f"{doc_id}_p{page_num}_c{idx}"
            chunked_docs.append(Document(page_content=chunk_text, metadata=meta))

    return chunked_docs