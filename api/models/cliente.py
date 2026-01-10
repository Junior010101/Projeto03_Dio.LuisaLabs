from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db import BaseModel


class Cliente(BaseModel):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )
    nome: Mapped[str] = mapped_column(
        String(69),
        nullable=False,
    )
    cpf: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True,
    )
    data_nascimento: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    endereco: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.current_timestamp(),
    )

    contas = relationship(
        "Conta",
        back_populates="cliente",
        lazy="selectin",
    )
