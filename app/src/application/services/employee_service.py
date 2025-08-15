from typing import Optional, List
from app.src.domain.ports.employee_repository import EmployeeRepositoryInterface
from app.src.domain.entities.employee_model import Employee
from app.src.domain.entities.client_model import Address
from app.src.application.dtos.employee_dto import (
    CreateEmployeeRequest, UpdateEmployeeRequest, EmployeeResponse, 
    EmployeeListResponse, EmployeesListResponse, AddressResponse
)
import logging

logger = logging.getLogger(__name__)


class EmployeeService:
    """
    Serviço de aplicação para operações relacionadas a funcionários.
    Coordena as operações entre a camada de apresentação e o domínio.
    """
    
    def __init__(self, employee_repository: EmployeeRepositoryInterface):
        self.employee_repository = employee_repository
    
    async def create_employee(self, request: CreateEmployeeRequest) -> EmployeeResponse:
        """
        Cria um novo funcionário.
        
        Args:
            request: Dados para criação do funcionário
            
        Returns:
            EmployeeResponse: Dados do funcionário criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            logger.info(f"Iniciando criação de funcionário: {request.name}")
            
            # Verificar se já existe funcionário com mesmo email
            existing_employee = await self.employee_repository.get_employee_by_email(request.email)
            if existing_employee:
                raise ValueError(f"Já existe um funcionário cadastrado com o email: {request.email}")
            
            # Verificar se já existe funcionário com mesmo CPF
            existing_employee_cpf = await self.employee_repository.get_employee_by_cpf(request.cpf)
            if existing_employee_cpf:
                raise ValueError(f"Já existe um funcionário cadastrado com o CPF: {request.cpf}")
            
            # Criar entidades do domínio
            address, employee = Employee.create_with_address(
                name=request.name,
                email=request.email,
                cpf=request.cpf,
                phone=request.phone,
                street=request.street,
                city=request.city,
                state=request.state,
                zip_code=request.zip_code,
                country=request.country
            )
            
            # Persistir no repositório
            created_employee = await self.employee_repository.create_employee(address, employee)
            
            logger.info(f"Funcionário criado com sucesso. ID: {created_employee.id}")
            
            # Converter para DTO de resposta
            return self._convert_to_employee_response(created_employee)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao criar funcionário: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao criar funcionário: {e}")
            raise Exception(f"Erro interno do servidor ao criar funcionário: {str(e)}")
    
    async def get_employee_by_id(self, employee_id: int) -> Optional[EmployeeResponse]:
        """
        Busca um funcionário pelo ID.
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            Optional[EmployeeResponse]: Dados do funcionário ou None se não encontrado
        """
        try:
            logger.info(f"Buscando funcionário por ID: {employee_id}")
            
            employee = await self.employee_repository.get_employee_by_id(employee_id)
            
            if not employee:
                logger.warning(f"Funcionário não encontrado com ID: {employee_id}")
                return None
            
            logger.info(f"Funcionário encontrado: {employee.name}")
            return self._convert_to_employee_response(employee)
            
        except Exception as e:
            logger.error(f"Erro ao buscar funcionário por ID {employee_id}: {e}")
            raise Exception(f"Erro interno do servidor ao buscar funcionário: {str(e)}")
    
    async def get_employee_by_cpf(self, cpf: str) -> Optional[EmployeeResponse]:
        """
        Busca um funcionário pelo CPF.
        
        Args:
            cpf: CPF do funcionário
            
        Returns:
            Optional[EmployeeResponse]: Dados do funcionário ou None se não encontrado
        """
        try:
            logger.info(f"Buscando funcionário por CPF: {cpf}")
            
            employee = await self.employee_repository.get_employee_by_cpf(cpf)
            
            if not employee:
                logger.warning(f"Funcionário não encontrado com CPF: {cpf}")
                return None
            
            logger.info(f"Funcionário encontrado: {employee.name}")
            return self._convert_to_employee_response(employee)
            
        except Exception as e:
            logger.error(f"Erro ao buscar funcionário por CPF {cpf}: {e}")
            raise Exception(f"Erro interno do servidor ao buscar funcionário: {str(e)}")
    
    async def update_employee(self, employee_id: int, request: UpdateEmployeeRequest) -> Optional[EmployeeResponse]:
        """
        Atualiza um funcionário existente.
        
        Args:
            employee_id: ID do funcionário
            request: Dados para atualização
            
        Returns:
            Optional[EmployeeResponse]: Dados do funcionário atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        try:
            logger.info(f"Iniciando atualização de funcionário. ID: {employee_id}")
            
            # Verificar se o funcionário existe
            existing_employee = await self.employee_repository.get_employee_by_id(employee_id)
            if not existing_employee:
                logger.warning(f"Funcionário não encontrado para atualização. ID: {employee_id}")
                return None
            
            # Verificar se email está sendo alterado e se já existe
            if request.email and request.email != existing_employee.email:
                email_employee = await self.employee_repository.get_employee_by_email(request.email)
                if email_employee and email_employee.id != employee_id:
                    raise ValueError(f"Já existe outro funcionário cadastrado com o email: {request.email}")
            
            # Verificar se CPF está sendo alterado e se já existe
            if request.cpf and request.cpf != existing_employee.cpf:
                cpf_employee = await self.employee_repository.get_employee_by_cpf(request.cpf)
                if cpf_employee and cpf_employee.id != employee_id:
                    raise ValueError(f"Já existe outro funcionário cadastrado com o CPF: {request.cpf}")
            
            # Criar entidades atualizadas
            address = None
            if any([request.street, request.city, request.state, request.zip_code, request.country]):
                address = Address(
                    street=request.street,
                    city=request.city,
                    state=request.state,
                    zip_code=request.zip_code,
                    country=request.country
                )
                if existing_employee.address_id:
                    address.id = existing_employee.address_id
            
            # Atualizar dados do funcionário
            employee = Employee(
                name=request.name or existing_employee.name,
                email=request.email or existing_employee.email,
                cpf=request.cpf or existing_employee.cpf,
                phone=request.phone if request.phone is not None else existing_employee.phone,
                status=request.status or existing_employee.status,
                address_id=existing_employee.address_id
            )
            employee.id = employee_id
            
            # Persistir no repositório
            updated_employee = await self.employee_repository.update_employee(employee_id, address, employee)
            
            if not updated_employee:
                logger.warning(f"Falha ao atualizar funcionário. ID: {employee_id}")
                return None
            
            logger.info(f"Funcionário atualizado com sucesso. ID: {employee_id}")
            return self._convert_to_employee_response(updated_employee)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar funcionário {employee_id}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar funcionário {employee_id}: {e}")
            raise Exception(f"Erro interno do servidor ao atualizar funcionário: {str(e)}")
    
    async def update_employee_status(self, employee_id: int, status: str) -> Optional[EmployeeResponse]:
        """
        Atualiza apenas o status de um funcionário.
        
        Args:
            employee_id: ID do funcionário
            status: Novo status (Ativo/Inativo)
            
        Returns:
            Optional[EmployeeResponse]: Dados do funcionário atualizado ou None se não encontrado
        """
        try:
            logger.info(f"Iniciando atualização de status do funcionário. ID: {employee_id}, Status: {status}")
            
            # Validar status
            if status not in ["Ativo", "Inativo"]:
                raise ValueError("Status deve ser 'Ativo' ou 'Inativo'")
            
            updated_employee = await self.employee_repository.update_employee_status(employee_id, status)
            
            if not updated_employee:
                logger.warning(f"Funcionário não encontrado para atualização de status. ID: {employee_id}")
                return None
            
            logger.info(f"Status do funcionário atualizado com sucesso. ID: {employee_id}")
            return self._convert_to_employee_response(updated_employee)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar status do funcionário {employee_id}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar status do funcionário {employee_id}: {e}")
            raise Exception(f"Erro interno do servidor ao atualizar status: {str(e)}")
    
    async def delete_employee(self, employee_id: int) -> bool:
        """
        Remove um funcionário.
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            Exception: Se houver erro na remoção
        """
        try:
            logger.info(f"Iniciando remoção de funcionário. ID: {employee_id}")
            
            success = await self.employee_repository.delete_employee(employee_id)
            
            if success:
                logger.info(f"Funcionário removido com sucesso. ID: {employee_id}")
            else:
                logger.warning(f"Funcionário não encontrado para remoção. ID: {employee_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover funcionário {employee_id}: {e}")
            raise Exception(f"Erro interno do servidor ao remover funcionário: {str(e)}")
    
    async def get_all_employees(self, skip: int = 0, limit: int = 100, 
                               name: Optional[str] = None, status: Optional[str] = None) -> List[EmployeeListResponse]:
        """
        Lista funcionários com filtros opcionais.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            name: Nome ou parte do nome para filtrar (opcional)
            status: Status para filtrar (opcional)
            
        Returns:
            List[EmployeeListResponse]: Lista de funcionários
        """
        try:
            if status:
                logger.info(f"Listando funcionários por status: {status}. Skip: {skip}, Limit: {limit}")
                employees = await self.employee_repository.get_employees_by_status(status, skip, limit)
                logger.info(f"Encontrados {len(employees)} funcionários com status '{status}'")
            elif name:
                logger.info(f"Buscando funcionários por nome: {name}. Skip: {skip}, Limit: {limit}")
                employees = await self.employee_repository.search_employees_by_name(name, skip, limit)
                logger.info(f"Encontrados {len(employees)} funcionários com nome '{name}'")
            else:
                logger.info(f"Listando todos os funcionários. Skip: {skip}, Limit: {limit}")
                employees = await self.employee_repository.get_all_employees(skip, limit)
                logger.info(f"Encontrados {len(employees)} funcionários")
            
            return [self._convert_to_employee_list_response(employee) for employee in employees]
            
        except Exception as e:
            logger.error(f"Erro ao listar funcionários: {e}")
            raise Exception(f"Erro interno do servidor ao listar funcionários: {str(e)}")

    async def get_employees_with_filters(self, skip: int = 0, limit: int = 100,
                                        name: Optional[str] = None, cpf: Optional[str] = None,
                                        status: Optional[str] = None) -> List[EmployeeListResponse]:
        """
        Lista funcionários com filtros unificados.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            name: Nome ou parte do nome para filtrar (opcional)
            cpf: CPF exato para buscar (opcional)
            status: Status para filtrar (opcional)
            
        Returns:
            List[EmployeeListResponse]: Lista de funcionários
        """
        try:
            logger.info(f"Listando funcionários com filtros. Skip: {skip}, Limit: {limit}, Name: {name}, CPF: {cpf}, Status: {status}")
            
            # Se CPF for fornecido, buscar funcionário específico
            if cpf:
                employee = await self.employee_repository.get_employee_by_cpf(cpf)
                if employee:
                    logger.info(f"Funcionário encontrado com CPF: {cpf}")
                    return [self._convert_to_employee_list_response(employee)]
                else:
                    logger.info(f"Funcionário não encontrado com CPF: {cpf}")
                    return []
            
            # Se nome for fornecido, buscar por nome
            elif name:
                employees = await self.employee_repository.search_employees_by_name(name, skip, limit)
                # Se status também foi fornecido, filtrar por status
                if status:
                    employees = [emp for emp in employees if emp.status == status]
                logger.info(f"Encontrados {len(employees)} funcionários com nome '{name}'")
                return [self._convert_to_employee_list_response(employee) for employee in employees]
            
            # Se apenas status for fornecido
            elif status:
                employees = await self.employee_repository.get_employees_by_status(status, skip, limit)
                logger.info(f"Encontrados {len(employees)} funcionários com status '{status}'")
                return [self._convert_to_employee_list_response(employee) for employee in employees]
            
            # Listar todos se nenhum filtro for fornecido
            else:
                employees = await self.employee_repository.get_all_employees(skip, limit)
                logger.info(f"Encontrados {len(employees)} funcionários")
                return [self._convert_to_employee_list_response(employee) for employee in employees]
            
        except Exception as e:
            logger.error(f"Erro ao listar funcionários com filtros: {e}")
            raise Exception(f"Erro interno do servidor ao listar funcionários: {str(e)}")
    
    def _convert_to_employee_response(self, employee: Employee) -> EmployeeResponse:
        """
        Converte uma entidade Employee para EmployeeResponse.
        
        Args:
            employee: Entidade do funcionário
            
        Returns:
            EmployeeResponse: DTO de resposta do funcionário
        """
        address_response = None
        if employee.address:
            address_response = AddressResponse(
                id=employee.address.id,
                street=employee.address.street,
                city=employee.address.city,
                state=employee.address.state,
                zip_code=employee.address.zip_code,
                country=employee.address.country
            )
        
        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            email=employee.email,
            phone=employee.phone,
            cpf=employee.cpf,
            status=employee.status,
            address=address_response,
            created_at=employee.created_at.isoformat() if employee.created_at else "",
            updated_at=employee.updated_at.isoformat() if employee.updated_at else ""
        )
    
    def _convert_to_employee_list_response(self, employee: Employee) -> EmployeeListResponse:
        """
        Converte uma entidade Employee para EmployeeListResponse.
        
        Args:
            employee: Entidade do funcionário
            
        Returns:
            EmployeeListResponse: DTO de resposta simplificada do funcionário
        """
        city = None
        if employee.address:
            city = employee.address.city
        
        return EmployeeListResponse(
            id=employee.id,
            name=employee.name,
            email=employee.email,
            phone=employee.phone,
            cpf=employee.cpf,
            status=employee.status,
            city=city
        )
