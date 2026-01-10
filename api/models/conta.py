from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db import BaseModel


class Conta(BaseModel):
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False,
    )
    numero: Mapped[str] = mapped_column(
        String,
        nullable=True,
        unique=True,
    )
    agencia: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    saldo: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    limite: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    limite_saques: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    numero_saques: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.current_timestamp(),
    )
    ultimo_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    cliente = relationship("Cliente", back_populates="contas")
    transacoes = relationship(
        "Transacao",
        back_populates="conta",
        cascade="all, delete-orphan",
    )
