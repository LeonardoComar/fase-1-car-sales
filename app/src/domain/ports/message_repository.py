from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.src.domain.entities.message_model import Message

class MessageRepository(ABC):
    
    @abstractmethod
    def create(self, message: Message) -> Message:
        """Criar uma nova mensagem"""
        pass
    
    @abstractmethod
    def find_by_id(self, message_id: int) -> Optional[Message]:
        """Buscar mensagem por ID"""
        pass
    
    @abstractmethod
    def find_all_with_filters(
        self, 
        status: Optional[str] = None,
        responsible_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Buscar mensagens com filtros opcionais"""
        pass
    
    @abstractmethod
    def update(self, message: Message) -> Message:
        """Atualizar uma mensagem"""
        pass
    
    @abstractmethod
    def update_by_id(self, message_id: int, updates: Dict[str, Any]) -> Message:
        """Atualizar uma mensagem por ID com campos específicos"""
        pass
    
    @abstractmethod
    def delete(self, message_id: int) -> bool:
        """Deletar uma mensagem"""
        pass
    
    @abstractmethod
    def count_with_filters(
        self,
        status: Optional[str] = None,
        responsible_id: Optional[int] = None,
        vehicle_id: Optional[int] = None
    ) -> int:
        """Contar mensagens com filtros"""
        pass
