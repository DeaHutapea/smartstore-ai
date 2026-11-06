"""
Recursive Word-Aware Text Splitter
"""

from __future__ import annotations
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .loader import Document
from .config import get_chunk_config, ChunkConfig


def chunk_documents(
    documents: List[Document],
    preset: str = "medium",
    custom_size: int = None,
    custom_overlap: int = None
) -> List[Document]:
    """
    Membagi dokumen menjadi chunk rekursif berlandaskan pemisah kalimat/paragraf
    dan menyematkan metadata 'chunk_id' unik (misal: doc_id_c0, doc_id_c1).
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
        
        for idx, chunk_text in enumerate(raw_chunks):
            meta = dict(doc.metadata)
            meta["chunk_id"] = f"{doc_id}_c{idx}"
            chunked_docs.append(Document(page_content=chunk_text, metadata=meta))

    return chunked_docs