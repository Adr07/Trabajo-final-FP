"""
Punto de entrada de la API (FastAPI). Es la capa más externa: recibe HTTP,
delega todo en `workflow.run(...)` / `auth_login.login(...)`, y no contiene
lógica de agente.

Ejecutar:
    uvicorn agent.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import workflow
from agent.nodes import auth_login, auth_session, consulta

app = FastAPI(title="Odoo Support Agent")


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    name: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    session_token: str


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    requires_form: str | None = None


class FinalizarConsultaRequest(BaseModel):
    conversation_id: str
    session_token: str
    started_at: str


class ListarConsultasRequest(BaseModel):
    session_token: str


class ConsultaDto(BaseModel):
    start: str
    stop: str
    transcript: str
    state: str


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    try:
        token, name = auth_login.login(request.email, request.password)
    except auth_login.AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return LoginResponse(token=token, name=name)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    partner_id = auth_session.store.resolve(request.session_token)
    if partner_id is None:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada. Vuelve a iniciar sesión.")
    result = workflow.run(request.conversation_id, request.message, partner_id)
    return ChatResponse(
        conversation_id=result.conversation_id,
        response=result.response,
        requires_form=result.requires_form,
    )


@app.post("/consulta/finalizar")
def finalizar_consulta(request: FinalizarConsultaRequest) -> dict:
    partner_id = auth_session.store.resolve(request.session_token)
    if partner_id is None:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada. Vuelve a iniciar sesión.")
    consulta.finalizar(partner_id, request.conversation_id, request.started_at)
    return {"ok": True}


@app.post("/consulta/listar", response_model=list[ConsultaDto])
def listar_consultas(request: ListarConsultasRequest) -> list[ConsultaDto]:
    partner_id = auth_session.store.resolve(request.session_token)
    if partner_id is None:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada. Vuelve a iniciar sesión.")
    return consulta.listar(partner_id)
