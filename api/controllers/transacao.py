from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api import get_session
from api.errors import (
    ClienteNaoEncontradoPeloID,
    ContaAcessoNegado,
    ContaNaoEncontradaPeloID,
    TransacaoLimiteExcedido,
    TransacaoLimiteSaquesExcedido,
    TransacaoSaldoInsuficiente,
    TransacaoTipoInvalido,
)
from api.models import Cliente, Conta, Transacao
from api.schemas import TransacaoIn
from api.security import get_current_user, login_required
from api.views import ContaError, TransacaoError, TransacaoOut

router = APIRouter(prefix="/transacoes")


@router.post(
    "/",
    description="Realiza uma transação bancária e registra no sistema.",
    status_code=status.HTTP_201_CREATED,
    response_model=TransacaoOut | TransacaoError | ContaError,
    dependencies=[Depends(login_required)],
)
async def realizar_transacao(
    payload: TransacaoIn,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    async with session.begin():
        resultado = await session.execute(
            select(Conta).where(Conta.id == payload.conta_id).with_for_update()
        )
        conta = resultado.scalar_one_or_none()

        if conta is None:
            raise ContaNaoEncontradaPeloID(payload.conta_id)

        if conta.cliente_id != int(current_user["id_usuario"]):
            raise ContaAcessoNegado(
                current_user["id_usuario"],
                conta_id_field=payload.conta_id,
            )

        status_transacao = True
        agora = datetime.now(timezone.utc)

        if payload.acao not in {"SAQUE", "DEPOSITO"}:
            raise TransacaoTipoInvalido(payload.acao)

        if payload.acao == "SAQUE":
            if conta.ultimo_reset.date() != agora.date():
                conta.numero_saques = 0
                conta.ultimo_reset = agora

            if conta.numero_saques >= conta.limite_saques:
                status_transacao = False
                erro = "LIMITE_SAQUES"

            elif payload.valor > conta.saldo:
                status_transacao = False
                erro = "SALDO"

            elif payload.valor > conta.limite:
                status_transacao = False
                erro = "LIMITE_VALOR"

        if status_transacao:
            if payload.acao == "SAQUE":
                conta.saldo -= payload.valor
                conta.numero_saques += 1
            else:
                conta.saldo += payload.valor

        transacao = Transacao(
            conta_id=conta.id,
            acao=payload.acao,
            valor=payload.valor,
            status=status_transacao,
        )

        session.add(transacao)

    await session.refresh(transacao)

    if not status_transacao:
        if erro == "LIMITE_SAQUES":
            raise TransacaoLimiteSaquesExcedido()
        if erro == "LIMITE_VALOR":
            raise TransacaoLimiteExcedido()
        raise TransacaoSaldoInsuficiente(conta.saldo)

    return transacao


@router.get(
    "/{id}",
    description="Puxa o extrato bancario de uma conta.",
    status_code=status.HTTP_200_OK,
    response_model=list[TransacaoOut],
    dependencies=[Depends(login_required)],
)
async def mostrar_extrato(
    id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    id_usuario = current_user["id_usuario"]
    cliente = await session.get(Cliente, id_usuario)

    if cliente is None:
        raise ClienteNaoEncontradoPeloID(id_usuario)

    resultado = await session.execute(select(Conta).where(Conta.id == id))
    conta = resultado.scalar_one_or_none()

    if conta is None:
        raise ContaNaoEncontradaPeloID(id)

    if conta.cliente_id != int(current_user["id_usuario"]):
        raise ContaAcessoNegado(
            current_user["id_usuario"],
            conta_id_field=id,
        )

    query = (
        select(Transacao)
        .where(Transacao.conta_id == id)
        .order_by(
            Transacao.id,
        )
    )

    resultado = await session.execute(query)
    return resultado.scalars().all()
