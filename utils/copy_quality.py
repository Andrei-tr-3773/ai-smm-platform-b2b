"""
Copy Quality Check Utilities - Analyze and improve marketing copy quality.
"""

from typing import Dict, List, Any
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


def check_tone_consistency(
    text: str,
    target_tone: str = "professional"
) -> Dict[str, Any]:
    """
    Check if copy matches target tone.

    Args:
        text: Copy text to analyze
        target_tone: Target tone (professional, casual, persuasive, educational)

    Returns:
        Dict with score, issues, and suggestions
    """
    # Tone indicators
    tone_indicators = {
        "professional": {
            "good_words": ["innovative", "solution", "optimize", "enhance", "streamline", "expertise"],
            "bad_words": ["awesome", "cool", "hey", "gonna", "wanna", "yeah"],
            "formality": "high"
        },
        "casual": {
            "good_words": ["hey", "awesome", "cool", "easy", "simple", "quick"],
            "bad_words": ["hereby", "pursuant", "aforementioned", "heretofore"],
            "formality": "low"
        },
        "persuasive": {
            "good_words": ["proven", "guaranteed", "results", "transform", "breakthrough", "exclusive"],
            "bad_words": ["maybe", "might", "possibly", "perhaps", "uncertain"],
            "formality": "medium"
        },
        "educational": {
            "good_words": ["learn", "discover", "understand", "guide", "tutorial", "step-by-step"],
            "bad_words": ["buy now", "limited time", "act fast", "don't miss"],
            "formality": "medium"
        }
    }

    target = tone_indicators.get(target_tone, tone_indicators["professional"])
    text_lower = text.lower()

    # Count good and bad words
    good_count = sum(1 for word in target["good_words"] if word in text_lower)
    bad_count = sum(1 for word in target["bad_words"] if word in text_lower)

    # Check sentence structure
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

    # Calculate score
    base_score = 100
    penalties = []

    if bad_count > 0:
        penalty = bad_count * 15
        base_score -= penalty
        penalties.append(f"Contains {bad_count} words inappropriate for {target_tone} tone")

    # Formality check
    if target["formality"] == "high" and avg_sentence_length < 10:
        base_score -= 10
        penalties.append("Sentences too short for professional tone (aim for 12-20 words)")

    if target["formality"] == "low" and avg_sentence_length > 25:
        base_score -= 10
        penalties.append("Sentences too long for casual tone (aim for 8-15 words)")

    # Suggestions
    suggestions = []

    if good_count == 0:
        suggestions.append(f"Add power words for {target_tone} tone: {', '.join(target['good_words'][:3])}")

    if bad_count > 0:
        suggestions.append(f"Remove inappropriate words: {', '.join([w for w in target['bad_words'] if w in text_lower])}")

    # Check for contractions
    has_contractions = any(c in text for c in ["don't", "can't", "won't", "it's", "you're"])

    if target["formality"] == "high" and has_contractions:
        suggestions.append("Use full words instead of contractions for professional tone")
    elif target["formality"] == "low" and not has_contractions:
        suggestions.append("Add contractions for more casual, friendly tone")

    return {
        "score": max(0, min(100, base_score)),
        "issues": penalties if penalties else ["No major issues"],
        "suggestions": suggestions if suggestions else ["Tone is consistent"],
        "tone": target_tone,
        "avg_sentence_length": round(avg_sentence_length, 1)
    }


def detect_repetition(text: str, threshold: int = 3) -> Dict[str, Any]:
    """
    Detect repeated words and phrases in copy.

    Args:
        text: Copy text to analyze
        threshold: Max times a word should appear (default 3)

    Returns:
        Dict with repetitive words, score, and suggestions
    """
    # Tokenize (simple word split)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())  # Words 4+ chars

    # Count word frequency
    word_counts = Counter(words)

    # Common words to ignore
    stop_words = {
        'that', 'this', 'with', 'from', 'have', 'will', 'would',
        'could', 'should', 'your', 'their', 'about', 'when', 'where',
        'what', 'which', 'some', 'other', 'than', 'then', 'more'
    }

    # Find repetitive words (excluding stop words)
    repetitive = {
        word: count
        for word, count in word_counts.items()
        if count > threshold and word not in stop_words
    }

    # Calculate score
    if not repetitive:
        score = 100
    else:
        # Penalty: 10 points per repetitive word
        score = max(0, 100 - (len(repetitive) * 10))

    # Suggestions
    suggestions = []
    for word, count in sorted(repetitive.items(), key=lambda x: x[1], reverse=True):
        # Suggest synonyms (simple heuristic)
        synonyms = _suggest_synonyms(word)
        suggestions.append(
            f"'{word}' used {count}x - consider: {', '.join(synonyms)}"
        )

    return {
        "repetitive_words": repetitive,
        "score": score,
        "suggestions": suggestions if suggestions else ["No repetitive words detected"],
        "total_words": len(words),
        "unique_words": len(word_counts)
    }


def _suggest_synonyms(word: str) -> List[str]:
    """
    Simple synonym suggestions (basic mapping).

    In production, could integrate with thesaurus API or word embeddings.
    """
    synonym_map = {
        "create": ["generate", "build", "produce", "design"],
        "make": ["create", "build", "produce", "craft"],
        "help": ["assist", "support", "aid", "guide"],
        "use": ["utilize", "employ", "leverage", "apply"],
        "get": ["obtain", "acquire", "receive", "gain"],
        "good": ["excellent", "great", "outstanding", "quality"],
        "fast": ["quick", "rapid", "swift", "speedy"],
        "easy": ["simple", "effortless", "straightforward", "intuitive"],
        "best": ["top", "leading", "premier", "superior"],
        "new": ["fresh", "innovative", "modern", "latest"]
    }

    return synonym_map.get(word, ["alternative", "variation", "different word"])


def check_readability(text: str) -> Dict[str, Any]:
    """
    Check readability score (Flesch Reading Ease approximation).

    Args:
        text: Copy text to analyze

    Returns:
        Dict with readability score and grade level
    """
    # Count sentences
    sentences = len(re.findall(r'[.!?]+', text))
    if sentences == 0:
        sentences = 1

    # Count words
    words = len(re.findall(r'\b\w+\b', text))
    if words == 0:
        return {"score": 0, "grade": "N/A", "rating": "N/A"}

    # Count syllables (approximation)
    syllables = sum(_count_syllables(word) for word in re.findall(r'\b\w+\b', text.lower()))

    # Flesch Reading Ease Formula
    # 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    score = max(0, min(100, score))

    # Grade level and rating
    if score >= 90:
        grade = "5th grade"
        rating = "Very Easy"
    elif score >= 80:
        grade = "6th grade"
        rating = "Easy"
    elif score >= 70:
        grade = "7th grade"
        rating = "Fairly Easy"
    elif score >= 60:
        grade = "8-9th grade"
        rating = "Standard"
    elif score >= 50:
        grade = "10-12th grade"
        rating = "Fairly Difficult"
    elif score >= 30:
        grade = "College"
        rating = "Difficult"
    else:
        grade = "Graduate"
        rating = "Very Difficult"

    return {
        "score": round(score, 1),
        "grade": grade,
        "rating": rating,
        "words": words,
        "sentences": sentences,
        "avg_words_per_sentence": round(words / sentences, 1),
        "recommendation": "Aim for 60-70 for marketing copy (8-9th grade level)"
    }


def _count_syllables(word: str) -> int:
    """
    Count syllables in a word (approximation).

    Args:
        word: Word to count syllables

    Returns:
        Number of syllables
    """
    vowels = 'aeiouy'
    word = word.lower()
    count = 0
    prev_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith('e'):
        count = max(1, count - 1)

    # Every word has at least one syllable
    return max(1, count)


def check_cta_strength(text: str) -> Dict[str, Any]:
    """
    Check call-to-action strength.

    Args:
        text: Copy text to analyze

    Returns:
        Dict with CTA score and suggestions
    """
    text_lower = text.lower()

    # CTA indicators
    action_verbs = [
        "start", "get", "try", "join", "discover", "learn",
        "download", "sign up", "register", "subscribe", "buy",
        "shop", "order", "claim", "unlock", "access"
    ]

    urgency_words = [
        "now", "today", "immediately", "limited", "exclusive",
        "don't miss", "hurry", "fast", "quick", "instant"
    ]

    # Check for action verbs
    has_action = any(verb in text_lower for verb in action_verbs)

    # Check for urgency
    has_urgency = any(word in text_lower for word in urgency_words)

    # Check for exclamation mark
    has_excitement = "!" in text

    # Calculate score
    score = 0
    if has_action:
        score += 40
    if has_urgency:
        score += 30
    if has_excitement:
        score += 30

    # Suggestions
    suggestions = []
    if not has_action:
        suggestions.append(f"Add action verb: {', '.join(action_verbs[:5])}")
    if not has_urgency:
        suggestions.append(f"Add urgency: {', '.join(urgency_words[:5])}")
    if not has_excitement:
        suggestions.append("Consider adding exclamation mark for emphasis")

    return {
        "score": score,
        "has_action_verb": has_action,
        "has_urgency": has_urgency,
        "has_excitement": has_excitement,
        "suggestions": suggestions if suggestions else ["CTA is strong"],
        "rating": "Strong" if score >= 70 else "Moderate" if score >= 40 else "Weak"
    }


def analyze_copy_comprehensively(text: str, target_tone: str = "professional") -> Dict[str, Any]:
    """
    Run all quality checks on copy.

    Args:
        text: Copy text to analyze
        target_tone: Target tone for consistency check

    Returns:
        Dict with all quality metrics
    """
    return {
        "tone": check_tone_consistency(text, target_tone),
        "repetition": detect_repetition(text),
        "readability": check_readability(text),
        "cta": check_cta_strength(text),
        "overall_score": _calculate_overall_score(text, target_tone)
    }


def _calculate_overall_score(text: str, target_tone: str) -> int:
    """Calculate overall quality score (0-100)."""
    tone = check_tone_consistency(text, target_tone)
    repetition = detect_repetition(text)
    readability = check_readability(text)
    cta = check_cta_strength(text)

    # Weighted average
    overall = (
        tone["score"] * 0.25 +
        repetition["score"] * 0.25 +
        min(100, readability["score"] * 1.5) * 0.25 +  # Normalize readability
        cta["score"] * 0.25
    )

    return round(overall)
