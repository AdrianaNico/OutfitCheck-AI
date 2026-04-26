"""
OutfitCheck AI - Agent Evaluation Tests
This script tests the consistency and quality of the AI agents.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import the agents
from backend.agents.outfit_stylist import generate_outfit_suggestions, _format_wardrobe
from backend.agents.fashion_critic import critique_outfit, _format_outfit

# --- Mock Data ---

MOCK_WARDROBE = [
    {"id": "1", "name": "White T-Shirt", "category": "top", "color": "white", "season": "summer", "occasion": "casual"},
    {"id": "2", "name": "Blue Jeans", "category": "bottom", "color": "blue", "season": "all", "occasion": "casual"},
    {"id": "3", "name": "Black Sneakers", "category": "shoes", "color": "black", "season": "all", "occasion": "casual"},
    {"id": "4", "name": "Red Dress", "category": "dress", "color": "red", "season": "summer", "occasion": "party"}
]

MOCK_OUTFIT = [
    {"name": "White T-Shirt", "category": "top", "color": "white", "occasion": "casual"},
    {"name": "Blue Jeans", "category": "bottom", "color": "blue", "occasion": "casual"}
]


# --- Evals for Outfit Stylist (Agent 1) ---

def test_stylist_wardrobe_formatting():
    """Eval: Ensure the agent receives properly formatted wardrobe context."""
    formatted = _format_wardrobe(MOCK_WARDROBE)
    assert "White T-Shirt" in formatted
    assert "top" in formatted
    assert "Blue Jeans" in formatted


@pytest.mark.asyncio
@patch('backend.agents.outfit_stylist.client')
@patch('backend.agents.outfit_stylist.get_weather')
async def test_stylist_empty_wardrobe(mock_weather, mock_client):
    """Eval: Agent should gracefully handle an empty wardrobe."""
    mock_weather.return_value = {"city": "Bucharest", "temperature": 20, "description": "sunny", "clothing_hint": "light"}
    
    result = await generate_outfit_suggestions([])
    
    assert len(result["suggestions"]) == 0
    assert "empty" in result["reasoning"].lower()
    assert not mock_client.models.generate_content.called


# --- Evals for Fashion Critic (Agent 2) ---

def test_critic_outfit_formatting():
    """Eval: Ensure the critic receives properly formatted outfit context."""
    formatted = _format_outfit(MOCK_OUTFIT)
    assert "White T-Shirt" in formatted
    assert "Blue Jeans" in formatted


@pytest.mark.asyncio
@patch('backend.agents.fashion_critic.groq_client')
async def test_critic_empty_outfit(mock_client):
    """Eval: Critic should refuse to score an empty outfit."""
    result = await critique_outfit([])
    
    assert result["overall_score"] == 0
    assert "Add items" in result["verdict"] or "Add items" in result["improvements"][0]
    assert not mock_client.chat.completions.create.called


@pytest.mark.asyncio
@patch('backend.agents.fashion_critic.groq_client')
async def test_critic_output_structure(mock_groq):
    """Eval: Ensure Critic returns the exact expected JSON schema regardless of LLM generation."""
    # Mock LLM response with missing fields to test validation
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"overall_score": 8, "vibe": "Cool"}'
    mock_groq.chat.completions.create.return_value = mock_response

    result = await critique_outfit(MOCK_OUTFIT)
    
    # Check if missing fields were auto-filled by _validate_feedback
    assert result["overall_score"] == 8
    assert result["vibe"] == "Cool"
    assert "color_score" in result
    assert "style_score" in result
    assert "improvements" in result
    assert type(result["improvements"]) is list
