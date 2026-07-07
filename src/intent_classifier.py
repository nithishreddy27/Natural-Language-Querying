"""Intent classification system for hospitality and dining queries."""

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from typing import List, Dict, Tuple, Optional, Any
import logging
import json
import os
from .config import config

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Intent classification for hospitality and dining queries."""
    
    # Predefined intent categories for hospitality/dining
    INTENT_CATEGORIES = {
        "restaurant_search": [
            "find restaurant", "restaurant near me", "good restaurants", 
            "dining options", "where to eat", "restaurant recommendations"
        ],
        "cuisine_preference": [
            "italian food", "chinese restaurant", "mexican cuisine", 
            "vegetarian options", "vegan restaurants", "seafood"
        ],
        "reservation": [
            "book table", "make reservation", "reserve restaurant", 
            "table booking", "dinner reservation"
        ],
        "menu_inquiry": [
            "menu items", "what's on menu", "food options", 
            "dish recommendations", "specials today"
        ],
        "price_inquiry": [
            "restaurant prices", "how much", "cost", "expensive", 
            "cheap restaurants", "budget dining"
        ],
        "location_based": [
            "restaurants downtown", "near hotel", "walking distance", 
            "close to", "in the area"
        ],
        "rating_review": [
            "best rated", "reviews", "highly rated", "top restaurants", 
            "customer reviews", "restaurant ratings"
        ],
        "hours_availability": [
            "opening hours", "open now", "late night dining", 
            "breakfast hours", "when open"
        ],
        "dietary_restrictions": [
            "gluten free", "allergen free", "halal food", "kosher", 
            "dairy free", "nut free"
        ],
        "ambiance_preference": [
            "romantic restaurant", "family friendly", "quiet place", 
            "outdoor seating", "casual dining", "fine dining"
        ]
    }
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the intent classifier.
        
        Args:
            model_name: Name of the transformer model for classification
        """
        self.model_name = model_name or "microsoft/DialoGPT-medium"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.label_encoder = LabelEncoder()
        self.classifier_pipeline = None
        
        # Prepare training data from predefined categories
        self.training_data = self._prepare_training_data()
        
        logger.info(f"Initialized IntentClassifier with {len(self.INTENT_CATEGORIES)} intent categories")
    
    def _prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """Prepare training data from predefined intent categories.
        
        Returns:
            Tuple of (texts, labels)
        """
        texts = []
        labels = []
        
        for intent, examples in self.INTENT_CATEGORIES.items():
            for example in examples:
                texts.append(example)
                labels.append(intent)
                
                # Add variations for better training
                variations = [
                    f"I'm looking for {example}",
                    f"Can you help me with {example}",
                    f"I need {example}",
                    f"Show me {example}"
                ]
                
                for variation in variations:
                    texts.append(variation)
                    labels.append(intent)
        
        logger.info(f"Prepared {len(texts)} training examples for {len(set(labels))} intents")
        return texts, labels
    
    def setup_classifier(self) -> None:
        """Setup the classification pipeline using a pre-trained model."""
        try:
            # Use a lightweight classification model
            model_name = "facebook/bart-large-mnli"  # Good for zero-shot classification
            
            self.classifier_pipeline = pipeline(
                "zero-shot-classification",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info(f"Setup classification pipeline with model: {model_name}")
            
        except Exception as e:
            logger.error(f"Error setting up classifier: {e}")
            # Fallback to a simpler approach
            self._setup_simple_classifier()
    
    def _setup_simple_classifier(self) -> None:
        """Setup a simple keyword-based classifier as fallback."""
        logger.info("Using keyword-based classification as fallback")
        self.classifier_pipeline = None
    
    def classify_intent(self, query: str,
                       confidence_threshold: float = 0.3) -> Dict[str, Any]:
        """Classify the intent of a query.
        
        Args:
            query: Input query string
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            Dictionary with intent, confidence, and additional info
        """
        if self.classifier_pipeline is None:
            return self._classify_with_keywords(query)
        
        try:
            # Get candidate labels
            candidate_labels = list(self.INTENT_CATEGORIES.keys())
            
            # Perform zero-shot classification
            result = self.classifier_pipeline(query, candidate_labels)
            
            intent = result['labels'][0]
            confidence = result['scores'][0]

            # Zero-shot classification spreads probability across all candidate
            # labels, so scores are naturally lower than a dedicated classifier.
            # We keep the best-guess intent and its real confidence (useful for
            # downstream ranking and the UI) and just flag when it's uncertain,
            # rather than discarding the signal as "unknown".
            return {
                "intent": intent,
                "confidence": float(confidence),
                "low_confidence": bool(confidence < confidence_threshold),
                "all_scores": dict(zip(result['labels'], result['scores'])),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return self._classify_with_keywords(query)
    
    def _classify_with_keywords(self, query: str) -> Dict[str, Any]:
        """Fallback keyword-based classification.
        
        Args:
            query: Input query string
            
        Returns:
            Classification result
        """
        query_lower = query.lower()
        intent_scores = {}
        
        # Calculate scores based on keyword matches
        for intent, keywords in self.INTENT_CATEGORIES.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 1
            
            # Normalize score
            if keywords:
                intent_scores[intent] = score / len(keywords)
        
        # Find best match
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent]
            
            if best_score > 0:
                return {
                    "intent": best_intent,
                    "confidence": float(best_score),
                    "all_scores": intent_scores,
                    "query": query
                }
        
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "all_scores": intent_scores,
            "query": query
        }
    
    def batch_classify(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple queries at once.
        
        Args:
            queries: List of query strings
            
        Returns:
            List of classification results
        """
        results = []
        for query in queries:
            result = self.classify_intent(query)
            results.append(result)
        
        logger.info(f"Classified {len(queries)} queries")
        return results
    
    def get_intent_examples(self, intent: str) -> List[str]:
        """Get example queries for a specific intent.
        
        Args:
            intent: Intent category name
            
        Returns:
            List of example queries
        """
        return self.INTENT_CATEGORIES.get(intent, [])
    
    def get_all_intents(self) -> List[str]:
        """Get all available intent categories.
        
        Returns:
            List of intent category names
        """
        return list(self.INTENT_CATEGORIES.keys())
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model and configuration.
        
        Args:
            filepath: Path to save the model
        """
        model_data = {
            "intent_categories": self.INTENT_CATEGORIES,
            "model_name": self.model_name,
            "training_data": self.training_data
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"Saved intent classifier to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a saved model and configuration.
        
        Args:
            filepath: Path to load the model from
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                model_data = json.load(f)
            
            self.INTENT_CATEGORIES = model_data.get("intent_categories", self.INTENT_CATEGORIES)
            self.model_name = model_data.get("model_name", self.model_name)
            self.training_data = model_data.get("training_data", self.training_data)
            
            logger.info(f"Loaded intent classifier from {filepath}")
        else:
            logger.warning(f"Model file not found: {filepath}")
