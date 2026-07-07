"""Embedding generation using transformer models."""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import logging
from .config import config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generates embeddings using pre-trained transformer models."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name or config.model.embedding_model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load the sentence transformer model
        self.model = SentenceTransformer(self.model_name, device=self.device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Loaded embedding model: {self.model_name}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def encode_queries(self, queries: Union[str, List[str]], 
                      normalize: bool = True) -> np.ndarray:
        """Encode queries into embeddings.
        
        Args:
            queries: Single query string or list of queries
            normalize: Whether to normalize embeddings for cosine similarity
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(queries, str):
            queries = [queries]
        
        # Generate embeddings
        embeddings = self.model.encode(
            queries,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=len(queries) > 100
        )
        
        logger.debug(f"Generated embeddings for {len(queries)} queries")
        return embeddings
    
    def encode_documents(self, documents: List[str], 
                        batch_size: int = 32,
                        normalize: bool = True) -> np.ndarray:
        """Encode documents into embeddings with batching.
        
        Args:
            documents: List of document strings
            batch_size: Batch size for processing
            normalize: Whether to normalize embeddings
            
        Returns:
            Numpy array of document embeddings
        """
        embeddings = self.model.encode(
            documents,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=True
        )
        
        logger.info(f"Generated embeddings for {len(documents)} documents")
        return embeddings
    
    def compute_similarity(self, query_embedding: np.ndarray, 
                          doc_embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Single query embedding
            doc_embeddings: Array of document embeddings
            
        Returns:
            Array of similarity scores
        """
        # Ensure embeddings are normalized for cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        
        # Compute dot product (cosine similarity for normalized vectors)
        similarities = np.dot(doc_norms, query_norm)
        return similarities
