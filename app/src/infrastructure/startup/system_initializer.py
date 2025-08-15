"""
Módulo para inicialização automática do sistema
"""

from app.src.domain.entities.user_model import User
from app.src.infrastructure.driven.persistence.user_repository_impl import UserRepositoryImpl
from app.src.infrastructure.driven.persistence.blacklisted_token_repository_impl import BlacklistedTokenRepositoryImpl
from app.src.application.services.user_service import UserService
from app.src.application.dtos.user_dto import UserCreateDto
import logging

logger = logging.getLogger(__name__)


async def create_default_admin_if_not_exists():
    """
    Cria automaticamente um usuário administrador padrão se não existir.
    Esta função é executada no startup da aplicação.
    """
    try:
        # Instanciar serviços
        user_repository = UserRepositoryImpl()
        blacklisted_token_repository = BlacklistedTokenRepositoryImpl()
        user_service = UserService(user_repository, blacklisted_token_repository)
        
        # Verificar se já existe um usuário administrador
        existing_admin = await user_repository.get_user_by_email("admin@carsales.com")
        if existing_admin:
            logger.info("✅ Usuário administrador já existe - sistema pronto para uso")
            return
        
        # Criar usuário administrador padrão
        admin_data = UserCreateDto(
            email="admin@carsales.com",
            password="admin123456",  # ALTERAR EM PRODUÇÃO!
            role="Administrador",
            employee_id=None  # Administrador não tem funcionário associado
        )
        
        admin_user = await user_service.create_user(admin_data)
        
        logger.info("🎉 Usuário administrador criado automaticamente!")
        logger.info("=" * 60)
        logger.info(f"📧 Email: {admin_user.email}")
        logger.info(f"🔑 Senha: admin123456")
        logger.info(f"👑 Role: {admin_user.role}")
        logger.info(f"🔗 Employee ID: {admin_user.employee_id or 'Não associado'}")
        logger.info("=" * 60)
        logger.info("⚠️  ATENÇÃO: Altere a senha padrão 'admin123456' em produção!")
        logger.info("🔐 Faça login em /api/auth/login para obter seu token JWT")
        logger.info("📖 Acesse /docs para ver a documentação interativa da API")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar usuário administrador: {str(e)}")
        logger.error("⚠️  Sistema iniciará sem usuário administrador")


async def initialize_system():
    """
    Inicializa o sistema com dados padrão necessários.
    """
    logger.info("🚀 Iniciando configuração automática do sistema...")
    
    try:
        # Criar usuário administrador
        await create_default_admin_if_not_exists()
        
        logger.info("✅ Configuração automática do sistema concluída!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização automática: {str(e)}")
        logger.error("⚠️  Sistema continuará funcionando, mas pode ser necessário criar usuário administrador manualmente")
        logger.error("💡 Execute: python scripts/create_admin_user.py para criar usuário administrador")
