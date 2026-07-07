"""Demonstration script for the NLP Query Understanding System."""

import sys
import os

# Ensure emoji/Unicode output works even when stdout is a Windows console or a
# redirected pipe (cp1252 would otherwise crash on characters like the rocket).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.query_understanding import QueryUnderstandingSystem
from data.sample_services import SAMPLE_SERVICES, SAMPLE_USER_PROFILES, SAMPLE_QUERIES
import json

def demo_basic_functionality():
    """Demonstrate basic system functionality."""
    print("🚀 NLP Query Understanding System Demo")
    print("=" * 50)
    
    # Initialize system
    print("Initializing system...")
    system = QueryUnderstandingSystem()
    system.load_services(SAMPLE_SERVICES)
    
    print(f"✅ Loaded {len(SAMPLE_SERVICES)} services into the system")
    
    # Demo queries
    demo_queries = [
        "Find me a good Italian restaurant for a romantic dinner",
        "I need vegetarian options that are gluten free",
        "Best sushi place with fresh fish",
        "Cheap Mexican food for lunch",
        "Fine dining restaurant for business meeting"
    ]
    
    print("\n📝 Processing Demo Queries:")
    print("-" * 30)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        result = system.process_query(query, top_k=3)
        
        # Display intent classification
        intent_info = result["intent"]
        print(f"   Intent: {intent_info['intent']} (confidence: {intent_info['confidence']:.2f})")
        
        # Display top results
        print("   Top Results:")
        for j, res in enumerate(result["results"][:3], 1):
            service = res["service"]
            score = res["total_score"]
            print(f"     {j}. {service['name']} - Score: {score:.3f}")
            print(f"        {service['description'][:80]}...")
            if service['cuisine_type']:
                print(f"        Cuisine: {service['cuisine_type']}, Price: {'$' * service['price_range']}")

def demo_personalized_search():
    """Demonstrate personalized search with user profiles."""
    print("\n\n🎯 Personalized Search Demo")
    print("=" * 50)
    
    system = QueryUnderstandingSystem()
    system.load_services(SAMPLE_SERVICES)
    
    query = "restaurant for dinner tonight"
    
    print(f"Query: '{query}'")
    print("\nComparing results for different user profiles:")
    
    for i, user_profile in enumerate(SAMPLE_USER_PROFILES, 1):
        print(f"\n👤 User {i} Profile:")
        print(f"   Preferences: {user_profile.cuisine_preferences}")
        print(f"   Dietary restrictions: {user_profile.dietary_restrictions}")
        print(f"   Price range: ${user_profile.price_range[0]}-{user_profile.price_range[1]}")
        
        result = system.process_query(query, user_profile, top_k=3)
        
        print("   Top Results:")
        for j, res in enumerate(result["results"][:3], 1):
            service = res["service"]
            score = res["total_score"]
            breakdown = res["score_breakdown"]
            print(f"     {j}. {service['name']} - Total Score: {score:.3f}")
            print(f"        Preference Score: {breakdown['user_preference']:.3f}")
            print(f"        Semantic Score: {breakdown['semantic_similarity']:.3f}")

def demo_intent_analysis():
    """Demonstrate intent classification and analysis."""
    print("\n\n🧠 Intent Classification Analysis")
    print("=" * 50)
    
    system = QueryUnderstandingSystem()
    
    # Analyze query patterns
    analysis = system.analyze_query_patterns(SAMPLE_QUERIES)
    
    print("Query Pattern Analysis:")
    print(f"Total queries analyzed: {analysis['total_queries']}")
    print(f"Average confidence: {analysis['average_confidence']:.3f}")
    
    print("\nIntent Distribution:")
    for intent, count in sorted(analysis['intent_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / analysis['total_queries']) * 100
        print(f"  {intent}: {count} queries ({percentage:.1f}%)")
    
    if analysis['low_confidence_queries']:
        print(f"\nLow confidence queries ({len(analysis['low_confidence_queries'])}):")
        for query in analysis['low_confidence_queries'][:5]:  # Show first 5
            print(f"  - '{query}'")

def demo_system_stats():
    """Display system statistics and capabilities."""
    print("\n\n📊 System Statistics")
    print("=" * 50)
    
    system = QueryUnderstandingSystem()
    system.load_services(SAMPLE_SERVICES)
    
    stats = system.get_system_stats()
    
    print("System Configuration:")
    for key, value in stats.items():
        if key == "available_intents":
            print(f"  {key}: {len(value)} intents")
            for intent in value:
                print(f"    - {intent}")
        else:
            print(f"  {key}: {value}")

def interactive_demo():
    """Interactive demo where users can input their own queries."""
    print("\n\n💬 Interactive Query Demo")
    print("=" * 50)
    print("Enter your own queries to test the system!")
    print("Type 'quit' to exit, 'help' for sample queries")
    
    system = QueryUnderstandingSystem()
    system.load_services(SAMPLE_SERVICES)
    
    while True:
        query = input("\n🔍 Enter your query: ").strip()
        
        if query.lower() == 'quit':
            break
        elif query.lower() == 'help':
            print("\nSample queries to try:")
            for i, sample in enumerate(SAMPLE_QUERIES[:5], 1):
                print(f"  {i}. {sample}")
            continue
        elif not query:
            continue
        
        try:
            result = system.process_query(query, top_k=5)
            
            print(f"\n📋 Results for: '{query}'")
            print(f"Intent: {result['intent']['intent']} (confidence: {result['intent']['confidence']:.2f})")
            print(f"Found {len(result['results'])} results:")
            
            for i, res in enumerate(result["results"], 1):
                service = res["service"]
                score = res["total_score"]
                print(f"\n  {i}. {service['name']} - Score: {score:.3f}")
                print(f"     {service['description'][:100]}...")
                if service['cuisine_type']:
                    print(f"     Cuisine: {service['cuisine_type']}")
                if service['rating']:
                    print(f"     Rating: {service['rating']}/5.0")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")

if __name__ == "__main__":
    # Run all demos
    demo_basic_functionality()
    demo_personalized_search()
    demo_intent_analysis()
    demo_system_stats()
    
    # Ask if user wants interactive demo
    response = input("\n\nWould you like to try the interactive demo? (y/n): ")
    if response.lower().startswith('y'):
        interactive_demo()
    
    print("\n🎉 Demo completed! Thank you for trying the NLP Query Understanding System.")
