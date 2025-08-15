from sqlalchemy import Column, Integer, String, DECIMAL, DATE, TEXT, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.src.infrastructure.driven.database.connection_mysql import Base
from typing import Optional
from decimal import Decimal
from datetime import date


class Sale(Base):
    """
    Entidade Sale que representa a tabela sales no banco de dados.
    """
    __tablename__ = 'sales'

    # Status possíveis para vendas
    STATUS_PENDENTE = "Pendente"
    STATUS_CONFIRMADA = "Confirmada"
    STATUS_PAGA = "Paga"
    STATUS_ENTREGUE = "Entregue"
    STATUS_CANCELADA = "Cancelada"
    
    VALID_STATUSES = [STATUS_PENDENTE, STATUS_CONFIRMADA, STATUS_PAGA, STATUS_ENTREGUE, STATUS_CANCELADA]

    # Formas de pagamento possíveis
    PAYMENT_A_VISTA = "À vista"
    PAYMENT_CARTAO_CREDITO = "Cartão de crédito"
    PAYMENT_CARTAO_DEBITO = "Cartão de débito"
    PAYMENT_FINANCIAMENTO = "Financiamento"
    PAYMENT_CONSORCIO = "Consórcio"
    PAYMENT_PIX = "PIX"
    
    VALID_PAYMENT_METHODS = [
        PAYMENT_A_VISTA, PAYMENT_CARTAO_CREDITO, PAYMENT_CARTAO_DEBITO,
        PAYMENT_FINANCIAMENTO, PAYMENT_CONSORCIO, PAYMENT_PIX
    ]

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='RESTRICT'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='RESTRICT'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('motor_vehicles.id', ondelete='RESTRICT'), nullable=False)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=STATUS_PENDENTE)
    sale_date = Column(DATE, nullable=False)
    notes = Column(TEXT, nullable=True)
    discount_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))
    tax_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))
    commission_rate = Column(DECIMAL(5, 2), nullable=False, default=Decimal('0.00'))
    commission_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacionamentos
    client = relationship("Client", backref="sales", uselist=False)
    employee = relationship("Employee", backref="sales", uselist=False)
    vehicle = relationship("MotorVehicle", backref="sales", uselist=False)

    def __init__(self, client_id: int, employee_id: int, vehicle_id: int, total_amount: Decimal,
                 payment_method: str, sale_date: date, status: str = STATUS_PENDENTE,
                 notes: Optional[str] = None, discount_amount: Decimal = Decimal('0.00'),
                 tax_amount: Decimal = Decimal('0.00'), commission_rate: Decimal = Decimal('0.00'),
                 commission_amount: Decimal = Decimal('0.00')):
        self.client_id = client_id
        self.employee_id = employee_id
        self.vehicle_id = vehicle_id
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.status = status
        self.sale_date = sale_date
        self.notes = notes
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.commission_rate = commission_rate
        self.commission_amount = commission_amount

    @classmethod
    def create_sale(cls, client_id: int, employee_id: int, vehicle_id: int, 
                   total_amount: Decimal, payment_method: str, sale_date: date,
                   notes: Optional[str] = None, discount_amount: Decimal = Decimal('0.00'),
                   tax_amount: Decimal = Decimal('0.00'), commission_rate: Decimal = Decimal('0.00')):
        """
        Método de classe para criar uma venda.
        """
        # Calcular comissão automaticamente
        commission_amount = (total_amount - discount_amount) * (commission_rate / 100)
        
        sale = cls(
            client_id=client_id,
            employee_id=employee_id,
            vehicle_id=vehicle_id,
            total_amount=total_amount,
            payment_method=payment_method,
            sale_date=sale_date,
            status=cls.STATUS_PENDENTE,  # Status padrão sempre "Pendente"
            notes=notes,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            commission_rate=commission_rate,
            commission_amount=commission_amount
        )
        
        return sale

    def update_fields(self, total_amount: Optional[Decimal] = None, payment_method: Optional[str] = None,
                     status: Optional[str] = None, sale_date: Optional[date] = None,
                     notes: Optional[str] = None, discount_amount: Optional[Decimal] = None,
                     tax_amount: Optional[Decimal] = None, commission_rate: Optional[Decimal] = None):
        """
        Atualiza os campos da venda.
        """
        if total_amount is not None:
            self.total_amount = total_amount
        if payment_method is not None:
            self.payment_method = payment_method
        if status is not None:
            self.status = status
        if sale_date is not None:
            self.sale_date = sale_date
        if notes is not None:
            self.notes = notes
        if discount_amount is not None:
            self.discount_amount = discount_amount
        if tax_amount is not None:
            self.tax_amount = tax_amount
        if commission_rate is not None:
            self.commission_rate = commission_rate
            # Recalcular comissão quando taxa muda
            self.commission_amount = (self.total_amount - self.discount_amount) * (commission_rate / 100)

    def confirm_sale(self):
        """
        Confirma a venda.
        """
        self.status = self.STATUS_CONFIRMADA

    def mark_as_paid(self):
        """
        Marca a venda como paga.
        """
        self.status = self.STATUS_PAGA

    def mark_as_delivered(self):
        """
        Marca a venda como entregue.
        """
        self.status = self.STATUS_ENTREGUE

    def cancel_sale(self):
        """
        Cancela a venda.
        """
        self.status = self.STATUS_CANCELADA

    def calculate_final_amount(self) -> Decimal:
        """
        Calcula o valor final da venda (total - desconto + impostos).
        """
        return self.total_amount - self.discount_amount + self.tax_amount

    def is_active(self) -> bool:
        """
        Verifica se a venda está ativa (não cancelada).
        """
        return self.status != self.STATUS_CANCELADA

    def is_completed(self) -> bool:
        """
        Verifica se a venda foi completada (entregue).
        """
        return self.status == self.STATUS_ENTREGUE

    @classmethod
    def is_valid_status(cls, status: str) -> bool:
        """
        Verifica se o status é válido.
        """
        return status in cls.VALID_STATUSES

    @classmethod
    def is_valid_payment_method(cls, payment_method: str) -> bool:
        """
        Verifica se a forma de pagamento é válida.
        """
        return payment_method in cls.VALID_PAYMENT_METHODS

    def __repr__(self):
        return f"<Sale(id={self.id}, client_id={self.client_id}, total={self.total_amount}, status='{self.status}')>"
