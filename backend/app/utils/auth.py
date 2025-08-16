from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_current_user_optional(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user (optional, returns None if not authenticated)"""
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        
        user = await get_user_by_email(db, email=email)
        return user
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user (required)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
