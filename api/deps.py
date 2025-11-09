from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories.auth import AuthRepository

from services.auth import AuthService

# Repositories
async def get_auth_repository(db: AsyncSession = Depends(get_async_session)) -> AuthRepository:
    return AuthRepository(db)


# Services
async def get_auth_service(
    auth_repository: AuthRepository = Depends(get_auth_repository)
) -> AuthService:
    return AuthService(auth_repository)
