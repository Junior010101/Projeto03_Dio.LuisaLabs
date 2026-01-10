from fastapi import APIRouter, Depends, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from api import get_session
from api.errors import (
    ClienteNaoEncontradoPeloCPF,
    ClienteNaoEncontradoPeloID,
    ClientePossuiContasNaoPodeSerDeletado,
    ClienteSemDadosNoUpdate,
)
from api.models import Cliente, Conta
from api.schemas import ClienteIn, ClienteUpdate
from api.security import adm_access_required
from api.views import ClienteError, ClienteOut

router = APIRouter(prefix="/clientes")


@router.post(
    "/",
    description="Cadastra um novo cliente no banco.",
    status_code=status.HTTP_201_CREATED,
    response_model=ClienteOut,
)
async def cadastrar_cliente(
    cliente: ClienteIn,
    session: AsyncSession = Depends(get_session),
):
    novo_cliente = Cliente(**cliente.model_dump())

    session.add(novo_cliente)
    await session.commit()
    await session.refresh(novo_cliente)

    return novo_cliente


@router.get(
    "/{cpf}",
    description="Busca um cliente no banco pelo seu CPF",
    status_code=status.HTTP_200_OK,
    response_model=ClienteOut | ClienteError,
)
async def buscar_pelo_cpf(
    cpf: str,
    session: AsyncSession = Depends(get_session),
):
    query = select(Cliente).where(Cliente.cpf == cpf)
    resultado = await session.execute(query)

    cliente = resultado.scalar_one_or_none()

    if cliente is None:
        raise ClienteNaoEncontradoPeloCPF(cpf)

    return cliente


@router.get(
    "/",
    description="Lista todos os clientes cadastrados no banco",
    status_code=status.HTTP_200_OK,
    response_model=list[ClienteOut],
    dependencies=[Depends(adm_access_required)],
)
async def listar_clientes(session: AsyncSession = Depends(get_session)):
    query = select(Cliente).order_by(Cliente.nome)
    resultado = await session.execute(query)

    return resultado.scalars().all()


@router.patch(
    "/{id}",
    description="Atualiza as informações de um cliente cadastrado no banco",
    status_code=status.HTTP_200_OK,
    response_model=ClienteOut | ClienteError,
    response_model_exclude_none=True,
    dependencies=[Depends(adm_access_required)],
)
async def atualizar_informacao_do_cliente(
    id: int,
    cliente: ClienteUpdate,
    session: AsyncSession = Depends(get_session),
):
    dados = cliente.model_dump(exclude_unset=True)

    if not dados:
        raise ClienteSemDadosNoUpdate("nome/data_nascimento/endereco")

    query = select(Cliente).where(Cliente.id == id)
    resultado = await session.execute(query)

    cliente_db = resultado.scalar_one_or_none()

    if cliente_db is None:
        raise ClienteNaoEncontradoPeloID(id)

    for campo, valor in dados.items():
        setattr(cliente_db, campo, valor)

    await session.commit()
    await session.refresh(cliente_db)

    return cliente_db


@router.delete(
    "/{id}",
    description="Remove um cliente do banco."
    " O cliente só pode ser removido se não possuir contas associadas.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(adm_access_required)],
)
async def deletar_cliente(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    query = select(Cliente).where(Cliente.id == id)
    resultado = await session.execute(query)

    cliente = resultado.scalar_one_or_none()

    if cliente is None:
        raise ClienteNaoEncontradoPeloID(id)

    stmt = select(exists().where(Conta.cliente_id == id))
    has_contas = (await session.execute(stmt)).scalar()

    if has_contas:
        raise ClientePossuiContasNaoPodeSerDeletado(id)

    await session.delete(cliente)
    await session.commit()
