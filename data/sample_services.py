"""Sample service data for testing the query understanding system."""

from src.ranking_pipeline import ServiceItem, UserProfile

# Sample restaurant and hospitality services
SAMPLE_SERVICES = [
    ServiceItem(
        id="rest_001",
        name="Bella Vista Italian",
        description="Authentic Italian restaurant with homemade pasta and wood-fired pizza. Family-owned establishment serving traditional recipes.",
        category="restaurant",
        cuisine_type="Italian",
        price_range=3,
        rating=4.5,
        location=(40.7589, -73.9851),  # NYC coordinates
        features=["outdoor seating", "wine bar", "vegetarian options", "romantic atmosphere"]
    ),
    ServiceItem(
        id="rest_002",
        name="Dragon Palace",
        description="Modern Chinese cuisine with authentic Szechuan dishes and dim sum. Contemporary atmosphere with traditional flavors.",
        category="restaurant",
        cuisine_type="Chinese",
        price_range=2,
        rating=4.2,
        location=(40.7505, -73.9934),
        features=["dim sum", "spicy food", "group dining", "takeout available"]
    ),
    ServiceItem(
        id="rest_003",
        name="Green Garden Cafe",
        description="Organic vegetarian and vegan restaurant focusing on fresh, locally-sourced ingredients. Health-conscious dining.",
        category="restaurant",
        cuisine_type="Vegetarian",
        price_range=2,
        rating=4.3,
        location=(40.7614, -73.9776),
        features=["vegan options", "organic", "gluten free", "healthy", "outdoor seating"]
    ),
    ServiceItem(
        id="rest_004",
        name="Sakura Sushi Bar",
        description="Fresh sushi and sashimi with traditional Japanese preparation. Omakase available with seasonal ingredients.",
        category="restaurant",
        cuisine_type="Japanese",
        price_range=4,
        rating=4.7,
        location=(40.7549, -73.9840),
        features=["sushi bar", "omakase", "fresh fish", "sake selection", "intimate setting"]
    ),
    ServiceItem(
        id="rest_005",
        name="Taco Libre",
        description="Casual Mexican eatery with authentic street tacos, fresh guacamole, and craft margaritas. Lively atmosphere.",
        category="restaurant",
        cuisine_type="Mexican",
        price_range=1,
        rating=4.1,
        location=(40.7282, -74.0776),
        features=["street tacos", "margaritas", "casual dining", "late night", "group friendly"]
    ),
    ServiceItem(
        id="rest_006",
        name="The Steakhouse",
        description="Premium steakhouse serving dry-aged beef and classic American cuisine. Upscale dining experience.",
        category="restaurant",
        cuisine_type="American",
        price_range=4,
        rating=4.6,
        location=(40.7505, -73.9857),
        features=["dry-aged beef", "wine cellar", "fine dining", "business dining", "private rooms"]
    ),
    ServiceItem(
        id="rest_007",
        name="Mumbai Spice",
        description="Authentic Indian restaurant with traditional curries, tandoor specialties, and vegetarian options.",
        category="restaurant",
        cuisine_type="Indian",
        price_range=2,
        rating=4.4,
        location=(40.7411, -73.9897),
        features=["tandoor", "vegetarian options", "spicy food", "lunch buffet", "family friendly"]
    ),
    ServiceItem(
        id="rest_008",
        name="Coastal Seafood",
        description="Fresh seafood restaurant with daily catches, raw bar, and ocean-to-table dining experience.",
        category="restaurant",
        cuisine_type="Seafood",
        price_range=3,
        rating=4.3,
        location=(40.7505, -73.9934),
        features=["fresh seafood", "raw bar", "daily specials", "waterfront view", "sustainable fishing"]
    ),
    ServiceItem(
        id="hotel_001",
        name="Grand Plaza Hotel",
        description="Luxury hotel in downtown with spa services, fine dining restaurant, and business facilities.",
        category="hotel",
        price_range=4,
        rating=4.5,
        location=(40.7549, -73.9840),
        features=["spa", "business center", "fine dining", "concierge", "fitness center"]
    ),
    ServiceItem(
        id="hotel_002",
        name="Boutique Inn",
        description="Charming boutique hotel with personalized service and unique room designs. Pet-friendly accommodation.",
        category="hotel",
        price_range=3,
        rating=4.2,
        location=(40.7614, -73.9776),
        features=["boutique", "pet friendly", "personalized service", "unique design", "continental breakfast"]
    )
]

# Sample user profiles for testing
SAMPLE_USER_PROFILES = [
    UserProfile(
        user_id="user_001",
        preferences={
            "restaurant": 0.8,
            "hotel": 0.3
        },
        location=(40.7589, -73.9851),  # NYC
        dietary_restrictions=["vegetarian"],
        price_range=(1, 3),
        cuisine_preferences=["Italian", "Vegetarian", "Indian"],
        past_queries=["vegetarian restaurants near me", "italian food", "healthy dining options"]
    ),
    UserProfile(
        user_id="user_002",
        preferences={
            "restaurant": 0.9,
            "hotel": 0.7
        },
        location=(40.7505, -73.9934),
        dietary_restrictions=[],
        price_range=(3, 4),
        cuisine_preferences=["Japanese", "American", "Seafood"],
        past_queries=["best sushi in town", "fine dining restaurants", "business lunch spots"]
    ),
    UserProfile(
        user_id="user_003",
        preferences={
            "restaurant": 0.6,
            "hotel": 0.2
        },
        location=(40.7282, -74.0776),
        dietary_restrictions=["gluten free"],
        price_range=(1, 2),
        cuisine_preferences=["Mexican", "Chinese"],
        past_queries=["cheap eats", "gluten free options", "casual dining"]
    )
]

# Sample test queries
SAMPLE_QUERIES = [
    "Find me a good Italian restaurant nearby",
    "I'm looking for vegetarian options for dinner",
    "Best sushi place in the area",
    "Cheap Mexican food for lunch",
    "Fine dining restaurant for business meeting",
    "Restaurants with outdoor seating",
    "Gluten free dining options",
    "Spicy Chinese food delivery",
    "Romantic restaurant for date night",
    "Family friendly restaurants",
    "Late night dining options",
    "Seafood restaurant with fresh fish",
    "Indian restaurant with vegetarian menu",
    "Steakhouse for special occasion",
    "Healthy food options near me"
]
