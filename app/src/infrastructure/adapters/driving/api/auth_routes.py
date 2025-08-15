from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.src.application.services.user_service import UserService
from app.src.application.dtos.user_dto import (
    UserCreateDto, UserUpdateDto, UserResponseDto, 
    LoginDto, TokenDto
)
from app.src.infrastructure.driven.persistence.user_repository_impl import UserRepositoryImpl
from app.src.infrastructure.driven.persistence.blacklisted_token_repository_impl import BlacklistedTokenRepositoryImpl
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_user, get_current_admin_user
)

# Router para autenticação
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Router para usuários (operações CRUD)
users_router = APIRouter(prefix="/users", tags=["Users"])

# Configuração do bearer token
security = HTTPBearer()

# Instância dos serviços
user_repository = UserRepositoryImpl()
blacklisted_token_repository = BlacklistedTokenRepositoryImpl()
user_service = UserService(user_repository, blacklisted_token_repository)


@auth_router.post("/login", response_model=TokenDto)
async def login(login_data: LoginDto):
    """
    Endpoint para autenticação de usuários.
    Retorna um token JWT válido por 30 minutos.
    """
    try:
        token = await user_service.login(login_data)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@auth_router.get("/me", response_model=UserResponseDto)
async def get_current_user_info(current_user: UserResponseDto = Depends(get_current_user)):
    """
    Endpoint para obter informações do usuário autenticado.
    """
    return current_user


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Endpoint para logout (invalidação de token).
    Adiciona o token atual à blacklist, invalidando-o.
    """
    try:
        token = credentials.credentials
        success = await user_service.logout(token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao realizar logout"
            )
        
        return {"message": "Logout realizado com sucesso"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@users_router.post("/", response_model=UserResponseDto, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateDto,
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Endpoint para criar um novo usuário.
    Apenas administradores podem criar usuários.
    """
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@users_router.get("/{user_id}", response_model=UserResponseDto)
async def get_user(
    user_id: int,
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Endpoint para buscar um usuário pelo ID.
    Apenas administradores podem visualizar outros usuários.
    """
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@users_router.put("/{user_id}", response_model=UserResponseDto)
async def update_user(
    user_id: int,
    user_data: UserUpdateDto,
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Endpoint para atualizar um usuário.
    Apenas administradores podem atualizar usuários.
    """
    try:
        user = await user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Endpoint para deletar um usuário.
    Apenas administradores podem deletar usuários.
    """
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
