"""Personalized ranking pipeline for local service discovery."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from .vector_store import FAISSVectorStore
from .intent_classifier import IntentClassifier
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """User profile for personalization."""
    user_id: str
    preferences: Dict[str, float]  # preference_type -> weight
    location: Optional[Tuple[float, float]] = None  # (lat, lon)
    dietary_restrictions: List[str] = None
    price_range: Optional[Tuple[float, float]] = None  # (min, max)
    cuisine_preferences: List[str] = None
    past_queries: List[str] = None
    
    def __post_init__(self):
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.cuisine_preferences is None:
            self.cuisine_preferences = []
        if self.past_queries is None:
            self.past_queries = []

@dataclass
class ServiceItem:
    """Represents a local service (restaurant, hotel, etc.)."""
    id: str
    name: str
    description: str
    category: str
    cuisine_type: Optional[str] = None
    price_range: Optional[int] = None  # 1-4 scale
    rating: Optional[float] = None
    location: Optional[Tuple[float, float]] = None
    features: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.metadata is None:
            self.metadata = {}

class PersonalizedRankingPipeline:
    """Personalized ranking pipeline for local service discovery."""
    
    def __init__(self, vector_store: FAISSVectorStore, 
                 intent_classifier: IntentClassifier):
        """Initialize the ranking pipeline.
        
        Args:
            vector_store: FAISS vector store for semantic search
            intent_classifier: Intent classification system
        """
        self.vector_store = vector_store
        self.intent_classifier = intent_classifier
        self.embedding_generator = EmbeddingGenerator()
        
        # Ranking weights for different factors
        self.ranking_weights = {
            "semantic_similarity": 0.4,
            "intent_match": 0.25,
            "user_preference": 0.2,
            "location_proximity": 0.1,
            "popularity": 0.05
        }
        
        logger.info("Initialized PersonalizedRankingPipeline")
    
    def rank_services(self, query: str,
                     services: List[ServiceItem],
                     user_profile: Optional[UserProfile] = None,
                     top_k: int = 10,
                     intent_result: Optional[Dict[str, Any]] = None) -> List[Tuple[ServiceItem, float, Dict[str, float]]]:
        """Rank services based on query and user profile.

        Args:
            query: User query string
            services: List of available services
            user_profile: Optional user profile for personalization
            top_k: Number of top results to return
            intent_result: Optional pre-computed intent classification. Pass this
                to avoid re-running the (expensive) intent classifier when the
                caller already has it.

        Returns:
            List of (service, total_score, score_breakdown) tuples
        """
        if not services:
            return []

        # Step 1: Intent classification (reuse the caller's result if provided)
        if intent_result is None:
            intent_result = self.intent_classifier.classify_intent(query)
        logger.debug(f"Classified intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.3f})")
        
        # Step 2: Semantic similarity scoring
        semantic_scores = self._compute_semantic_scores(query, services)
        
        # Step 3: Intent matching scores
        intent_scores = self._compute_intent_scores(intent_result, services)
        
        # Step 4: User preference scores
        preference_scores = self._compute_preference_scores(services, user_profile)
        
        # Step 5: Location proximity scores
        location_scores = self._compute_location_scores(services, user_profile)
        
        # Step 6: Popularity scores
        popularity_scores = self._compute_popularity_scores(services)
        
        # Step 7: Combine all scores
        final_scores = []
        for i, service in enumerate(services):
            score_breakdown = {
                "semantic_similarity": semantic_scores[i],
                "intent_match": intent_scores[i],
                "user_preference": preference_scores[i],
                "location_proximity": location_scores[i],
                "popularity": popularity_scores[i]
            }
            
            # Weighted combination
            total_score = sum(
                score_breakdown[factor] * weight 
                for factor, weight in self.ranking_weights.items()
            )
            
            final_scores.append((service, total_score, score_breakdown))
        
        # Sort by total score (descending)
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Ranked {len(services)} services, returning top {min(top_k, len(final_scores))}")
        return final_scores[:top_k]
    
    def _compute_semantic_scores(self, query: str, 
                               services: List[ServiceItem]) -> List[float]:
        """Compute semantic similarity scores between query and services.
        
        Args:
            query: User query
            services: List of services
            
        Returns:
            List of semantic similarity scores
        """
        # Create service descriptions for embedding
        service_texts = []
        for service in services:
            text = f"{service.name} {service.description}"
            if service.cuisine_type:
                text += f" {service.cuisine_type} cuisine"
            if service.features:
                text += f" {' '.join(service.features)}"
            service_texts.append(text)
        
        # Generate embeddings
        query_embedding = self.embedding_generator.encode_queries([query])
        service_embeddings = self.embedding_generator.encode_documents(service_texts)
        
        # Compute similarities
        similarities = self.embedding_generator.compute_similarity(
            query_embedding[0], service_embeddings
        )
        
        return similarities.tolist()
    
    def _compute_intent_scores(self, intent_result: Dict[str, Any], 
                             services: List[ServiceItem]) -> List[float]:
        """Compute intent matching scores.
        
        Args:
            intent_result: Result from intent classification
            services: List of services
            
        Returns:
            List of intent matching scores
        """
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        scores = []
        for service in services:
            score = 0.0
            
            # Match intent with service characteristics
            if intent == "restaurant_search":
                score = 1.0 if service.category == "restaurant" else 0.5
            elif intent == "cuisine_preference":
                if service.cuisine_type and any(
                    cuisine in intent_result["query"].lower() 
                    for cuisine in [service.cuisine_type.lower()]
                ):
                    score = 1.0
                else:
                    score = 0.3
            elif intent == "price_inquiry":
                # Boost services with price information
                score = 0.8 if service.price_range is not None else 0.2
            elif intent == "rating_review":
                # Boost highly rated services
                if service.rating:
                    score = min(service.rating / 5.0, 1.0)
                else:
                    score = 0.3
            elif intent == "location_based":
                # Boost services with location info
                score = 0.9 if service.location else 0.1
            else:
                score = 0.5  # Default score for other intents
            
            # Weight by intent confidence
            scores.append(score * confidence)
        
        return scores
    
    def _compute_preference_scores(self, services: List[ServiceItem],
                                 user_profile: Optional[UserProfile]) -> List[float]:
        """Compute user preference scores.
        
        Args:
            services: List of services
            user_profile: User profile (optional)
            
        Returns:
            List of preference scores
        """
        if not user_profile:
            return [0.5] * len(services)  # Neutral score
        
        scores = []
        for service in services:
            score = 0.5  # Base score
            
            # Cuisine preference matching
            if (service.cuisine_type and 
                service.cuisine_type.lower() in [c.lower() for c in user_profile.cuisine_preferences]):
                score += 0.3
            
            # Price range matching
            if (user_profile.price_range and service.price_range):
                min_price, max_price = user_profile.price_range
                if min_price <= service.price_range <= max_price:
                    score += 0.2
            
            # Dietary restrictions
            if user_profile.dietary_restrictions:
                for restriction in user_profile.dietary_restrictions:
                    if restriction.lower() in [f.lower() for f in service.features]:
                        score += 0.2
                        break
            
            # Category preferences
            category_pref = user_profile.preferences.get(service.category, 0.5)
            score = score * (0.5 + category_pref)
            
            scores.append(min(score, 1.0))  # Cap at 1.0
        
        return scores
    
    def _compute_location_scores(self, services: List[ServiceItem],
                               user_profile: Optional[UserProfile]) -> List[float]:
        """Compute location proximity scores.
        
        Args:
            services: List of services
            user_profile: User profile (optional)
            
        Returns:
            List of location proximity scores
        """
        if not user_profile or not user_profile.location:
            return [0.5] * len(services)  # Neutral score
        
        user_lat, user_lon = user_profile.location
        scores = []
        
        for service in services:
            if not service.location:
                scores.append(0.3)  # Lower score for services without location
                continue
            
            # Calculate distance (simplified Euclidean distance)
            service_lat, service_lon = service.location
            distance = np.sqrt((user_lat - service_lat)**2 + (user_lon - service_lon)**2)
            
            # Convert distance to score (closer = higher score)
            # Assuming distance is in degrees, normalize to 0-1 range
            max_distance = 1.0  # Adjust based on your use case
            proximity_score = max(0.0, 1.0 - (distance / max_distance))
            scores.append(proximity_score)
        
        return scores
    
    def _compute_popularity_scores(self, services: List[ServiceItem]) -> List[float]:
        """Compute popularity scores based on ratings.
        
        Args:
            services: List of services
            
        Returns:
            List of popularity scores
        """
        scores = []
        for service in services:
            if service.rating:
                # Normalize rating to 0-1 scale (assuming 5-star rating)
                score = min(service.rating / 5.0, 1.0)
            else:
                score = 0.5  # Default score for services without ratings
            
            scores.append(score)
        
        return scores
    
    def update_user_profile(self, user_profile: UserProfile, 
                          query: str, selected_service: ServiceItem) -> UserProfile:
        """Update user profile based on interaction.
        
        Args:
            user_profile: Current user profile
            query: User's query
            selected_service: Service the user selected
            
        Returns:
            Updated user profile
        """
        # Add query to history
        user_profile.past_queries.append(query)
        
        # Update cuisine preferences
        if selected_service.cuisine_type:
            if selected_service.cuisine_type not in user_profile.cuisine_preferences:
                user_profile.cuisine_preferences.append(selected_service.cuisine_type)
        
        # Update category preferences
        category = selected_service.category
        current_pref = user_profile.preferences.get(category, 0.5)
        user_profile.preferences[category] = min(current_pref + 0.1, 1.0)
        
        logger.debug(f"Updated user profile for user {user_profile.user_id}")
        return user_profile
