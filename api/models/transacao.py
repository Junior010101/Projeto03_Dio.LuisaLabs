from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db import BaseModel


class Transacao(BaseModel):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )
    conta_id = mapped_column(
        ForeignKey("contas.id", ondelete="CASCADE"),
        nullable=False,
    )
    acao: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    status: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    valor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    efetuada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.current_timestamp(),
    )

    conta = relationship("Conta", back_populates="transacoes")
