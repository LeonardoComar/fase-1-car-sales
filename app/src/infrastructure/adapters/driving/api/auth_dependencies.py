from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.src.application.services.user_service import UserService
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.infrastructure.driven.persistence.user_repository_impl import UserRepositoryImpl
from app.src.infrastructure.driven.persistence.blacklisted_token_repository_impl import BlacklistedTokenRepositoryImpl

# Configuração do bearer token
security = HTTPBearer()

# Instância dos serviços
user_repository = UserRepositoryImpl()
blacklisted_token_repository = BlacklistedTokenRepositoryImpl()
user_service = UserService(user_repository, blacklisted_token_repository)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponseDto:
    """
    Dependency para obter o usuário atual autenticado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user = await user_service.get_current_user(token)
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


async def get_current_admin_user(current_user: UserResponseDto = Depends(get_current_user)) -> UserResponseDto:
    """
    Dependency para verificar se o usuário atual é administrador.
    """
    if not user_service.verify_admin_role(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user


async def get_current_vendedor_user(current_user: UserResponseDto = Depends(get_current_user)) -> UserResponseDto:
    """
    Dependency para verificar se o usuário atual é vendedor.
    """
    if not user_service.verify_vendedor_role(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Vendedor role required."
        )
    return current_user


async def get_current_admin_or_vendedor_user(current_user: UserResponseDto = Depends(get_current_user)) -> UserResponseDto:
    """
    Dependency para verificar se o usuário atual é administrador ou vendedor.
    """
    if not (user_service.verify_admin_role(current_user) or user_service.verify_vendedor_role(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin or Vendedor role required."
        )
    return current_user


# Funções opcionais para autenticação opcional
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserResponseDto]:
    """
    Dependency para obter o usuário atual (opcional).
    Retorna None se não autenticado.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await user_service.get_current_user(token)
        return user
    except Exception:
        return None
