from typing import Optional, List
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.src.domain.ports.employee_repository import EmployeeRepositoryInterface
from app.src.domain.entities.employee_model import Employee
from app.src.domain.entities.client_model import Address
from app.src.infrastructure.driven.database.connection_mysql import get_db_session
import logging

logger = logging.getLogger(__name__)


class EmployeeRepository(EmployeeRepositoryInterface):
    """
    Implementação do repositório de funcionários usando SQLAlchemy.
    """
    
    def __init__(self):
        pass
    
    async def create_employee(self, address: Optional[Address], employee: Employee) -> Employee:
        """
        Cria um novo funcionário no banco de dados.
        
        Args:
            address: Dados do endereço (opcional)
            employee: Dados do funcionário
            
        Returns:
            Employee: O funcionário criado com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            logger.info(f"Criando funcionário no banco: {employee.name}")
            
            with get_db_session() as session:
                # Criar endereço se fornecido
                if address:
                    session.add(address)
                    session.flush()  # Para obter o ID do endereço
                    employee.address_id = address.id
                    logger.info(f"Endereço criado com ID: {address.id}")
                
                # Criar funcionário
                session.add(employee)
                session.commit()
                
                # Recarregar para ter os relacionamentos
                session.refresh(employee)
                if employee.address_id:
                    employee.address = session.get(Address, employee.address_id)
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(employee)
                if employee.address:
                    session.expunge(employee.address)
                
                logger.info(f"Funcionário criado com sucesso. ID: {employee.id}")
                return employee
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao criar funcionário: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar funcionário: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Busca um funcionário pelo ID.
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            Optional[Employee]: O funcionário encontrado ou None
        """
        try:
            logger.info(f"Buscando funcionário por ID: {employee_id}")
            
            with get_db_session() as session:
                employee = session.query(Employee).options(joinedload(Employee.address)).filter(Employee.id == employee_id).first()
                
                if employee:
                    logger.info(f"Funcionário encontrado: {employee.name}")
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(employee)
                    if employee.address:
                        session.expunge(employee.address)
                else:
                    logger.info(f"Funcionário não encontrado com ID: {employee_id}")
                
                return employee
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar funcionário por ID {employee_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar funcionário por ID {employee_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def update_employee(self, employee_id: int, address: Optional[Address], employee: Employee) -> Optional[Employee]:
        """
        Atualiza um funcionário existente.
        
        Args:
            employee_id: ID do funcionário
            address: Dados atualizados do endereço (opcional)
            employee: Dados atualizados do funcionário
            
        Returns:
            Optional[Employee]: O funcionário atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        try:
            logger.info(f"Atualizando funcionário ID: {employee_id}")
            
            with get_db_session() as session:
                # Buscar funcionário existente
                existing_employee = session.query(Employee).filter(Employee.id == employee_id).first()
                if not existing_employee:
                    logger.warning(f"Funcionário não encontrado para atualização. ID: {employee_id}")
                    return None
                
                # Atualizar endereço se fornecido
                if address:
                    if existing_employee.address_id:
                        # Atualizar endereço existente
                        existing_address = session.get(Address, existing_employee.address_id)
                        if existing_address:
                            existing_address.street = address.street
                            existing_address.city = address.city
                            existing_address.state = address.state
                            existing_address.zip_code = address.zip_code
                            existing_address.country = address.country
                            logger.info(f"Endereço atualizado. ID: {existing_address.id}")
                    else:
                        # Criar novo endereço
                        session.add(address)
                        session.flush()
                        existing_employee.address_id = address.id
                        logger.info(f"Novo endereço criado. ID: {address.id}")
                
                # Atualizar dados do funcionário
                existing_employee.name = employee.name
                existing_employee.email = employee.email
                existing_employee.phone = employee.phone
                existing_employee.cpf = employee.cpf
                existing_employee.status = employee.status
                
                session.commit()
                
                # Recarregar para ter os relacionamentos atualizados
                session.refresh(existing_employee)
                if existing_employee.address_id:
                    existing_employee.address = session.get(Address, existing_employee.address_id)
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(existing_employee)
                if existing_employee.address:
                    session.expunge(existing_employee.address)
                
                logger.info(f"Funcionário atualizado com sucesso. ID: {employee_id}")
                return existing_employee
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao atualizar funcionário {employee_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar funcionário {employee_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def update_employee_status(self, employee_id: int, status: str) -> Optional[Employee]:
        """
        Atualiza apenas o status de um funcionário.
        
        Args:
            employee_id: ID do funcionário
            status: Novo status (Ativo/Inativo)
            
        Returns:
            Optional[Employee]: O funcionário atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        try:
            logger.info(f"Atualizando status do funcionário ID: {employee_id} para: {status}")
            
            with get_db_session() as session:
                # Buscar funcionário existente
                employee = session.query(Employee).filter(Employee.id == employee_id).first()
                if not employee:
                    logger.warning(f"Funcionário não encontrado para atualização de status. ID: {employee_id}")
                    return None
                
                # Atualizar status
                employee.status = status
                session.commit()
                
                # Recarregar para ter os relacionamentos
                session.refresh(employee)
                if employee.address_id:
                    employee.address = session.get(Address, employee.address_id)
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(employee)
                if employee.address:
                    session.expunge(employee.address)
                
                logger.info(f"Status do funcionário atualizado com sucesso. ID: {employee_id}")
                return employee
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao atualizar status do funcionário {employee_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar status do funcionário {employee_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def delete_employee(self, employee_id: int) -> bool:
        """
        Remove um funcionário do banco de dados.
        
        Args:
            employee_id: ID do funcionário a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            Exception: Se houver erro na remoção
        """
        try:
            logger.info(f"Removendo funcionário ID: {employee_id}")
            
            with get_db_session() as session:
                # Buscar funcionário
                employee = session.query(Employee).filter(Employee.id == employee_id).first()
                if not employee:
                    logger.warning(f"Funcionário não encontrado para remoção. ID: {employee_id}")
                    return False
                
                # Remover funcionário (o endereço será mantido devido ao ON DELETE SET NULL)
                session.delete(employee)
                session.commit()
                
                logger.info(f"Funcionário removido com sucesso. ID: {employee_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao remover funcionário {employee_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao remover funcionário {employee_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Busca todos os funcionários com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Employee]: Lista de funcionários encontrados
        """
        try:
            logger.info(f"Buscando todos os funcionários. Skip: {skip}, Limit: {limit}")
            
            with get_db_session() as session:
                employees = (session.query(Employee)
                           .options(joinedload(Employee.address))
                           .offset(skip)
                           .limit(limit)
                           .all())
                
                # Fazer expunge para desconectar os objetos da sessão
                for employee in employees:
                    session.expunge(employee)
                    if employee.address:
                        session.expunge(employee.address)
                
                logger.info(f"Encontrados {len(employees)} funcionários")
                return employees
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar todos os funcionários: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar todos os funcionários: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """
        Busca um funcionário pelo email.
        
        Args:
            email: Email do funcionário
            
        Returns:
            Optional[Employee]: O funcionário encontrado ou None
        """
        try:
            logger.info(f"Buscando funcionário por email: {email}")
            
            with get_db_session() as session:
                employee = session.query(Employee).options(joinedload(Employee.address)).filter(Employee.email == email).first()
                
                if employee:
                    logger.info(f"Funcionário encontrado com email: {email}")
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(employee)
                    if employee.address:
                        session.expunge(employee.address)
                else:
                    logger.info(f"Funcionário não encontrado com email: {email}")
                
                return employee
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar funcionário por email {email}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar funcionário por email {email}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_employee_by_cpf(self, cpf: str) -> Optional[Employee]:
        """
        Busca um funcionário pelo CPF.
        
        Args:
            cpf: CPF do funcionário
            
        Returns:
            Optional[Employee]: O funcionário encontrado ou None
        """
        try:
            logger.info(f"Buscando funcionário por CPF: {cpf}")
            
            with get_db_session() as session:
                employee = session.query(Employee).options(joinedload(Employee.address)).filter(Employee.cpf == cpf).first()
                
                if employee:
                    logger.info(f"Funcionário encontrado com CPF: {cpf}")
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(employee)
                    if employee.address:
                        session.expunge(employee.address)
                else:
                    logger.info(f"Funcionário não encontrado com CPF: {cpf}")
                
                return employee
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar funcionário por CPF {cpf}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar funcionário por CPF {cpf}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def search_employees_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Busca funcionários por nome (busca parcial).
        
        Args:
            name: Nome ou parte do nome para buscar
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Employee]: Lista de funcionários encontrados
        """
        try:
            logger.info(f"Buscando funcionários por nome: {name}")
            
            with get_db_session() as session:
                employees = (session.query(Employee)
                           .options(joinedload(Employee.address))
                           .filter(Employee.name.contains(name))
                           .offset(skip)
                           .limit(limit)
                           .all())
                
                # Fazer expunge para desconectar os objetos da sessão
                for employee in employees:
                    session.expunge(employee)
                    if employee.address:
                        session.expunge(employee.address)
                
                logger.info(f"Encontrados {len(employees)} funcionários com nome contendo '{name}'")
                return employees
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar funcionários por nome {name}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar funcionários por nome {name}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_employees_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Busca funcionários por status.
        
        Args:
            status: Status dos funcionários (Ativo/Inativo)
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Employee]: Lista de funcionários encontrados
        """
        try:
            logger.info(f"Buscando funcionários por status: {status}")
            
            with get_db_session() as session:
                employees = (session.query(Employee)
                           .options(joinedload(Employee.address))
                           .filter(Employee.status == status)
                           .offset(skip)
                           .limit(limit)
                           .all())
                
                # Fazer expunge para desconectar os objetos da sessão
                for employee in employees:
                    session.expunge(employee)
                    if employee.address:
                        session.expunge(employee.address)
                
                logger.info(f"Encontrados {len(employees)} funcionários com status '{status}'")
                return employees
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar funcionários por status {status}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar funcionários por status {status}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
