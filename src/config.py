"""Configuration settings for the NLP Query Understanding System."""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for model settings."""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    intent_model: str = "microsoft/DialoGPT-medium"
    max_sequence_length: int = 512
    embedding_dim: int = 384
    
@dataclass
class FAISSConfig:
    """Configuration for FAISS vector storage."""
    index_type: str = "IndexFlatIP"  # Inner Product for cosine similarity
    nlist: int = 100  # Number of clusters for IVF
    nprobe: int = 10  # Number of clusters to search
    
@dataclass
class SystemConfig:
    """Main system configuration."""
    model: ModelConfig = ModelConfig()
    faiss: FAISSConfig = FAISSConfig()
    data_dir: str = "data"
    models_dir: str = "models"
    cache_dir: str = ".cache"
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Create directories if they don't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

# Global configuration instance
config = SystemConfig()
