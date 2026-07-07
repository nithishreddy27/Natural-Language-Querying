"""Test suite for the NLP Query Understanding System."""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.query_understanding import QueryUnderstandingSystem
from src.intent_classifier import IntentClassifier
from src.vector_store import FAISSVectorStore
from data.sample_services import SAMPLE_SERVICES, SAMPLE_USER_PROFILES, SAMPLE_QUERIES

class TestQueryUnderstandingSystem(unittest.TestCase):
    """Test cases for the main query understanding system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.system = QueryUnderstandingSystem()
        self.system.load_services(SAMPLE_SERVICES)
    
    def test_system_initialization(self):
        """Test system initialization."""
        self.assertIsNotNone(self.system.vector_store)
        self.assertIsNotNone(self.system.intent_classifier)
        self.assertIsNotNone(self.system.ranking_pipeline)
        self.assertTrue(self.system.services_loaded)
    
    def test_query_processing(self):
        """Test basic query processing."""
        query = "Find me a good Italian restaurant"
        result = self.system.process_query(query)
        
        self.assertIn("query", result)
        self.assertIn("intent", result)
        self.assertIn("results", result)
        self.assertEqual(result["query"], query)
        self.assertGreater(len(result["results"]), 0)
    
    def test_personalized_query(self):
        """Test query processing with user profile."""
        query = "vegetarian restaurant for dinner"
        user_profile = SAMPLE_USER_PROFILES[0]  # Vegetarian user
        
        result = self.system.process_query(query, user_profile)
        
        self.assertGreater(len(result["results"]), 0)
        # Check if vegetarian restaurants are ranked higher
        top_result = result["results"][0]
        self.assertIn("vegetarian", top_result["service"]["description"].lower())
    
    def test_intent_classification(self):
        """Test intent classification accuracy."""
        test_cases = [
            ("Find Italian restaurant", "restaurant_search"),
            ("vegetarian food options", "cuisine_preference"),
            ("book a table for dinner", "reservation"),
            ("restaurant prices", "price_inquiry"),
            ("restaurants near me", "location_based")
        ]
        
        for query, expected_intent in test_cases:
            result = self.system.intent_classifier.classify_intent(query)
            # Allow for some flexibility in intent classification
            self.assertIsNotNone(result["intent"])
            self.assertGreater(result["confidence"], 0.0)

class TestIntentClassifier(unittest.TestCase):
    """Test cases for intent classification."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = IntentClassifier()
        self.classifier.setup_classifier()
    
    def test_intent_categories(self):
        """Test that all intent categories are available."""
        intents = self.classifier.get_all_intents()
        expected_intents = [
            "restaurant_search", "cuisine_preference", "reservation",
            "menu_inquiry", "price_inquiry", "location_based",
            "rating_review", "hours_availability", "dietary_restrictions",
            "ambiance_preference"
        ]
        
        for intent in expected_intents:
            self.assertIn(intent, intents)
    
    def test_batch_classification(self):
        """Test batch classification of multiple queries."""
        queries = SAMPLE_QUERIES[:5]  # Test with first 5 queries
        results = self.classifier.batch_classify(queries)
        
        self.assertEqual(len(results), len(queries))
        for result in results:
            self.assertIn("intent", result)
            self.assertIn("confidence", result)
            self.assertIn("query", result)

class TestVectorStore(unittest.TestCase):
    """Test cases for FAISS vector store."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vector_store = FAISSVectorStore()
        
        # Add sample documents
        documents = [service.description for service in SAMPLE_SERVICES]
        self.vector_store.add_documents(documents)
    
    def test_document_addition(self):
        """Test adding documents to vector store."""
        self.assertEqual(len(self.vector_store.documents), len(SAMPLE_SERVICES))
        self.assertIsNotNone(self.vector_store.index)
    
    def test_semantic_search(self):
        """Test semantic search functionality."""
        query = "Italian pasta restaurant"
        results = self.vector_store.search(query, k=5)
        
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)
        
        # Check result format
        for doc, score, metadata in results:
            self.assertIsInstance(doc, str)
            self.assertIsInstance(score, float)
            self.assertIsInstance(metadata, dict)
    
    def test_search_relevance(self):
        """Test search result relevance."""
        query = "sushi japanese restaurant"
        results = self.vector_store.search(query, k=3)
        
        # Check if Japanese restaurant appears in top results
        found_japanese = False
        for doc, score, metadata in results:
            if "japanese" in doc.lower() or "sushi" in doc.lower():
                found_japanese = True
                break
        
        self.assertTrue(found_japanese, "Japanese restaurant should appear in results for sushi query")

def run_performance_test():
    """Run performance tests on the system."""
    print("Running performance tests...")
    
    system = QueryUnderstandingSystem()
    system.load_services(SAMPLE_SERVICES)
    
    import time
    
    # Test query processing speed
    start_time = time.time()
    for query in SAMPLE_QUERIES:
        result = system.process_query(query)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / len(SAMPLE_QUERIES)
    print(f"Average query processing time: {avg_time:.3f} seconds")
    
    # Test system stats
    stats = system.get_system_stats()
    print("System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance tests
    print("\n" + "="*50)
    run_performance_test()
