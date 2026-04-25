"""OutfitCheck AI - Outfit Router (Generation + Critique)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Garment, Outfit, AIFeedbackHistory
from backend.schemas import (
    OutfitCreate, OutfitResponse,
    OutfitSuggestionRequest, OutfitSuggestionResponse,
    FashionCriticRequest, FashionCriticResponse
)
from backend.auth import get_current_user
from backend.agents.outfit_stylist import generate_outfit_suggestions
from backend.agents.fashion_critic import critique_outfit

router = APIRouter(prefix="/api/outfits", tags=["Outfits"])


@router.get("/", response_model=list[OutfitResponse])
async def get_outfits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all saved outfits for the current user."""
    outfits = db.query(Outfit).filter(
        Outfit.user_id == current_user.id
    ).order_by(Outfit.created_at.desc()).all()

    return [OutfitResponse.model_validate(o) for o in outfits]


@router.post("/", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
async def create_outfit(
    outfit_data: OutfitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a new outfit combination."""
    # Verify all garment IDs belong to the user
    for gid in outfit_data.garment_ids:
        garment = db.query(Garment).filter(
            Garment.id == gid,
            Garment.user_id == current_user.id
        ).first()
        if not garment:
            raise HTTPException(status_code=404, detail=f"Garment {gid} not found")

    outfit = Outfit(
        user_id=current_user.id,
        name=outfit_data.name or "My Outfit",
        garment_ids=outfit_data.garment_ids,
        occasion=outfit_data.occasion
    )

    db.add(outfit)
    db.commit()
    db.refresh(outfit)

    return OutfitResponse.model_validate(outfit)


@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a saved outfit."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db.delete(outfit)
    db.commit()

    return {"message": "Outfit deleted successfully"}


@router.post("/suggest")
async def suggest_outfits(
    request: OutfitSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI Agent 1: Generate outfit suggestions using the Outfit Stylist Agent.
    Uses Gemini to analyze the user's wardrobe and suggest combinations
    based on weather and occasion.
    """
    # Get all user's garments
    garments = db.query(Garment).filter(Garment.user_id == current_user.id).all()
    wardrobe_items = [
        {
            "id": g.id,
            "name": g.name,
            "category": g.category,
            "subcategory": g.subcategory,
            "color": g.color,
            "season": g.season,
            "occasion": g.occasion,
            "image_url": g.image_url
        }
        for g in garments
    ]

    # Call Agent 1
    result = await generate_outfit_suggestions(
        wardrobe_items=wardrobe_items,
        occasion=request.occasion,
        city=request.city or "Bucharest",
        preferences=request.preferences or ""
    )

    # Save to feedback history
    history = AIFeedbackHistory(
        user_id=current_user.id,
        agent_type="outfit_stylist",
        input_data={
            "occasion": request.occasion,
            "city": request.city,
            "wardrobe_count": len(wardrobe_items)
        },
        output_data=result
    )
    db.add(history)
    db.commit()

    return result


@router.post("/critique")
async def critique_outfit_endpoint(
    request: FashionCriticRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI Agent 2: Get fashion critique using the Fashion Critic Agent.
    Uses Groq/Llama to evaluate the outfit across multiple dimensions.
    """
    # Get garment details
    outfit_items = []
    for gid in request.garment_ids:
        garment = db.query(Garment).filter(
            Garment.id == gid,
            Garment.user_id == current_user.id
        ).first()
        if garment:
            outfit_items.append({
                "name": garment.name,
                "category": garment.category,
                "subcategory": garment.subcategory,
                "color": garment.color,
                "season": garment.season,
                "occasion": garment.occasion
            })

    if not outfit_items:
        raise HTTPException(status_code=400, detail="No valid garments found")

    # Get previous feedback for this user (agent memory)
    previous = db.query(AIFeedbackHistory).filter(
        AIFeedbackHistory.user_id == current_user.id,
        AIFeedbackHistory.agent_type == "fashion_critic"
    ).order_by(AIFeedbackHistory.created_at.desc()).limit(3).all()

    previous_feedback = [
        {"output_data": p.output_data} for p in previous
    ]

    # Call Agent 2
    result = await critique_outfit(
        outfit_items=outfit_items,
        occasion=request.occasion or "casual",
        previous_feedback=previous_feedback
    )

    # Save to feedback history
    history = AIFeedbackHistory(
        user_id=current_user.id,
        outfit_id=request.outfit_id,
        agent_type="fashion_critic",
        input_data={
            "garment_ids": request.garment_ids,
            "occasion": request.occasion
        },
        output_data=result
    )
    db.add(history)
    db.commit()

    return result


@router.post("/{outfit_id}/favorite")
async def toggle_favorite(
    outfit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status for an outfit."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit.is_favorite = not outfit.is_favorite
    db.commit()

    return {"is_favorite": outfit.is_favorite}


@router.get("/favorites/all", response_model=list[OutfitResponse])
async def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorite outfits."""
    outfits = db.query(Outfit).filter(
        Outfit.user_id == current_user.id,
        Outfit.is_favorite == True
    ).order_by(Outfit.created_at.desc()).all()

    return [OutfitResponse.model_validate(o) for o in outfits]
