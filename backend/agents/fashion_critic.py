"""
OutfitCheck AI - Agent 2: Fashion Critic Agent
Uses Groq (Llama 3.3 70B) to provide detailed fashion feedback
on outfit combinations selected by the user.

This agent demonstrates AGENTIC behavior through:
1. Persona-based reasoning: acts as a professional fashion critic
2. Structured evaluation: scores across multiple dimensions
3. Memory: considers previous feedback history for consistent advice
4. Actionable output: provides specific improvement suggestions
"""
import json
from groq import Groq
from backend.config import GROQ_API_KEY

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

CRITIC_SYSTEM_PROMPT = """You are OutfitCheck AI's Fashion Critic Agent — a renowned fashion critic 
with deep knowledge of style, color theory, trends, and occasion-appropriate dressing.

Your personality: Direct but encouraging. You give honest feedback but always include 
constructive suggestions. Think of yourself as a supportive but truthful friend who 
happens to be a fashion expert.

EVALUATION CRITERIA:
1. Color Harmony (do the colors work together?)
2. Style Coherence (does the outfit tell a consistent style story?)
3. Occasion Appropriateness (is it suitable for the intended occasion?)
4. Seasonal Suitability (is it appropriate for the weather/season?)
5. Overall Impact (does this outfit make a statement?)

SCORING: Use a 1-10 scale where:
- 1-3: Needs significant changes
- 4-5: Below average, several issues
- 6-7: Good, minor improvements possible
- 8-9: Excellent, very well put together
- 10: Perfect, wouldn't change a thing

OUTPUT FORMAT - Return ONLY valid JSON:
{
    "overall_score": 7.5,
    "color_harmony": "Detailed analysis of color combinations...",
    "color_score": 8,
    "style_coherence": "Analysis of style consistency...",
    "style_score": 7,
    "occasion_fit": "How well it fits the occasion...",
    "occasion_score": 8,
    "seasonal_fit": "Weather/season appropriateness...",
    "seasonal_score": 7,
    "improvements": [
        "Specific actionable suggestion 1",
        "Specific actionable suggestion 2"
    ],
    "highlights": [
        "What works really well 1",
        "What works really well 2"
    ],
    "vibe": "2-4 word vibe/aesthetic description",
    "celebrity_match": "A celebrity or style icon who might wear this",
    "verdict": "A fun, memorable one-sentence verdict"
}
"""


async def critique_outfit(
    outfit_items: list[dict],
    occasion: str = "casual",
    weather_context: str = "",
    previous_feedback: list[dict] = None
) -> dict:
    """
    Generate a detailed fashion critique for an outfit combination.
    
    This is the main agentic function that:
    1. Builds context from outfit items and occasion
    2. Includes previous feedback for consistency (memory)
    3. Generates multi-dimensional evaluation
    4. Returns structured, actionable feedback
    
    Args:
        outfit_items: List of garment dicts in the outfit
        occasion: Type of occasion
        weather_context: Current weather description
        previous_feedback: List of previous feedback for this user
    
    Returns:
        Dict with scores, analysis, and suggestions
    """
    # Format outfit description
    outfit_text = _format_outfit(outfit_items)

    if not outfit_items:
        return _empty_feedback()

    # Build context prompt
    context_parts = [f"OUTFIT TO CRITIQUE:\n{outfit_text}"]
    context_parts.append(f"\nINTENDED OCCASION: {occasion}")

    if weather_context:
        context_parts.append(f"\nWEATHER CONTEXT: {weather_context}")

    # Include previous feedback for consistency (agent memory)
    if previous_feedback:
        prev_text = _format_previous_feedback(previous_feedback[-3:])  # Last 3
        context_parts.append(f"\nPREVIOUS FEEDBACK GIVEN TO THIS USER (for consistency):\n{prev_text}")

    user_prompt = "\n".join(context_parts)
    user_prompt += "\n\nPlease provide your detailed fashion critique as valid JSON."

    # Call Groq API (Llama 3.3 70B)
    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        response_text = chat_completion.choices[0].message.content
        result = json.loads(response_text)

        # Ensure all expected fields exist
        return _validate_feedback(result)

    except Exception as e:
        return {
            "overall_score": 0,
            "color_harmony": "Unable to analyze",
            "color_score": 0,
            "style_coherence": "Unable to analyze",
            "style_score": 0,
            "occasion_fit": "Unable to analyze",
            "occasion_score": 0,
            "seasonal_fit": "Unable to analyze",
            "seasonal_score": 0,
            "improvements": ["Please try again later"],
            "highlights": [],
            "vibe": "Unknown",
            "celebrity_match": "Unknown",
            "verdict": f"The Fashion Critic encountered an issue: {str(e)}",
            "error": str(e)
        }


async def quick_style_tip(item_description: str) -> str:
    """
    Generate a quick styling tip for a single garment.
    Lightweight call for individual item pages.
    """
    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fashion expert. Give a brief, helpful styling tip in 1-2 sentences."
                },
                {
                    "role": "user",
                    "content": f"Give me a quick styling tip for: {item_description}"
                }
            ],
            temperature=0.7,
            max_tokens=100,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception:
        return "This is a versatile piece that can be styled in many ways!"


def _format_outfit(items: list[dict]) -> str:
    """Format outfit items into readable text for the AI."""
    if not items:
        return "No items provided."

    lines = []
    for item in items:
        lines.append(
            f"- {item.get('name', 'Unknown')} "
            f"({item.get('category', 'unknown')}) — "
            f"Color: {item.get('color', 'unknown')}, "
            f"Style: {item.get('occasion', 'casual')}, "
            f"Season: {item.get('season', 'all')}"
        )
    return "\n".join(lines)


def _format_previous_feedback(feedback_list: list[dict]) -> str:
    """Format previous feedback for context."""
    lines = []
    for fb in feedback_list:
        score = fb.get("output_data", {}).get("overall_score", "?")
        verdict = fb.get("output_data", {}).get("verdict", "No verdict")
        lines.append(f"- Score: {score}/10 — {verdict}")
    return "\n".join(lines) if lines else "No previous feedback."


def _validate_feedback(result: dict) -> dict:
    """Ensure all expected fields exist in the feedback."""
    defaults = {
        "overall_score": 5.0,
        "color_harmony": "Not analyzed",
        "color_score": 5,
        "style_coherence": "Not analyzed",
        "style_score": 5,
        "occasion_fit": "Not analyzed",
        "occasion_score": 5,
        "seasonal_fit": "Not analyzed",
        "seasonal_score": 5,
        "improvements": [],
        "highlights": [],
        "vibe": "Classic",
        "celebrity_match": "Unknown",
        "verdict": "A decent outfit overall!"
    }

    for key, default in defaults.items():
        if key not in result:
            result[key] = default

    return result


def _empty_feedback() -> dict:
    """Return empty feedback when no items are provided."""
    return {
        "overall_score": 0,
        "color_harmony": "No outfit to analyze",
        "color_score": 0,
        "style_coherence": "No outfit to analyze",
        "style_score": 0,
        "occasion_fit": "No outfit to analyze",
        "occasion_score": 0,
        "seasonal_fit": "No outfit to analyze",
        "seasonal_score": 0,
        "improvements": ["Add items to your outfit to get feedback"],
        "highlights": [],
        "vibe": "Empty",
        "celebrity_match": "N/A",
        "verdict": "Add some items to your outfit first!"
    }
