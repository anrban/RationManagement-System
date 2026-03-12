from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from auth.jwt import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        district=user_data.district,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        role=new_user.role.value if hasattr(new_user.role, "value") else new_user.role,
        district=new_user.district,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token, token_type="bearer")
