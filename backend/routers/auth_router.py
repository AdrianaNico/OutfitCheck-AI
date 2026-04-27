"""OutfitCheck AI - Authentication Router"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from backend.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, response: Response, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name or ""
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create token
    token = create_access_token({"sub": user.id})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": user.id})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout by clearing the auth cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        __import__('backend.auth', fromlist=['get_current_user']).get_current_user
    )
):
    """Get current authenticated user info."""
    return UserResponse.model_validate(current_user)
