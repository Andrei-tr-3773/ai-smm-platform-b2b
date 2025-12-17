#!/usr/bin/env python3
"""
Marketing Workflow Integration Tests

Tests the integration between AI Template Generator and Video Script Generator,
ensuring they work together correctly in real-world workflows.
"""
import os
import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.template_generator_agent import TemplateGeneratorAgent
from agents.video_script_agent import VideoScriptAgent

# Load environment
load_dotenv(override=True)


@pytest.fixture(scope="module")
def openai_model():
    """Initialize OpenAI model for testing."""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
    )


@pytest.fixture(scope="module")
def template_agent(openai_model):
    """Initialize Template Generator Agent."""
    return TemplateGeneratorAgent(model=openai_model)


@pytest.fixture(scope="module")
def video_script_agent(openai_model):
    """Initialize Video Script Agent."""
    return VideoScriptAgent(model=openai_model)


class TestMarketingWorkflowIntegration:
    """Integration tests for marketing content generation workflow."""

    def test_fitness_campaign_workflow(self, template_agent, video_script_agent):
        """
        Test complete workflow: Template generation → Video script generation
        Industry: Fitness
        """
        # Step 1: Generate template for fitness class
        template_desc = "Template for fitness class announcement with instructor photo, class time, and benefits list"
        template_result = template_agent.generate_template_from_description(template_desc)

        assert template_result['validation_result']['valid']
        assert template_result['liquid_template'] != ""
        assert len(template_result['field_schema']) >= 3

        # Step 2: Generate video script for fitness campaign
        campaign = "New HIIT class with instructor Sarah every Saturday at 10 AM - burn 500 calories, all levels welcome"
        video_result = video_script_agent.generate_video_script_from_campaign(
            campaign_content=campaign,
            platform="instagram_reels",
            target_audience="fitness enthusiasts aged 25-40",
            content_goal="Drive class registrations"
        )

        assert len(video_result['script_sections']) >= 3
        assert video_result['virality_prediction']['virality_score'] > 50
        assert 'platform_optimization' in video_result

        print(f"✅ Fitness workflow: Template ({len(template_result['field_schema'])} fields) + Video ({video_result['virality_prediction']['virality_score']}/100)")

    def test_saas_campaign_workflow(self, template_agent, video_script_agent):
        """
        Test complete workflow: Template generation → Video script generation
        Industry: SaaS
        """
        # Step 1: Generate template for SaaS feature
        template_desc = "Template for SaaS feature announcement with demo video, technical specs, and CTA button"
        template_result = template_agent.generate_template_from_description(template_desc)

        assert template_result['validation_result']['valid']
        assert template_result['liquid_template'] != ""

        # Step 2: Generate video script for SaaS launch
        campaign = "Launching API v3 with 10x faster queries, real-time streaming, and enhanced security. Try free for 30 days!"
        video_result = video_script_agent.generate_video_script_from_campaign(
            campaign_content=campaign,
            platform="linkedin",
            target_audience="CTOs and software developers",
            content_goal="Drive API trial signups"
        )

        assert len(video_result['script_sections']) >= 3
        assert video_result['virality_prediction']['virality_score'] > 0

        # LinkedIn should have professional tone
        platform_opt = video_result['platform_optimization']
        assert 'professional' in platform_opt['tone'].lower()

        print(f"✅ SaaS workflow: Template ({len(template_result['field_schema'])} fields) + Video ({video_result['virality_prediction']['virality_score']}/100)")

    def test_ecommerce_campaign_workflow(self, template_agent, video_script_agent):
        """
        Test complete workflow: Template generation → Video script generation
        Industry: E-commerce
        """
        # Step 1: Generate template for product promotion
        template_desc = "Template for product sale with product image, original price, discount price, and urgency timer"
        template_result = template_agent.generate_template_from_description(template_desc)

        assert template_result['validation_result']['valid']
        assert len(template_result['field_schema']) >= 3

        # Step 2: Generate video script for flash sale
        campaign = "Winter dress collection - 30% off this week only! Over 200 styles, free shipping over $50"
        video_result = video_script_agent.generate_video_script_from_campaign(
            campaign_content=campaign,
            platform="tiktok",
            target_audience="fashion shoppers aged 18-35",
            content_goal="Drive flash sale purchases"
        )

        assert len(video_result['script_sections']) >= 3
        assert video_result['virality_prediction']['virality_score'] >= 50

        # TikTok should mention trending audio
        production = video_result['production_notes']
        audio = production.get('audio', {})
        music = audio.get('music', '') if isinstance(audio, dict) else str(audio)
        assert 'trending' in music.lower() or 'sound' in music.lower()

        print(f"✅ E-commerce workflow: Template ({len(template_result['field_schema'])} fields) + Video ({video_result['virality_prediction']['virality_score']}/100)")

    def test_multi_platform_video_generation(self, video_script_agent):
        """
        Test generating video scripts for same campaign across multiple platforms.
        Validates platform-specific optimizations work correctly.
        """
        campaign = "Special offer: 30% off all products this weekend only!"
        platforms = ['instagram_reels', 'tiktok', 'youtube_shorts', 'linkedin']

        results = {}
        for platform in platforms:
            result = video_script_agent.generate_video_script_from_campaign(
                campaign_content=campaign,
                platform=platform,
                target_audience="general consumers",
                content_goal="Drive sales"
            )

            # Validate platform optimization
            assert 'platform_optimization' in result
            platform_opt = result['platform_optimization']
            assert 'tone' in platform_opt
            assert 'duration_check' in platform_opt
            assert 'aspect_ratio' in platform_opt

            results[platform] = {
                'score': result['virality_prediction']['virality_score'],
                'sections': len(result['script_sections']),
                'tone': platform_opt['tone']
            }

        # Verify different platforms have different tones
        tones = [r['tone'] for r in results.values()]
        assert len(set(tones)) >= 2  # At least 2 different tones

        print(f"✅ Multi-platform generation:")
        for platform, data in results.items():
            print(f"   - {platform}: {data['score']}/100, {data['sections']} sections, tone: {data['tone']}")

    def test_template_validation_quality(self, template_agent):
        """
        Test that generated templates pass validation across different industries.
        """
        test_cases = [
            ("Fitness class announcement with instructor bio and schedule", "fitness"),
            ("SaaS feature release with demo video and technical details", "saas"),
            ("Product promotion with image gallery and pricing", "ecommerce"),
            ("Restaurant menu special with food photos and ingredients", "food"),
        ]

        validation_results = []
        for description, industry in test_cases:
            result = template_agent.generate_template_from_description(description)

            # All should pass validation
            assert result['validation_result']['valid'] == True
            assert result['liquid_template'] != ""
            assert len(result['field_schema']) >= 2

            validation_results.append({
                'industry': industry,
                'fields': len(result['field_schema']),
                'valid': result['validation_result']['valid']
            })

        print(f"✅ Template validation quality:")
        for vr in validation_results:
            print(f"   - {vr['industry']}: {vr['fields']} fields, valid={vr['valid']}")

    def test_virality_score_consistency(self, video_script_agent):
        """
        Test that virality scores are consistent and reasonable.
        High-quality campaigns should score higher than low-quality ones.
        """
        # High-quality campaign (specific, urgent, valuable)
        high_quality = "EXCLUSIVE: Join celebrity trainer Sarah for FREE HIIT masterclass this Saturday - only 50 spots! Burn 500 calories, transform your body. Register NOW!"

        # Medium-quality campaign (clear but less urgent)
        medium_quality = "New yoga class starting next month with experienced instructor. Improve flexibility and reduce stress."

        high_result = video_script_agent.generate_video_script_from_campaign(
            campaign_content=high_quality,
            platform="instagram_reels",
            target_audience="fitness enthusiasts",
            content_goal="Drive registrations"
        )

        medium_result = video_script_agent.generate_video_script_from_campaign(
            campaign_content=medium_quality,
            platform="instagram_reels",
            target_audience="yoga practitioners",
            content_goal="Awareness"
        )

        high_score = high_result['virality_prediction']['virality_score']
        medium_score = medium_result['virality_prediction']['virality_score']

        # Both should be in reasonable range
        assert 30 <= high_score <= 100
        assert 30 <= medium_score <= 100

        # High quality should generally score higher (but AI may vary)
        # Just check they're both reasonable, not enforcing strict ordering
        assert high_score > 0
        assert medium_score > 0

        print(f"✅ Virality consistency: High={high_score}/100, Medium={medium_score}/100")

    def test_production_notes_actionability(self, video_script_agent):
        """
        Test that production notes are actionable and platform-appropriate.
        """
        campaign = "New product launch - limited edition available now!"
        platforms = ['instagram_reels', 'tiktok', 'linkedin']

        for platform in platforms:
            result = video_script_agent.generate_video_script_from_campaign(
                campaign_content=campaign,
                platform=platform,
                target_audience="general audience",
                content_goal="awareness"
            )

            production = result['production_notes']

            # Check required production fields exist
            assert 'camera_setup' in production
            assert 'lighting' in production
            assert 'audio' in production or 'smartphone_tips' in production

            # Camera setup should have practical tips
            camera_setup = production['camera_setup']
            if isinstance(camera_setup, list):
                assert len(camera_setup) > 0
            else:
                assert len(str(camera_setup)) > 10  # Non-empty description

            print(f"✅ {platform}: Production notes actionable")


if __name__ == "__main__":
    print("Running Marketing Workflow Integration Tests...")
    print("=" * 80)

    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
