# viral_patterns.py
"""
Viral Patterns Database utilities

Provides access to viral video patterns for different platforms and content types.
"""
import json
from typing import Dict, List, Optional
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ViralPatternsDB:
    """Database interface for viral video patterns."""

    def __init__(self, patterns_file: str = None):
        """
        Initialize viral patterns database.

        Args:
            patterns_file: Path to viral_patterns.json (defaults to data/viral_patterns.json)
        """
        if patterns_file is None:
            # Default to data/viral_patterns.json in project root
            project_root = Path(__file__).parent.parent
            patterns_file = project_root / "data" / "viral_patterns.json"

        try:
            with open(patterns_file, 'r') as f:
                self.patterns = json.load(f)
            logger.info(f"Loaded {len(self.patterns)} viral patterns from {patterns_file}")
        except FileNotFoundError:
            logger.error(f"Viral patterns file not found: {patterns_file}")
            self.patterns = []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing viral patterns JSON: {e}")
            self.patterns = []

    def get_all_patterns(self) -> List[Dict]:
        """Get all viral patterns."""
        return self.patterns

    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict]:
        """
        Get specific viral pattern by ID.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Pattern dict or None if not found
        """
        for pattern in self.patterns:
            if pattern['id'] == pattern_id:
                logger.info(f"Found pattern: {pattern['name']} (id: {pattern_id})")
                return pattern

        logger.warning(f"Pattern not found: {pattern_id}")
        return None

    def find_patterns_by_platform(self, platform: str) -> List[Dict]:
        """
        Find all patterns compatible with a specific platform.

        Args:
            platform: Platform name (instagram_reels, tiktok, youtube_shorts, facebook_video, linkedin)

        Returns:
            List of matching patterns sorted by success_rate
        """
        matching = [p for p in self.patterns if platform in p['platform']]
        matching.sort(key=lambda p: p['success_rate'], reverse=True)

        logger.info(f"Found {len(matching)} patterns for platform: {platform}")
        return matching

    def find_best_patterns(
        self,
        content_type: str,
        platform: str,
        top_n: int = 3
    ) -> List[Dict]:
        """
        Find best viral patterns for content type and platform.

        Args:
            content_type: Content category (announcement, tutorial, promotion, transformation, etc.)
            platform: Platform name (instagram_reels, tiktok, youtube_shorts, etc.)
            top_n: Number of top patterns to return

        Returns:
            List of best-matching patterns sorted by success_rate
        """
        # First filter by platform
        platform_matches = [p for p in self.patterns if platform in p['platform']]

        # Then filter by content type in best_for
        content_matches = []
        for pattern in platform_matches:
            best_for = pattern.get('best_for', [])

            # Check if content_type matches any best_for category
            # Use fuzzy matching for flexibility
            if any(content_type.lower() in category.lower() or category.lower() in content_type.lower()
                   for category in best_for):
                content_matches.append(pattern)

        # If no exact matches, return top platform matches
        if not content_matches:
            logger.info(f"No exact content_type matches for '{content_type}', returning top platform patterns")
            content_matches = platform_matches

        # Sort by success_rate
        content_matches.sort(key=lambda p: p['success_rate'], reverse=True)

        top_patterns = content_matches[:top_n]
        logger.info(
            f"Found {len(top_patterns)} best patterns for platform={platform}, content_type={content_type}"
        )

        return top_patterns

    def find_patterns_by_industry(self, industry: str, platform: str = None) -> List[Dict]:
        """
        Find patterns suitable for a specific industry.

        Args:
            industry: Industry name (fitness, saas, ecommerce, education, food, etc.)
            platform: Optional platform filter

        Returns:
            List of matching patterns
        """
        # Map industry to typical content types
        industry_content_map = {
            'fitness': ['fitness', 'transformation', 'testimonial', 'tutorial'],
            'saas': ['saas', 'education', 'explainer', 'announcement'],
            'ecommerce': ['product_demo', 'promotion', 'unboxing', 'testimonial'],
            'education': ['tutorial', 'education', 'explainer', 'tips'],
            'food': ['recipes', 'process', 'tutorial', 'makeover'],
            'consulting': ['education', 'expertise', 'thought_leadership', 'tips'],
            'generic': []  # All patterns
        }

        relevant_content_types = industry_content_map.get(industry.lower(), [])

        # Filter patterns
        matches = []
        for pattern in self.patterns:
            # Check platform if specified
            if platform and platform not in pattern['platform']:
                continue

            # Check if pattern fits industry
            best_for = pattern.get('best_for', [])
            if industry.lower() == 'generic':
                matches.append(pattern)
            elif any(content in best_for for content in relevant_content_types):
                matches.append(pattern)

        # Sort by success_rate
        matches.sort(key=lambda p: p['success_rate'], reverse=True)

        logger.info(f"Found {len(matches)} patterns for industry: {industry}")
        return matches

    def get_pattern_stats(self) -> Dict:
        """
        Get statistics about the patterns database.

        Returns:
            Dict with pattern statistics
        """
        if not self.patterns:
            return {
                'total_patterns': 0,
                'platforms': [],
                'avg_success_rate': 0,
                'avg_views': 0,
                'content_categories': []
            }

        # Collect platforms
        platforms = set()
        for pattern in self.patterns:
            platforms.update(pattern['platform'])

        # Collect content categories
        categories = set()
        for pattern in self.patterns:
            categories.update(pattern.get('best_for', []))

        # Calculate averages
        success_rates = [p['success_rate'] for p in self.patterns]
        avg_views = [p['avg_views'] for p in self.patterns]

        stats = {
            'total_patterns': len(self.patterns),
            'platforms': sorted(list(platforms)),
            'avg_success_rate': sum(success_rates) / len(success_rates) if success_rates else 0,
            'avg_views': sum(avg_views) / len(avg_views) if avg_views else 0,
            'content_categories': sorted(list(categories)),
            'top_pattern': max(self.patterns, key=lambda p: p['success_rate']) if self.patterns else None
        }

        return stats

    def get_platform_recommendations(self, content_type: str) -> Dict[str, List[Dict]]:
        """
        Get pattern recommendations for all platforms for a given content type.

        Args:
            content_type: Content category

        Returns:
            Dict mapping platform names to lists of recommended patterns
        """
        platforms = ['instagram_reels', 'tiktok', 'youtube_shorts', 'facebook_video', 'linkedin']

        recommendations = {}
        for platform in platforms:
            patterns = self.find_best_patterns(content_type, platform, top_n=3)
            if patterns:
                recommendations[platform] = patterns

        logger.info(f"Generated recommendations for {len(recommendations)} platforms")
        return recommendations

    def search_patterns(self, query: str) -> List[Dict]:
        """
        Search patterns by keyword in name, best_for, or pattern sections.

        Args:
            query: Search query string

        Returns:
            List of matching patterns
        """
        query_lower = query.lower()
        matches = []

        for pattern in self.patterns:
            # Search in name
            if query_lower in pattern['name'].lower():
                matches.append(pattern)
                continue

            # Search in best_for
            if any(query_lower in category.lower() for category in pattern.get('best_for', [])):
                matches.append(pattern)
                continue

            # Search in pattern section templates
            for section in pattern.get('pattern', {}).values():
                if isinstance(section, dict):
                    template = section.get('template', '')
                    if query_lower in template.lower():
                        matches.append(pattern)
                        break

        logger.info(f"Search '{query}' found {len(matches)} patterns")
        return matches
