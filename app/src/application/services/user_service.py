from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid
from passlib.context import CryptContext
from passlib.hash import bcrypt
from app.src.domain.entities.user_model import User
from app.src.domain.entities.blacklisted_token_model import BlacklistedToken
from app.src.domain.ports.user_repository import UserRepositoryInterface
from app.src.domain.ports.blacklisted_token_repository import BlacklistedTokenRepositoryInterface
from app.src.application.dtos.user_dto import (
    UserCreateDto, UserUpdateDto, UserResponseDto, 
    LoginDto, TokenDto, TokenDataDto
)
import logging

logger = logging.getLogger(__name__)

# Configurações JWT - em produção devem vir de variáveis de ambiente
SECRET_KEY = "your-secret-key-here-change-in-production"  # Mudar em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuração para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    Serviço de aplicação para usuários e autenticação.
    """
    
    def __init__(self, user_repository: UserRepositoryInterface, blacklisted_token_repository: Optional[BlacklistedTokenRepositoryInterface] = None):
        self.user_repository = user_repository
        self.blacklisted_token_repository = blacklisted_token_repository
    
    def _hash_password(self, password: str) -> str:
        """
        Gera hash da senha.
        """
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha está correta.
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, str, datetime]:
        """
        Cria um token JWT de acesso com JTI.
        
        Returns:
            tuple: (token, jti, expires_at)
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Gerar JTI único
        jti = str(uuid.uuid4())
        
        to_encode.update({
            "exp": expire,
            "jti": jti  # JWT ID para identificar tokens únicos
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, jti, expire
    
    async def _verify_token(self, token: str) -> Optional[TokenDataDto]:
        """
        Verifica e decodifica um token JWT, incluindo verificação de blacklist.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")
            jti: str = payload.get("jti")
            
            if user_id is None or email is None or jti is None:
                return None
            
            # Verificar se token está na blacklist
            if self.blacklisted_token_repository:
                is_blacklisted = await self.blacklisted_token_repository.is_token_blacklisted(jti)
                if is_blacklisted:
                    logger.info(f"Token blacklisted rejeitado: {jti}")
                    return None
                
            return TokenDataDto(user_id=user_id, email=email, role=role)
        except jwt.PyJWTError:
            return None
    
    async def create_user(self, user_create: UserCreateDto) -> UserResponseDto:
        """
        Cria um novo usuário.
        """
        try:
            # Verificar se email já existe
            existing_user = await self.user_repository.get_user_by_email(user_create.email)
            if existing_user:
                raise ValueError("Email já está em uso")
            
            # Criar usuário com senha hasheada
            hashed_password = self._hash_password(user_create.password)
            
            user = User(
                email=user_create.email,
                password=hashed_password,
                role=user_create.role,
                employee_id=user_create.employee_id
            )
            
            created_user = await self.user_repository.create_user(user)
            
            return UserResponseDto(
                id=created_user.id,
                email=created_user.email,
                role=created_user.role,
                employee_id=created_user.employee_id
            )
            
        except ValueError as e:
            logger.error(f"Erro de validação ao criar usuário: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            raise Exception(f"Erro interno do servidor: {str(e)}")
    
    async def authenticate_user(self, login: LoginDto) -> Optional[User]:
        """
        Autentica um usuário.
        """
        try:
            user = await self.user_repository.get_user_by_email(login.email)
            if not user or not self._verify_password(login.password, user.password):
                return None
            return user
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {str(e)}")
            return None
    
    async def login(self, login: LoginDto) -> TokenDto:
        """
        Realiza login e retorna token JWT.
        """
        try:
            user = await self.authenticate_user(login)
            if not user:
                raise ValueError("Email ou senha incorretos")
            
            # Criar token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token, jti, expires_at = self._create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": user.role
                },
                expires_delta=access_token_expires
            )
            
            return TokenDto(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except ValueError as e:
            logger.error(f"Erro de autenticação: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            raise Exception(f"Erro interno do servidor: {str(e)}")
    
    async def logout(self, token: str) -> bool:
        """
        Realiza logout adicionando o token à blacklist.
        
        Args:
            token: Token JWT a ser invalidado
            
        Returns:
            bool: True se logout realizado com sucesso
        """
        try:
            if not self.blacklisted_token_repository:
                logger.warning("Repositório de blacklist não configurado - logout não disponível")
                return False
            
            # Decodificar token para obter informações
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti")
            user_id = payload.get("sub")
            exp = payload.get("exp")
            
            if not jti or not user_id or not exp:
                raise ValueError("Token inválido para logout")
            
            # Converter timestamp de expiração para datetime
            expires_at = datetime.utcfromtimestamp(exp)
            
            # Criar registro de token blacklisted
            blacklisted_token = BlacklistedToken.create_blacklisted_token(
                jti=jti,
                token=token,
                user_id=int(user_id),
                expires_at=expires_at
            )
            
            # Adicionar à blacklist
            await self.blacklisted_token_repository.add_token_to_blacklist(blacklisted_token)
            
            logger.info(f"Logout realizado com sucesso para usuário {user_id}")
            return True
            
        except jwt.PyJWTError as e:
            logger.error(f"Erro ao decodificar token para logout: {str(e)}")
            raise ValueError("Token inválido")
        except Exception as e:
            logger.error(f"Erro no logout: {str(e)}")
            raise Exception(f"Erro interno do servidor: {str(e)}")
    
    async def get_current_user(self, token: str) -> Optional[UserResponseDto]:
        """
        Obtém o usuário atual baseado no token.
        """
        try:
            token_data = await self._verify_token(token)
            if token_data is None or token_data.user_id is None:
                return None
            
            user = await self.user_repository.get_user_by_id(token_data.user_id)
            if user is None:
                return None
            
            return UserResponseDto(
                id=user.id,
                email=user.email,
                role=user.role,
                employee_id=user.employee_id
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter usuário atual: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponseDto]:
        """
        Busca um usuário pelo ID.
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                return None
            
            return UserResponseDto(
                id=user.id,
                email=user.email,
                role=user.role,
                employee_id=user.employee_id
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {str(e)}")
            raise Exception(f"Erro interno do servidor: {str(e)}")
    
    async def update_user(self, user_id: int, user_update: UserUpdateDto) -> Optional[UserResponseDto]:
        """
        Atualiza um usuário.
        """
        try:
            # Buscar usuário existente
            existing_user = await self.user_repository.get_user_by_id(user_id)
            if not existing_user:
                return None
            
            # Verificar se email já existe (se está sendo alterado)
            if user_update.email and user_update.email != existing_user.email:
                email_exists = await self.user_repository.get_user_by_email(user_update.email)
                if email_exists:
                    raise ValueError("Email já está em uso")
            
            # Atualizar campos
            if user_update.email:
                existing_user.email = user_update.email
            if user_update.password:
                existing_user.password = self._hash_password(user_update.password)
            if user_update.role:
                existing_user.role = user_update.role
            if user_update.employee_id is not None:
                existing_user.employee_id = user_update.employee_id
            
            updated_user = await self.user_repository.update_user(user_id, existing_user)
            if not updated_user:
                return None
            
            return UserResponseDto(
                id=updated_user.id,
                email=updated_user.email,
                role=updated_user.role,
                employee_id=updated_user.employee_id
            )
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar usuário: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            raise Exception(f"Erro interno do servidor: {str(e)}")
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Remove um usuário.
        """
        try:
            return await self.user_repository.delete_user(user_id)
            
        except Exception as e:
            logger.error(f"Erro ao deletar usuário: {str(e)}")
            raise Exception(f"Erro interno do servidor: {str(e)}")
    
    def verify_admin_role(self, user: UserResponseDto) -> bool:
        """
        Verifica se o usuário tem perfil de administrador.
        """
        return user.role == User.ROLE_ADMINISTRADOR
    
    def verify_vendedor_role(self, user: UserResponseDto) -> bool:
        """
        Verifica se o usuário tem perfil de vendedor.
        """
        return user.role == User.ROLE_VENDEDOR
