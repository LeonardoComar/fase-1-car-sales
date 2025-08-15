"""
Script para criação de usuário administrador inicial
Execute este script após a criação das tabelas do banco de dados
"""

from app.src.domain.entities.user_model import User
from app.src.infrastructure.driven.persistence.user_repository_impl import UserRepositoryImpl
from app.src.application.services.user_service import UserService
from app.src.application.dtos.user_dto import UserCreateDto
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_default_admin():
    """
    Cria um usuário administrador padrão no sistema.
    """
    try:
        # Instanciar serviços
        user_repository = UserRepositoryImpl()
        user_service = UserService(user_repository)
        
        # Verificar se já existe um usuário com este email
        existing_user = await user_repository.get_user_by_email("admin@carsales.com")
        if existing_user:
            logger.info("Usuário administrador já existe!")
            return
        
        # Criar usuário administrador padrão
        admin_data = UserCreateDto(
            email="admin@carsales.com",
            password="admin123456",  # ALTERAR EM PRODUÇÃO!
            role="Administrador",
            employee_id=None  # Administrador não tem funcionário associado
        )
        
        admin_user = await user_service.create_user(admin_data)
        
        logger.info(f"Usuário administrador criado com sucesso!")
        logger.info(f"Email: {admin_user.email}")
        logger.info(f"Role: {admin_user.role}")
        logger.info("ATENÇÃO: Altere a senha padrão em produção!")
        
    except Exception as e:
        logger.error(f"Erro ao criar usuário administrador: {str(e)}")


if __name__ == "__main__":
    asyncio.run(create_default_admin())
