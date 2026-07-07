"""Main query understanding system that integrates all components."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from .vector_store import FAISSVectorStore
from .intent_classifier import IntentClassifier
from .ranking_pipeline import PersonalizedRankingPipeline, UserProfile, ServiceItem
from .embeddings import EmbeddingGenerator
from .config import config

logger = logging.getLogger(__name__)

class QueryUnderstandingSystem:
    """Main system for NLP-powered query understanding and intent classification."""
    
    def __init__(self):
        """Initialize the query understanding system."""
        logger.info("Initializing Query Understanding System...")
        
        # Initialize components
        self.vector_store = FAISSVectorStore()
        self.intent_classifier = IntentClassifier()
        self.ranking_pipeline = PersonalizedRankingPipeline(
            self.vector_store, self.intent_classifier
        )
        
        # Setup intent classifier
        self.intent_classifier.setup_classifier()
        
        # System state
        self.is_initialized = False
        self.services_loaded = False
        
        logger.info("Query Understanding System initialized successfully")
    
    def load_services(self, services: List[ServiceItem]) -> None:
        """Load services into the vector store.
        
        Args:
            services: List of service items to index
        """
        if not services:
            logger.warning("No services provided to load")
            return
        
        # Prepare documents for vector store
        documents = []
        metadata = []
        
        for service in services:
            # Create searchable document text
            doc_text = f"{service.name} {service.description}"
            if service.cuisine_type:
                doc_text += f" {service.cuisine_type} cuisine"
            if service.features:
                doc_text += f" {' '.join(service.features)}"
            
            documents.append(doc_text)
            metadata.append({
                "service_id": service.id,
                "name": service.name,
                "category": service.category,
                "cuisine_type": service.cuisine_type,
                "price_range": service.price_range,
                "rating": service.rating,
                "location": service.location
            })
        
        # Add to vector store
        self.vector_store.add_documents(documents, metadata)
        self.services_loaded = True
        
        logger.info(f"Loaded {len(services)} services into the system")
    
    def process_query(self, query: str, 
                     user_profile: Optional[UserProfile] = None,
                     top_k: int = 10) -> Dict[str, Any]:
        """Process a user query and return ranked results.
        
        Args:
            query: User query string
            user_profile: Optional user profile for personalization
            top_k: Number of top results to return
            
        Returns:
            Dictionary containing query analysis and ranked results
        """
        logger.info(f"Processing query: '{query[:50]}...'")
        
        # Step 1: Intent classification
        intent_result = self.intent_classifier.classify_intent(query)
        
        # Step 2: Semantic search in vector store
        semantic_results = self.vector_store.search(query, k=top_k * 2)  # Get more for reranking
        
        # Step 3: Create service objects from search results
        services = []
        for doc, score, metadata in semantic_results:
            service = ServiceItem(
                id=metadata.get("service_id", "unknown"),
                name=metadata.get("name", "Unknown"),
                description=doc,
                category=metadata.get("category", "unknown"),
                cuisine_type=metadata.get("cuisine_type"),
                price_range=metadata.get("price_range"),
                rating=metadata.get("rating"),
                location=metadata.get("location")
            )
            services.append(service)
        
        # Step 4: Personalized ranking (reuse the intent computed in Step 1 so the
        # expensive classifier doesn't run twice for the same query)
        if services:
            ranked_results = self.ranking_pipeline.rank_services(
                query, services, user_profile, top_k, intent_result=intent_result
            )
        else:
            ranked_results = []
        
        # Step 5: Prepare response
        response = {
            "query": query,
            "intent": intent_result,
            "semantic_search_count": len(semantic_results),
            "final_results_count": len(ranked_results),
            "results": []
        }
        
        # Format results
        for service, total_score, score_breakdown in ranked_results:
            result = {
                "service": {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "category": service.category,
                    "cuisine_type": service.cuisine_type,
                    "price_range": service.price_range,
                    "rating": service.rating,
                    "location": service.location
                },
                "total_score": total_score,
                "score_breakdown": score_breakdown
            }
            response["results"].append(result)
        
        logger.info(f"Query processed successfully. Found {len(ranked_results)} results")
        return response
    
    def analyze_query_patterns(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze patterns in multiple queries.
        
        Args:
            queries: List of query strings
            
        Returns:
            Analysis results
        """
        intent_results = self.intent_classifier.batch_classify(queries)
        
        # Analyze intent distribution
        intent_counts = {}
        confidence_scores = []
        
        for result in intent_results:
            intent = result["intent"]
            confidence = result["confidence"]
            
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            confidence_scores.append(confidence)
        
        # Calculate statistics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        analysis = {
            "total_queries": len(queries),
            "intent_distribution": intent_counts,
            "average_confidence": avg_confidence,
            "low_confidence_queries": [
                result["query"] for result in intent_results 
                if result["confidence"] < 0.5
            ]
        }
        
        return analysis
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and health information.
        
        Returns:
            System statistics
        """
        stats = {
            "services_loaded": self.services_loaded,
            "total_services": len(self.vector_store.documents),
            "available_intents": self.intent_classifier.get_all_intents(),
            "vector_store_initialized": self.vector_store.index is not None,
            "embedding_dimension": self.vector_store.embedding_dim
        }
        
        return stats
    
    def save_system(self, base_path: str) -> None:
        """Save the entire system to disk.
        
        Args:
            base_path: Base path for saving system components
        """
        import os
        os.makedirs(base_path, exist_ok=True)
        
        # Save vector store
        self.vector_store.save(os.path.join(base_path, "vector_store"))
        
        # Save intent classifier
        self.intent_classifier.save_model(os.path.join(base_path, "intent_classifier.json"))
        
        logger.info(f"System saved to {base_path}")
    
    def load_system(self, base_path: str) -> None:
        """Load the entire system from disk.
        
        Args:
            base_path: Base path for loading system components
        """
        import os
        
        # Load vector store
        vector_store_path = os.path.join(base_path, "vector_store")
        if os.path.exists(f"{vector_store_path}.faiss"):
            self.vector_store.load(vector_store_path)
            self.services_loaded = True
        
        # Load intent classifier
        intent_classifier_path = os.path.join(base_path, "intent_classifier.json")
        if os.path.exists(intent_classifier_path):
            self.intent_classifier.load_model(intent_classifier_path)
        
        self.is_initialized = True
        logger.info(f"System loaded from {base_path}")
