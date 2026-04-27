"""OutfitCheck AI - Search Router (NLP Search)"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Garment
from backend.auth import get_current_user
from backend.schemas import SearchRequest

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("/")
async def search_wardrobe(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search wardrobe using natural language.
    Performs keyword matching on name, category, color, description, and AI tags.
    """
    query = request.query.lower().strip()

    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")

    # Get all user's garments
    garments = db.query(Garment).filter(Garment.user_id == current_user.id).all()

    # Score each garment by relevance
    scored_results = []
    query_words = query.split()

    for garment in garments:
        score = 0
        searchable_text = " ".join([
            garment.name.lower(),
            garment.category.lower(),
            garment.subcategory.lower(),
            garment.color.lower(),
            garment.season.lower(),
            garment.occasion.lower(),
            garment.description.lower(),
            " ".join([str(t).lower() for t in (garment.ai_tags or [])])
        ])

        for word in query_words:
            if word in searchable_text:
                score += 1
                # Bonus for exact name match
                if word in garment.name.lower():
                    score += 2
                # Bonus for category match
                if word in garment.category.lower():
                    score += 1.5
                # Bonus for color match
                if word in garment.color.lower():
                    score += 1.5

        if score > 0:
            scored_results.append({
                "garment": {
                    "id": garment.id,
                    "name": garment.name,
                    "category": garment.category,
                    "subcategory": garment.subcategory,
                    "color": garment.color,
                    "season": garment.season,
                    "occasion": garment.occasion,
                    "image_url": garment.image_url,
                    "description": garment.description,
                    "ai_tags": garment.ai_tags,
                },
                "relevance_score": score
            })

    # Sort by score descending
    scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Apply category filter if specified
    if request.category:
        scored_results = [
            r for r in scored_results
            if r["garment"]["category"] == request.category
        ]

    return {
        "query": request.query,
        "results": scored_results,
        "total": len(scored_results)
    }
