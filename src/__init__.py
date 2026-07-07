"""NLP Query Understanding System - A comprehensive solution for query processing and intent classification."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .query_understanding import QueryUnderstandingSystem
from .intent_classifier import IntentClassifier
from .vector_store import FAISSVectorStore
from .ranking_pipeline import PersonalizedRankingPipeline, UserProfile, ServiceItem
from .embeddings import EmbeddingGenerator

__all__ = [
    "QueryUnderstandingSystem",
    "IntentClassifier", 
    "FAISSVectorStore",
    "PersonalizedRankingPipeline",
    "UserProfile",
    "ServiceItem",
    "EmbeddingGenerator"
]
