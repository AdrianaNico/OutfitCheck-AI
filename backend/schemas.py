"""OutfitCheck AI - Pydantic Schemas for request/response validation"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─── Auth Schemas ─────────────────────────────
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = ""


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Garment Schemas ─────────────────────────────
class GarmentCreate(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = ""
    color: Optional[str] = ""
    season: Optional[str] = "all"
    occasion: Optional[str] = "casual"
    description: Optional[str] = ""


class GarmentResponse(BaseModel):
    id: str
    name: str
    category: str
    subcategory: str
    color: str
    season: str
    occasion: str
    image_url: str
    description: str
    ai_tags: list
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Outfit Schemas ─────────────────────────────
class OutfitCreate(BaseModel):
    name: Optional[str] = ""
    garment_ids: list[str]
    occasion: Optional[str] = "casual"


class OutfitResponse(BaseModel):
    id: str
    name: str
    garment_ids: list
    occasion: str
    weather_context: str
    is_favorite: bool
    ai_score: float
    ai_feedback: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ─── AI Agent Schemas ─────────────────────────────
class OutfitSuggestionRequest(BaseModel):
    occasion: str = "casual"
    city: Optional[str] = "Bucharest"
    preferences: Optional[str] = ""


class OutfitSuggestionResponse(BaseModel):
    suggestions: list[dict]
    weather: dict
    reasoning: str


class FashionCriticRequest(BaseModel):
    outfit_id: Optional[str] = None
    garment_ids: list[str]
    occasion: Optional[str] = "casual"


class FashionCriticResponse(BaseModel):
    overall_score: float
    color_harmony: str
    style_coherence: str
    occasion_fit: str
    improvements: list[str]
    vibe: str


# ─── Search Schemas ─────────────────────────────
class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
