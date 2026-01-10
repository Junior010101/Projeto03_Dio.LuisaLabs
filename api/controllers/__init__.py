from .auth import router as auth_router
from .cliente import router as clientes_routes
from .conta import router as contas_routes
from .transacao import router as transacao_routes

__all__ = [
    "clientes_routes",
    "auth_router",
    "contas_routes",
    "transacao_routes",
]
