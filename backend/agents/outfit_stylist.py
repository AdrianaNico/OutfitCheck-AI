"""
OutfitCheck AI - Agent 1: Outfit Stylist Agent
Uses Google Gemini 1.5 Flash to generate outfit suggestions
based on the user's wardrobe, weather conditions, and occasion.

This agent demonstrates AGENTIC behavior through:
1. Tool use: calls weather API and wardrobe database
2. Multi-step reasoning: analyzes context → filters wardrobe → generates combinations
3. Structured output: returns actionable outfit suggestions
"""
import json
from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY
from backend.services.weather import get_weather

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

STYLIST_SYSTEM_PROMPT = """You are OutfitCheck AI's Outfit Stylist Agent — a professional fashion stylist 
with expertise in color theory, seasonal fashion, and occasion-appropriate dressing.

Your role is to create complete outfit combinations from the user's EXISTING wardrobe items.

RULES:
1. ONLY suggest items that exist in the user's wardrobe (provided below)
2. Each outfit MUST include at least a top and bottom (or a dress)
3. Consider weather conditions for practical suggestions
4. Consider the occasion for style appropriateness
5. Suggest 2-3 complete outfits
6. Explain WHY each combination works

OUTPUT FORMAT - Return ONLY valid JSON:
{
    "outfits": [
        {
            "name": "Creative outfit name",
            "items": ["item_id_1", "item_id_2", "item_id_3"],
            "item_names": ["Blue Cotton T-Shirt", "Black Jeans", "White Sneakers"],
            "reasoning": "Why this combination works",
            "style_vibe": "A 2-3 word vibe description",
            "confidence_score": 0.85
        }
    ],
    "overall_reasoning": "General styling advice for this context",
    "weather_consideration": "How weather influenced the suggestions"
}
"""


async def generate_outfit_suggestions(
    wardrobe_items: list[dict],
    occasion: str = "casual",
    city: str = "Bucharest",
    preferences: str = ""
) -> dict:
    """
    Generate outfit suggestions using Gemini AI.
    
    This is the main agentic function that:
    1. Fetches weather data (tool use)
    2. Formats wardrobe context
    3. Sends to Gemini for multi-step reasoning
    4. Parses and validates the response
    
    Args:
        wardrobe_items: List of garment dicts from the user's wardrobe
        occasion: Type of occasion (casual, formal, sport, party, work)
        city: City for weather data
        preferences: Optional style preferences from the user
    
    Returns:
        Dict with outfit suggestions, weather data, and reasoning
    """
    # Step 1: Tool use — Get weather data
    weather = await get_weather(city)

    # Step 2: Format wardrobe context
    wardrobe_text = _format_wardrobe(wardrobe_items)

    if not wardrobe_items:
        return {
            "suggestions": [],
            "weather": weather,
            "reasoning": "Your wardrobe is empty! Add some clothes first to get outfit suggestions."
        }

    # Step 3: Build the prompt with all context
    user_prompt = f"""Please create outfit suggestions based on the following context:

WEATHER CONDITIONS:
- City: {weather['city']}
- Temperature: {weather['temperature']}°C (feels like {weather['feels_like']}°C)
- Conditions: {weather['description']}
- Clothing hint: {weather['clothing_hint']}

OCCASION: {occasion}

USER PREFERENCES: {preferences if preferences else 'No specific preferences'}

AVAILABLE WARDROBE ITEMS:
{wardrobe_text}

Please suggest 2-3 complete outfits from these items. Remember to ONLY use items from the wardrobe above.
Return your response as valid JSON following the format specified in your instructions."""

    # Step 4: Call Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=STYLIST_SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=2000,
            )
        )

        # Step 5: Parse response
        result = _parse_response(response.text)

        return {
            "suggestions": result.get("outfits", []),
            "weather": weather,
            "reasoning": result.get("overall_reasoning", ""),
            "weather_consideration": result.get("weather_consideration", "")
        }

    except Exception as e:
        return {
            "suggestions": [],
            "weather": weather,
            "reasoning": f"The stylist agent encountered an issue: {str(e)}. Please try again.",
            "error": str(e)
        }


async def analyze_garment_image(image_base64: str) -> dict:
    """
    Use Gemini Vision to analyze a clothing image and extract metadata.
    
    This enables the smart auto-categorization feature.
    
    Args:
        image_base64: Base64 encoded image string
    
    Returns:
        Dict with category, color, season, occasion, and description
    """
    analysis_prompt = """Analyze this clothing item image and provide the following information.
Return ONLY valid JSON:

{
    "name": "Short descriptive name of the garment",
    "category": "one of: top, bottom, shoes, accessory, outerwear, dress",
    "subcategory": "specific type like t-shirt, jeans, sneakers, hat, etc.",
    "color": "primary color of the garment",
    "season": "one of: spring, summer, autumn, winter, all",
    "occasion": "one of: casual, formal, sport, party, work",
    "description": "Brief 1-2 sentence description of the garment style",
    "tags": ["tag1", "tag2", "tag3"]
}"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[
                types.Part.from_bytes(
                    data=__import__('base64').b64decode(image_base64),
                    mime_type="image/jpeg"
                ),
                analysis_prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500,
            )
        )

        return _parse_response(response.text)

    except Exception as e:
        return {
            "name": "Unknown garment",
            "category": "top",
            "subcategory": "",
            "color": "",
            "season": "all",
            "occasion": "casual",
            "description": "Could not analyze image",
            "tags": [],
            "error": str(e)
        }


def _format_wardrobe(items: list[dict]) -> str:
    """Format wardrobe items into a readable string for the AI prompt."""
    if not items:
        return "No items in wardrobe."

    lines = []
    for item in items:
        lines.append(
            f"- ID: {item.get('id', 'unknown')} | "
            f"Name: {item.get('name', 'Unknown')} | "
            f"Category: {item.get('category', 'unknown')} | "
            f"Color: {item.get('color', 'unknown')} | "
            f"Season: {item.get('season', 'all')} | "
            f"Occasion: {item.get('occasion', 'casual')}"
        )
    return "\n".join(lines)


def _parse_response(text: str) -> dict:
    """Parse AI response text, handling markdown code blocks."""
    # Remove markdown code blocks if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass

        return {"error": "Could not parse AI response", "raw": text}
