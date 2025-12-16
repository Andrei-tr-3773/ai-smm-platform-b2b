#!/usr/bin/env python3
"""
Seed script to load viral patterns into MongoDB

Usage:
    poetry run python seed_viral_patterns.py
"""
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(override=True)

def seed_viral_patterns():
    """Load viral patterns from JSON file into MongoDB."""
    try:
        # Connect to MongoDB
        connection_string = os.getenv("CONNECTION_STRING_MONGO")
        if not connection_string:
            raise ValueError("CONNECTION_STRING_MONGO not found in environment variables")

        client = MongoClient(connection_string)
        db = client.get_database()
        collection = db.viral_patterns

        # Load patterns from JSON file
        patterns_file = "data/viral_patterns.json"
        with open(patterns_file, 'r') as f:
            patterns = json.load(f)

        # Add metadata to each pattern
        for pattern in patterns:
            pattern['created_at'] = datetime.now()
            pattern['updated_at'] = datetime.now()
            pattern['usage_count'] = 0  # Track how often pattern is used

        # Clear existing patterns (fresh seed)
        deleted_count = collection.delete_many({}).deleted_count
        print(f"🗑️  Deleted {deleted_count} existing patterns")

        # Insert new patterns
        result = collection.insert_many(patterns)
        print(f"✅ Seeded {len(result.inserted_ids)} viral patterns into MongoDB")

        # Create indexes for better query performance
        collection.create_index("id", unique=True)
        collection.create_index("platform")
        collection.create_index("success_rate")
        collection.create_index("best_for")
        print("📊 Created indexes: id, platform, success_rate, best_for")

        # Display statistics
        print("\n📈 Pattern Statistics:")
        total = collection.count_documents({})
        print(f"   Total patterns: {total}")

        # Platform breakdown
        platforms = collection.distinct("platform")
        print(f"\n   Platforms covered: {len(platforms)}")
        for platform in platforms:
            count = collection.count_documents({"platform": platform})
            print(f"      - {platform}: {count} patterns")

        # Success rate stats
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_success_rate": {"$avg": "$success_rate"},
                "max_success_rate": {"$max": "$success_rate"},
                "min_success_rate": {"$min": "$success_rate"}
            }}
        ]
        stats = list(collection.aggregate(pipeline))
        if stats:
            print(f"\n   Success Rate:")
            print(f"      - Average: {stats[0]['avg_success_rate']:.2%}")
            print(f"      - Highest: {stats[0]['max_success_rate']:.2%}")
            print(f"      - Lowest: {stats[0]['min_success_rate']:.2%}")

        # Top patterns
        print(f"\n   🏆 Top 5 Patterns by Success Rate:")
        top_patterns = collection.find().sort("success_rate", -1).limit(5)
        for i, pattern in enumerate(top_patterns, 1):
            print(f"      {i}. {pattern['name']} ({pattern['success_rate']:.1%}) - {', '.join(pattern['platform'][:2])}")

        print("\n🎉 Viral patterns database seeded successfully!")
        return True

    except FileNotFoundError:
        print(f"❌ Error: {patterns_file} not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🌱 Seeding Viral Patterns Database...")
    print("=" * 60)
    success = seed_viral_patterns()
    exit(0 if success else 1)
