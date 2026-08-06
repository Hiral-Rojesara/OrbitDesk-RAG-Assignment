import logging
from pathlib import Path
from typing import List, Optional, Union

import torch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from schema import RetrievedDoc

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_KB_PATH = BASE_DIR / "data" / "knowledge_base"
DEFAULT_INDEX_PATH = BASE_DIR / "data" / "faiss_index"


class OrbitDeskRetriever:
    """
    Pro-level RAG Retriever using LangChain, HuggingFace embeddings, and FAISS.
    Supports index persistence, smart GPU/CPU auto-detection, and diversity deduplication.
    """

    def __init__(
        self,
        kb_path: Optional[Union[Path, str]] = None,
        index_path: Optional[Union[Path, str]] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        force_rebuild: bool = False,
    ) -> None:
        self.kb_path = Path(kb_path) if kb_path else DEFAULT_KB_PATH
        self.index_path = Path(index_path) if index_path else DEFAULT_INDEX_PATH
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing embeddings model: {self.embedding_model_name} on device: {device}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": device}
        )
        
        self.vectorstore = self._load_or_build_vectorstore(force_rebuild)

    def _load_documents(self) -> List[Document]:
        """Loads all markdown documents from the knowledge base directory."""
        if not self.kb_path.exists() or not self.kb_path.is_dir():
            logger.error(f"Knowledge base directory missing at: {self.kb_path}")
            raise FileNotFoundError(f"Knowledge base folder not found: {self.kb_path}")

        documents: List[Document] = []
        md_files = list(self.kb_path.glob("*.md"))

        if not md_files:
            logger.warning(f"No Markdown (.md) files found in {self.kb_path}")

        for filepath in md_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                source_id = filepath.stem  
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"source_id": source_id},
                    )
                )
                logger.debug(f"Loaded document: {source_id}")
            except Exception as e:
                logger.error(f"Failed to load file {filepath.name}: {e}")

        logger.info(f"Successfully loaded {len(documents)} raw documents from {self.kb_path}")
        return documents

    def _load_or_build_vectorstore(self, force_rebuild: bool) -> FAISS:
        """Loads FAISS index from local disk if it exists, otherwise builds and saves it."""
        index_file = self.index_path / "index.faiss"
        pkl_file = self.index_path / "index.pkl"

        if index_file.exists() and pkl_file.exists() and not force_rebuild:
            logger.info(f"Loading existing FAISS index from: {self.index_path}")
            try:
                return FAISS.load_local(
                    str(self.index_path), 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                logger.warning(f"Failed to load local index ({e}). Rebuilding from scratch...")

        logger.info("Building FAISS vector index from documents...")
        docs = self._load_documents()

        if not docs:
            raise ValueError("Cannot build vectorstore with zero documents.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        chunks = splitter.split_documents(docs)
        logger.info(f"Split into {len(chunks)} chunks. Generating embeddings...")

        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        self.index_path.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(self.index_path))
        logger.info(f"FAISS vectorstore built and saved successfully to {self.index_path}")

        return vectorstore

    def search(self, query: str, top_k: int = 3) -> List[RetrievedDoc]:
        """
        Performs a semantic similarity search on the FAISS index with source deduplication.
        """
        if not query or not query.strip():
            logger.warning("Empty query received for retrieval.")
            return []

        try:
            fetch_k = max(top_k * 3, 10)
            results = self.vectorstore.similarity_search_with_score(query, k=fetch_k)
            
            retrieved_docs: List[RetrievedDoc] = []
            seen_sources = set()

            for doc, score in results:
                source_id = doc.metadata.get("source_id", "unknown")
                
                if source_id in seen_sources:
                    continue
                
                seen_sources.add(source_id)

                similarity = 1.0 / (1.0 + float(score))

                retrieved_docs.append(
                    RetrievedDoc(
                        source_id=source_id,
                        passage=doc.page_content,
                        score=round(similarity, 4),
                    )
                )

                if len(retrieved_docs) >= top_k:
                    break

            logger.info(f"Retrieved {len(retrieved_docs)} diverse documents for query: '{query[:30]}...'")
            return retrieved_docs

        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []
