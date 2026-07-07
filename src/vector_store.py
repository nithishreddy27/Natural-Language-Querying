"""FAISS-based vector storage and retrieval system."""

import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Optional, Dict, Any
import logging
from .config import config
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """FAISS-based vector storage for semantic search."""
    
    def __init__(self, embedding_dim: Optional[int] = None):
        """Initialize the FAISS vector store.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim or config.model.embedding_dim
        self.index = None
        self.documents = []
        self.metadata = []
        self.embedding_generator = EmbeddingGenerator()
        
        # Update embedding dimension from the actual model
        self.embedding_dim = self.embedding_generator.embedding_dim
        
    def _create_index(self, index_type: str = "IndexFlatIP") -> faiss.Index:
        """Create a FAISS index.
        
        Args:
            index_type: Type of FAISS index to create
            
        Returns:
            FAISS index
        """
        if index_type == "IndexFlatIP":
            # Inner Product index (good for normalized embeddings)
            index = faiss.IndexFlatIP(self.embedding_dim)
        elif index_type == "IndexFlatL2":
            # L2 distance index
            index = faiss.IndexFlatL2(self.embedding_dim)
        elif index_type == "IndexIVFFlat":
            # IVF (Inverted File) index for faster search
            quantizer = faiss.IndexFlatIP(self.embedding_dim)
            index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, config.faiss.nlist)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        logger.info(f"Created FAISS index: {index_type}")
        return index
    
    def add_documents(self, documents: List[str], 
                     metadata: Optional[List[Dict[str, Any]]] = None,
                     batch_size: int = 1000) -> None:
        """Add documents to the vector store.
        
        Args:
            documents: List of document strings
            metadata: Optional metadata for each document
            batch_size: Batch size for processing
        """
        if not documents:
            return
        
        # Initialize index if not exists
        if self.index is None:
            self.index = self._create_index(config.faiss.index_type)
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedding_generator.encode_documents(
            documents, batch_size=batch_size
        )
        
        # Add to FAISS index
        self.index.add(embeddings.astype(np.float32))
        
        # Store documents and metadata
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in documents])
        
        logger.info(f"Added {len(documents)} documents to vector store")
        logger.info(f"Total documents in store: {len(self.documents)}")
    
    def search(self, query: str, k: int = 10, 
               score_threshold: float = 0.0) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar documents.
        
        Args:
            query: Query string
            k: Number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of (document, score, metadata) tuples
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_generator.encode_queries([query])
        
        # Search in FAISS index
        scores, indices = self.index.search(
            query_embedding.astype(np.float32), k
        )
        
        # Filter results by score threshold and format output
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score >= score_threshold:  # -1 indicates no match found
                document = self.documents[idx]
                metadata = self.metadata[idx] if idx < len(self.metadata) else {}
                results.append((document, float(score), metadata))
        
        logger.debug(f"Found {len(results)} results for query: '{query[:50]}...'")
        return results
    
    def save(self, filepath: str) -> None:
        """Save the vector store to disk.
        
        Args:
            filepath: Path to save the vector store
        """
        if self.index is None:
            logger.warning("No index to save")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.faiss")
        
        # Save documents and metadata
        with open(f"{filepath}.pkl", "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata,
                "embedding_dim": self.embedding_dim
            }, f)
        
        logger.info(f"Saved vector store to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load the vector store from disk.
        
        Args:
            filepath: Path to load the vector store from
        """
        # Load FAISS index
        if os.path.exists(f"{filepath}.faiss"):
            self.index = faiss.read_index(f"{filepath}.faiss")
            logger.info(f"Loaded FAISS index from {filepath}.faiss")
        
        # Load documents and metadata
        if os.path.exists(f"{filepath}.pkl"):
            with open(f"{filepath}.pkl", "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                self.embedding_dim = data["embedding_dim"]
            logger.info(f"Loaded {len(self.documents)} documents from {filepath}.pkl")
