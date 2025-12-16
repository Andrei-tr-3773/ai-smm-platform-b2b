#!/usr/bin/env python3
"""
Test script for Viral Patterns Database

Validates ViralPatternsDB functionality and pattern quality.
"""
from utils.viral_patterns import ViralPatternsDB

print("Testing Viral Patterns Database")
print("=" * 80)

# Initialize database
db = ViralPatternsDB()

# Test 1: Get all patterns
print("\n[Test 1] Get All Patterns")
print("-" * 80)
all_patterns = db.get_all_patterns()
print(f"✅ Loaded {len(all_patterns)} patterns")
assert len(all_patterns) == 30, f"Expected 30 patterns, got {len(all_patterns)}"

# Test 2: Get pattern by ID
print("\n[Test 2] Get Pattern by ID")
print("-" * 80)
pattern = db.get_pattern_by_id("curiosity_hook")
if pattern:
    print(f"✅ Found pattern: {pattern['name']}")
    print(f"   Platforms: {', '.join(pattern['platform'])}")
    print(f"   Success Rate: {pattern['success_rate']:.1%}")
    print(f"   Best For: {', '.join(pattern['best_for'])}")
else:
    print("❌ Pattern not found")
    assert False, "curiosity_hook pattern should exist"

# Test 3: Find patterns by platform
print("\n[Test 3] Find Patterns by Platform")
print("-" * 80)
platforms = ["instagram_reels", "tiktok", "youtube_shorts", "facebook_video", "linkedin"]

for platform in platforms:
    patterns = db.find_patterns_by_platform(platform)
    print(f"   {platform}: {len(patterns)} patterns")

instagram_patterns = db.find_patterns_by_platform("instagram_reels")
assert len(instagram_patterns) > 0, "Should have Instagram patterns"
print(f"✅ Instagram has {len(instagram_patterns)} patterns")

# Test 4: Find best patterns for content type + platform
print("\n[Test 4] Find Best Patterns (Content Type + Platform)")
print("-" * 80)

test_cases = [
    ("announcement", "instagram_reels"),
    ("tutorial", "youtube_shorts"),
    ("promotion", "facebook_video"),
    ("testimonial", "linkedin"),
    ("transformation", "tiktok")
]

for content_type, platform in test_cases:
    patterns = db.find_best_patterns(content_type, platform, top_n=3)
    print(f"\n   {content_type.capitalize()} on {platform}:")
    if patterns:
        for i, p in enumerate(patterns, 1):
            print(f"      {i}. {p['name']} ({p['success_rate']:.1%})")
    else:
        print(f"      No patterns found")

assert len(db.find_best_patterns("announcement", "instagram_reels")) > 0, "Should find patterns"
print("\n✅ find_best_patterns() working correctly")

# Test 5: Find patterns by industry
print("\n[Test 5] Find Patterns by Industry")
print("-" * 80)

industries = ["fitness", "saas", "ecommerce", "education", "food"]

for industry in industries:
    patterns = db.find_patterns_by_industry(industry, platform="instagram_reels")
    print(f"   {industry.capitalize()}: {len(patterns)} patterns for Instagram")

fitness_patterns = db.find_patterns_by_industry("fitness")
assert len(fitness_patterns) > 0, "Should have fitness patterns"
print(f"\n✅ Found {len(fitness_patterns)} patterns for fitness industry")

# Test 6: Get pattern stats
print("\n[Test 6] Pattern Statistics")
print("-" * 80)

stats = db.get_pattern_stats()
print(f"   Total Patterns: {stats['total_patterns']}")
print(f"   Average Success Rate: {stats['avg_success_rate']:.1%}")
print(f"   Average Views: {stats['avg_views']:,}")
print(f"   Platforms: {len(stats['platforms'])}")
print(f"   Content Categories: {len(stats['content_categories'])}")
if stats['top_pattern']:
    print(f"   Top Pattern: {stats['top_pattern']['name']} ({stats['top_pattern']['success_rate']:.1%})")

assert stats['total_patterns'] == 30, "Should have 30 patterns"
assert stats['avg_success_rate'] > 0, "Should have positive success rate"
print("\n✅ Statistics calculated correctly")

# Test 7: Platform recommendations
print("\n[Test 7] Platform Recommendations")
print("-" * 80)

recommendations = db.get_platform_recommendations("announcement")
print(f"   Recommendations for 'announcement' content:")
for platform, patterns in recommendations.items():
    print(f"\n   {platform}:")
    for i, p in enumerate(patterns[:2], 1):  # Show top 2
        print(f"      {i}. {p['name']} ({p['success_rate']:.1%})")

assert len(recommendations) > 0, "Should have recommendations"
print(f"\n✅ Generated recommendations for {len(recommendations)} platforms")

# Test 8: Search patterns
print("\n[Test 8] Search Patterns")
print("-" * 80)

search_queries = ["transformation", "tutorial", "testimonial", "announcement"]

for query in search_queries:
    results = db.search_patterns(query)
    print(f"   '{query}': {len(results)} matches")

transformation_results = db.search_patterns("transformation")
assert len(transformation_results) > 0, "Should find transformation patterns"
print(f"\n✅ Search working correctly")

# Test 9: Validate pattern structure
print("\n[Test 9] Validate Pattern Structure")
print("-" * 80)

required_fields = ['id', 'name', 'platform', 'pattern', 'success_rate', 'avg_views', 'best_for']
valid_count = 0

for pattern in all_patterns:
    # Check required fields
    has_all_fields = all(field in pattern for field in required_fields)
    if has_all_fields:
        valid_count += 1
    else:
        missing = [field for field in required_fields if field not in pattern]
        print(f"   ⚠️  Pattern '{pattern.get('name', 'Unknown')}' missing fields: {missing}")

print(f"   ✅ {valid_count}/{len(all_patterns)} patterns have all required fields")
assert valid_count == len(all_patterns), "All patterns should have required fields"

# Test 10: Validate success rates and views
print("\n[Test 10] Validate Metrics")
print("-" * 80)

success_rates = [p['success_rate'] for p in all_patterns]
avg_views = [p['avg_views'] for p in all_patterns]

# Check ranges
valid_success = all(0 <= rate <= 1 for rate in success_rates)
valid_views = all(views > 0 for views in avg_views)

print(f"   Success rates range: {min(success_rates):.1%} - {max(success_rates):.1%}")
print(f"   Avg views range: {min(avg_views):,} - {max(avg_views):,}")

assert valid_success, "Success rates should be between 0 and 1"
assert valid_views, "Avg views should be positive"
print("   ✅ All metrics valid")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✅ All tests passed!")
print(f"\n📊 Database Stats:")
print(f"   - {len(all_patterns)} viral patterns")
print(f"   - {len(stats['platforms'])} platforms")
print(f"   - {len(stats['content_categories'])} content categories")
print(f"   - Average success rate: {stats['avg_success_rate']:.1%}")
print(f"   - Top pattern: {stats['top_pattern']['name']} ({stats['top_pattern']['success_rate']:.1%})")
print("\n🎉 Viral Patterns Database is ready for Video Script Generator!")
