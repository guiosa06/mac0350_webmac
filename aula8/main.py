from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


templates = Jinja2Templates(directory="templates")

curtidas = 0

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/curtir", response_class=HTMLResponse)
def curtir(request: Request):
    global curtidas
    curtidas = curtidas+1
    return templates.TemplateResponse(
        request=request, 
        name="contador.html", 
        context={"curtidas": curtidas}
    )

@app.delete("/curtir", response_class=HTMLResponse)
def resetar_curtidas(request: Request):
    global curtidas
    curtidas = 0
    return templates.TemplateResponse(
        request=request,
        name="contador.html",
        context={"curtidas": curtidas}
    )

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/curtidas"})

@app.get("/curtidas", response_class=HTMLResponse)
async def tab_curtidas(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/curtidas"})
    return templates.TemplateResponse(request, "curtidas.html")

@app.get("/jupyter", response_class=HTMLResponse)
async def tab_jupyter(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/jupyter"})
    return templates.TemplateResponse(request, "jupyter.html")

@app.get("/professor", response_class=HTMLResponse)
async def tab_professor(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/professor"})
    return templates.TemplateResponse(request, "professor.html")