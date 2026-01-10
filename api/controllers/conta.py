from hashlib import sha1

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api import get_session
from api.errors import (
    ClienteNaoEncontradoPeloID,
    ClienteSemDadosNoUpdate,
    ContaAcessoNegado,
    ContaComSaldoNaoPodeSerDeletada,
    ContaNaoEncontradaPeloID,
)
from api.models import Cliente, Conta
from api.schemas import ContaIn, ContaUpdate
from api.security import adm_access_required as adm_access
from api.security import get_current_user, is_admin, login_required
from api.views import ClienteError, ContaError, ContaOut

router = APIRouter(prefix="/contas")


@router.post(
    "/",
    description="Cria uma nova conta bancária",
    status_code=status.HTTP_201_CREATED,
    response_model=ContaOut | ClienteError,
    dependencies=[Depends(login_required)],
)
async def criar_conta_bancaria(
    conta: ContaIn,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    def token_cliente(cliente_id: int) -> str:
        return sha1(str(cliente_id).encode()).hexdigest()[:5]

    id_usuario = current_user["id_usuario"]

    cliente = await session.get(Cliente, id_usuario)

    if cliente is None:
        raise ClienteNaoEncontradoPeloID(id_usuario)

    nova_conta = Conta(
        **conta.model_dump(),
        cliente_id=id_usuario,
    )

    session.add(nova_conta)
    await session.flush()

    nova_conta.numero = (
        f"{nova_conta.agencia}-{token_cliente(id_usuario)}-{nova_conta.id}"
    )

    await session.commit()
    await session.refresh(nova_conta)

    return nova_conta


@router.get(
    "/",
    description="Lista as contas bancárias associadas ao usuário autenticado. "
    "Se a requisição for autenticada com privilégios de superusuário, "
    "retorna todas as contas do banco.",
    status_code=status.HTTP_200_OK,
    response_model=list[ContaOut] | ClienteError,
    dependencies=[Depends(login_required)],
)
async def listar_contas(
    current_user: dict = Depends(get_current_user),
    admin: bool = Depends(is_admin),
    session: AsyncSession = Depends(get_session),
):
    if admin:
        query = select(Conta).order_by(Conta.id)
        resultado = await session.execute(query)

        return resultado.scalars().all()

    id_usuario = current_user["id_usuario"]
    cliente = await session.get(Cliente, id_usuario)

    if cliente is None:
        raise ClienteNaoEncontradoPeloID(id_usuario)

    query = (
        select(Conta)
        .where(Conta.cliente_id == id_usuario)
        .order_by(
            Conta.id,
        )
    )
    resultado = await session.execute(query)
    return resultado.scalars().all()


@router.get(
    "/{id}",
    description="Busca uma conta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=ContaOut | ContaError,
    dependencies=[Depends(login_required)],
)
async def buscar_pelo_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    id_usuario = current_user["id_usuario"]
    cliente = await session.get(Cliente, id_usuario)

    if cliente is None:
        raise ClienteNaoEncontradoPeloID(id_usuario)

    query = select(Conta).where(Conta.id == id)
    resultado = await session.execute(query)

    conta = resultado.scalar_one_or_none()

    if conta is None:
        raise ContaNaoEncontradaPeloID(id)

    if conta.cliente_id != int(id_usuario):
        raise ContaAcessoNegado(id_usuario, id)

    return conta


@router.patch(
    "/{id}",
    description="Atualiza as informações de uma conta cadastrada no banco",
    status_code=status.HTTP_200_OK,
    response_model=ContaOut | ContaError,
    dependencies=[Depends(adm_access)],
)
async def atualizar_informacao_da_conta(
    id: int,
    conta: ContaUpdate,
    session: AsyncSession = Depends(get_session),
):
    dados = conta.model_dump(exclude_unset=True)

    if not dados:
        raise ClienteSemDadosNoUpdate("limite/limite_saques")

    query = select(Conta).where(Conta.id == id)
    resultado = await session.execute(query)

    conta_db = resultado.scalar_one_or_none()

    if conta_db is None:
        raise ContaNaoEncontradaPeloID(id)

    for campo, valor in dados.items():
        setattr(conta_db, campo, valor)

    await session.commit()
    await session.refresh(conta_db)

    return conta_db


@router.delete(
    "/{id}",
    description="Deleta uma conta pelo ID",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(adm_access)],
)
async def deletar_conta(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    query = select(Conta).where(Conta.id == id)
    resultado = await session.execute(query)

    conta_db = resultado.scalar_one_or_none()

    if conta_db is None:
        raise ContaNaoEncontradaPeloID(id)

    if abs(conta_db.saldo) > 1e-9:
        raise ContaComSaldoNaoPodeSerDeletada(conta_db.saldo)

    await session.delete(conta_db)
    await session.commit()
