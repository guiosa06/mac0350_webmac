from fastapi import FastAPI, Request, Response, Depends, HTTPException, Cookie, status
from typing import Annotated  
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

usuarios_db = []

@app.get("/")
def form_usuario(request: Request):
    return templates.TemplateResponse(
        request=request, name="create_user.html"
    )

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user)
    return {"usuario": user.nome}

@app.get("/login")
def form_login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )

@app.post("/login")
def login(user: Usuario, response: Response):
    usuario_encontrado = None
    nome = user.nome
    senha = user.senha
    for u in usuarios_db:
        if u.nome == nome and u.senha == senha:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário ou senha inválidos")
    
    response.set_cookie(key="session_user", value=nome)
    return {"message": "Logado com sucesso"}



def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    user = None
    for u in usuarios_db:
        if(u.nome == session_user):
            user = u

    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user


@app.get("/profile")
def mostra_perfil(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request, 
        name="profile.html", 
        context={"username": user.nome, "bio": user.bio}
    )

