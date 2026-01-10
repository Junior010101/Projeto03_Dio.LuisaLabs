from json import load

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from api.controllers import (
    auth_router,
    clientes_routes,
    contas_routes,
    transacao_routes,
)
from api.errors import register_domain_handlers, register_validation_handler

with open("api/openapi_config.json", "r", encoding="utf-8") as arquivo:
    data = load(arquivo)

tags_metadata = data["tags_metadata"]
servers = data["servers"]
description = data["description"]

api = FastAPI(
    title="API Bancária",
    version="0.1.0",
    summary="API para gestão de operações financeiras.",
    description=description,
    openapi_tags=tags_metadata,
    servers=servers,
)
register_validation_handler(api)
register_domain_handlers(api)

api.include_router(clientes_routes, tags=["cliente"])
api.include_router(auth_router, tags=["auth"])
api.include_router(contas_routes, tags=["conta"])
api.include_router(transacao_routes, tags=["transação"])

api.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_origins=[
        "http://localhost:8000",
    ],
)

if __name__ == "__main__":
    run(
        app="main:api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
