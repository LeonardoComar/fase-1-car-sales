from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.src.domain.entities.message_model import Message
from app.src.domain.ports.message_repository import MessageRepository
from app.src.infrastructure.driven.database.connection_mysql import get_session_factory

class MessageRepositoryImpl(MessageRepository):
    
    def __init__(self):
        self.session_factory = get_session_factory()
    
    def create(self, message: Message) -> Message:
        """Criar uma nova mensagem"""
        session: Session = self.session_factory()
        try:
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_id(self, message_id: int) -> Optional[Message]:
        """Buscar mensagem por ID"""
        session: Session = self.session_factory()
        try:
            message = session.query(Message).filter(Message.id == message_id).first()
            if message:
                # Expunge o objeto da sessão para evitar problemas de sessão fechada
                session.expunge(message)
            return message
        finally:
            session.close()
    
    def find_all_with_filters(
        self, 
        status: Optional[str] = None,
        responsible_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Buscar mensagens com filtros opcionais"""
        session: Session = self.session_factory()
        try:
            query = session.query(Message)
            
            # Aplicar filtros se fornecidos
            if status:
                query = query.filter(Message.status == status)
            
            if responsible_id:
                query = query.filter(Message.responsible_id == responsible_id)
            
            if vehicle_id:
                query = query.filter(Message.vehicle_id == vehicle_id)
            
            # Ordenar por data de criação (mais recentes primeiro)
            query = query.order_by(Message.created_at.desc())
            
            # Aplicar paginação
            messages = query.offset(offset).limit(limit).all()
            
            # Expunge todos os objetos da sessão
            for message in messages:
                session.expunge(message)
            
            return messages
            
        finally:
            session.close()
    
    def update(self, message: Message) -> Message:
        """Atualizar uma mensagem"""
        session: Session = self.session_factory()
        try:
            # Buscar a mensagem atual no banco para garantir que está na sessão
            existing_message = session.query(Message).filter(Message.id == message.id).first()
            
            if not existing_message:
                raise ValueError(f"Mensagem com ID {message.id} não encontrada")
            
            # Atualizar os campos da mensagem existente
            existing_message.responsible_id = message.responsible_id
            existing_message.vehicle_id = message.vehicle_id
            existing_message.name = message.name
            existing_message.email = message.email
            existing_message.phone = message.phone
            existing_message.message = message.message
            existing_message.status = message.status
            existing_message.service_start_time = message.service_start_time
            existing_message.updated_at = message.updated_at
            
            session.commit()
            session.refresh(existing_message)
            session.expunge(existing_message)
            return existing_message
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_by_id(self, message_id: int, updates: Dict[str, Any]) -> Message:
        """Atualizar uma mensagem por ID com campos específicos"""
        session: Session = self.session_factory()
        try:
            # Buscar a mensagem
            message = session.query(Message).filter(Message.id == message_id).first()
            
            if not message:
                raise ValueError(f"Mensagem com ID {message_id} não encontrada")
            
            # Aplicar as atualizações
            for field, value in updates.items():
                if hasattr(message, field):
                    setattr(message, field, value)
            
            # Sempre atualizar o campo updated_at
            message.updated_at = datetime.utcnow()
            
            session.commit()
            session.refresh(message)
            session.expunge(message)
            return message
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete(self, message_id: int) -> bool:
        """Deletar uma mensagem"""
        session: Session = self.session_factory()
        try:
            message = session.query(Message).filter(Message.id == message_id).first()
            if message:
                session.delete(message)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def count_with_filters(
        self,
        status: Optional[str] = None,
        responsible_id: Optional[int] = None,
        vehicle_id: Optional[int] = None
    ) -> int:
        """Contar mensagens com filtros"""
        session: Session = self.session_factory()
        try:
            query = session.query(Message)
            
            if status:
                query = query.filter(Message.status == status)
            
            if responsible_id:
                query = query.filter(Message.responsible_id == responsible_id)
            
            if vehicle_id:
                query = query.filter(Message.vehicle_id == vehicle_id)
            
            return query.count()
            
        finally:
            session.close()
