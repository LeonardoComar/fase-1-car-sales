from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from app.src.application.dtos.employee_dto import (
    CreateEmployeeRequest, 
    UpdateEmployeeRequest, 
    EmployeeResponse, 
    EmployeesListResponse
)
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.application.services.employee_service import EmployeeService
from app.src.infrastructure.driven.persistence.employee_repository_impl import EmployeeRepository
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_admin_user
)
import logging

logger = logging.getLogger(__name__)

# Configuração do router
router = APIRouter(prefix="/employees", tags=["employees"])

# Dependência para o serviço de funcionários
def get_employee_service() -> EmployeeService:
    employee_repository = EmployeeRepository()
    return EmployeeService(employee_repository)


@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    employee_request: CreateEmployeeRequest,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Cria um novo funcionário no sistema.
    
    Requer autenticação: Administrador
    
    - **name**: Nome completo do funcionário
    - **email**: Email único do funcionário
    - **phone**: Telefone do funcionário
    - **cpf**: CPF único do funcionário
    - **address**: Endereço do funcionário (opcional)
    
    O funcionário é criado com status "Ativo" por padrão.
    """
    try:
        logger.info(f"Criando novo funcionário: {employee_request.name}")
        employee = await employee_service.create_employee(employee_request)
        logger.info(f"Funcionário criado com sucesso. ID: {employee.id}")
        return employee
    except ValueError as e:
        logger.warning(f"Erro de validação ao criar funcionário: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao criar funcionário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/", response_model=EmployeesListResponse)
async def list_employees(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros para retornar"),
    name: Optional[str] = Query(None, description="Buscar por nome (busca parcial)"),
    cpf: Optional[str] = Query(None, description="Buscar por CPF exato"),
    status: Optional[str] = Query(None, regex="^(Ativo|Inativo)$", description="Filtrar por status"),
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Lista todos os funcionários com opções de busca e paginação.
    
    Requer autenticação: Administrador
    
    ### Parâmetros de busca (mutuamente exclusivos):
    - **name**: Busca funcionários cujo nome contenha o termo especificado
    - **cpf**: Busca funcionário com CPF exato
    
    ### Parâmetros de filtro:
    - **status**: Filtra funcionários por status (Ativo/Inativo)
    
    ### Parâmetros de paginação:
    - **skip**: Número de registros para pular (padrão: 0)
    - **limit**: Número máximo de registros para retornar (padrão: 100, máximo: 500)
    
    **Nota**: Os parâmetros name e cpf não podem ser usados simultaneamente.
    """
    try:
        # Validar que name e cpf não sejam usados simultaneamente
        search_params = [name, cpf]
        provided_search_params = [param for param in search_params if param is not None]
        
        if len(provided_search_params) > 1:
            raise HTTPException(
                status_code=400, 
                detail="Não é possível buscar por nome e CPF simultaneamente. Use apenas um parâmetro de busca por vez."
            )
        
        logger.info(f"Listando funcionários. Skip: {skip}, Limit: {limit}, Name: {name}, CPF: {cpf}, Status: {status}")
        
        employees = await employee_service.get_employees_with_filters(
            skip=skip,
            limit=limit,
            name=name,
            cpf=cpf,
            status=status
        )
        
        logger.info(f"Retornando {len(employees)} funcionários")
        return EmployeesListResponse(employees=employees, total=len(employees))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar funcionários: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Busca um funcionário específico pelo ID.
    
    Requer autenticação: Administrador
    
    - **employee_id**: ID único do funcionário
    """
    try:
        logger.info(f"Buscando funcionário por ID: {employee_id}")
        employee = await employee_service.get_employee_by_id(employee_id)
        
        if not employee:
            logger.warning(f"Funcionário não encontrado. ID: {employee_id}")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        logger.info(f"Funcionário encontrado: {employee.name}")
        return employee
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_request: UpdateEmployeeRequest,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Atualiza os dados de um funcionário existente.
    
    - **employee_id**: ID único do funcionário
    - **name**: Nome completo do funcionário (opcional)
    - **email**: Email único do funcionário (opcional)
    - **phone**: Telefone do funcionário (opcional)
    - **cpf**: CPF único do funcionário (opcional)
    - **status**: Status do funcionário - Ativo/Inativo (opcional)
    - **address**: Endereço do funcionário (opcional)
    
    Apenas os campos fornecidos serão atualizados.
    """
    try:
        logger.info(f"Atualizando funcionário ID: {employee_id}")
        employee = await employee_service.update_employee(employee_id, employee_request)
        
        if not employee:
            logger.warning(f"Funcionário não encontrado para atualização. ID: {employee_id}")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        logger.info(f"Funcionário atualizado com sucesso: {employee.name}")
        return employee
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Erro de validação ao atualizar funcionário {employee_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: int,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Remove um funcionário do sistema.
    
    - **employee_id**: ID único do funcionário a ser removido
    
    **Atenção**: Esta operação é irreversível. O funcionário será 
    permanentemente removido do banco de dados.
    """
    try:
        logger.info(f"Removendo funcionário ID: {employee_id}")
        deleted = await employee_service.delete_employee(employee_id)
        
        if not deleted:
            logger.warning(f"Funcionário não encontrado para remoção. ID: {employee_id}")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        logger.info(f"Funcionário removido com sucesso. ID: {employee_id}")
        return
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao remover funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Endpoints específicos para ativação/desativação
@router.patch("/{employee_id}/activate", response_model=EmployeeResponse)
async def activate_employee(
    employee_id: int,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Ativa um funcionário (define status como 'Ativo').
    
    Requer autenticação: Administrador
    
    - **employee_id**: ID único do funcionário
    
    Endpoint de conveniência para ativar funcionários rapidamente.
    """
    try:
        logger.info(f"Ativando funcionário ID: {employee_id}")
        employee = await employee_service.update_employee_status(employee_id, "Ativo")
        
        if not employee:
            logger.warning(f"Funcionário não encontrado para ativação. ID: {employee_id}")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        logger.info(f"Funcionário ativado com sucesso: {employee.name}")
        return employee
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao ativar funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{employee_id}/deactivate", response_model=EmployeeResponse)
async def deactivate_employee(
    employee_id: int,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: UserResponseDto = Depends(get_current_admin_user)
):
    """
    Desativa um funcionário (define status como 'Inativo').
    
    Requer autenticação: Administrador
    
    - **employee_id**: ID único do funcionário
    
    Endpoint de conveniência para desativar funcionários rapidamente.
    """
    try:
        logger.info(f"Desativando funcionário ID: {employee_id}")
        employee = await employee_service.update_employee_status(employee_id, "Inativo")
        
        if not employee:
            logger.warning(f"Funcionário não encontrado para desativação. ID: {employee_id}")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        logger.info(f"Funcionário desativado com sucesso: {employee.name}")
        return employee
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao desativar funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
