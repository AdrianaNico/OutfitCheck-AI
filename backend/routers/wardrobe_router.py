"""OutfitCheck AI - Wardrobe Router (CRUD for garments)"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from backend.database import get_db
from backend.models import User, Garment
from backend.schemas import GarmentResponse, GarmentCreate
from backend.auth import get_current_user
from backend.services.image_service import save_uploaded_image, image_to_base64, delete_image
from backend.agents.outfit_stylist import analyze_garment_image

router = APIRouter(prefix="/api/wardrobe", tags=["Wardrobe"])


@router.get("/", response_model=list[GarmentResponse])
async def get_wardrobe(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all garments in the user's wardrobe, optionally filtered by category."""
    query = db.query(Garment).filter(Garment.user_id == current_user.id)

    if category:
        query = query.filter(Garment.category == category)

    garments = query.order_by(Garment.created_at.desc()).all()
    return [GarmentResponse.model_validate(g) for g in garments]


@router.post("/", response_model=GarmentResponse, status_code=status.HTTP_201_CREATED)
async def add_garment(
    name: str = Form(...),
    category: str = Form(...),
    subcategory: str = Form(""),
    color: str = Form(""),
    season: str = Form("all"),
    occasion: str = Form("casual"),
    description: str = Form(""),
    image: Optional[UploadFile] = File(None),
    auto_categorize: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new garment to the wardrobe.
    If auto_categorize is True and an image is provided, uses Gemini Vision
    to automatically detect category, color, season, etc.
    """
    image_url = ""
    ai_tags = []

    if image:
        # Read and save image
        file_bytes = await image.read()
        image_url = save_uploaded_image(file_bytes, image.filename)

        # Auto-categorize with Gemini Vision if requested
        if auto_categorize:
            base64_img = image_to_base64(file_bytes)
            analysis = await analyze_garment_image(base64_img)

            if "error" not in analysis:
                # Override form data with AI analysis
                name = analysis.get("name", name) or name
                category = analysis.get("category", category) or category
                subcategory = analysis.get("subcategory", subcategory) or subcategory
                color = analysis.get("color", color) or color
                season = analysis.get("season", season) or season
                occasion = analysis.get("occasion", occasion) or occasion
                description = analysis.get("description", description) or description
                ai_tags = analysis.get("tags", [])

    garment = Garment(
        user_id=current_user.id,
        name=name,
        category=category,
        subcategory=subcategory,
        color=color,
        season=season,
        occasion=occasion,
        image_url=image_url,
        description=description,
        ai_tags=ai_tags
    )

    db.add(garment)
    db.commit()
    db.refresh(garment)

    return GarmentResponse.model_validate(garment)


@router.get("/{garment_id}", response_model=GarmentResponse)
async def get_garment(
    garment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific garment by ID."""
    garment = db.query(Garment).filter(
        Garment.id == garment_id,
        Garment.user_id == current_user.id
    ).first()

    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    return GarmentResponse.model_validate(garment)


@router.delete("/{garment_id}")
async def delete_garment(
    garment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a garment from the wardrobe."""
    garment = db.query(Garment).filter(
        Garment.id == garment_id,
        Garment.user_id == current_user.id
    ).first()

    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    # Delete image file
    if garment.image_url:
        delete_image(garment.image_url)

    db.delete(garment)
    db.commit()

    return {"message": "Garment deleted successfully"}


@router.get("/stats/summary")
async def wardrobe_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get wardrobe statistics."""
    garments = db.query(Garment).filter(Garment.user_id == current_user.id).all()

    categories = {}
    colors = {}
    seasons = {}

    for g in garments:
        categories[g.category] = categories.get(g.category, 0) + 1
        if g.color:
            colors[g.color] = colors.get(g.color, 0) + 1
        seasons[g.season] = seasons.get(g.season, 0) + 1

    return {
        "total_items": len(garments),
        "by_category": categories,
        "by_color": colors,
        "by_season": seasons
    }
