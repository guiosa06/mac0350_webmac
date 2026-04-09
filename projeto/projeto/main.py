from fastapi import FastAPI, Request, Form, HTTPException, Response, Cookie, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Models import Player, Game
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select


# initializations
arquivo_sqlite = "database.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

activePlayer = None


@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield
app = FastAPI(lifespan=initFunction)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# endpoints
@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    if(activePlayer == None):
        return templates.TemplateResponse(request, "index.html", {"page": "/login"})
    return templates.TemplateResponse(request, "index.html", {"page": "/game"})

@app.get("/login", response_class=HTMLResponse)
async def showLogin(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"page": "/login"})
    return templates.TemplateResponse(request, "login.html")

@app.get("/register", response_class=HTMLResponse)
async def showRegister(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"page": "/register"})
    return templates.TemplateResponse(request, "register.html")



def searchPlayer(username: str):
    with Session(engine) as session:
        query = (
            select(Player)
            .where(Player.username == username)
        )
        return session.exec(query).all()

@app.post("/register", response_class=HTMLResponse)
def registerNewPlayer(request: Request, new_username: str = Form(...), new_pswd: str = Form(...), game_color: str = Form(...)):
    with Session(engine) as session:
        
        if(len(searchPlayer(new_username))>0):
           raise HTTPException(status_code=404, detail="Usuário já existe!")
        newPlayer = Player(username=new_username, password=new_pswd, game_color=game_color)
        session.add(newPlayer)
        session.commit()
        session.refresh(newPlayer)
        return templates.TemplateResponse(request, "login.html")
    
    
@app.post("/login", response_class=HTMLResponse)
def loginPlayer(request: Request, response: Response, username: str = Form(...), pswd: str = Form(...)):
    players = searchPlayer(username)
    
    if(len(players) == 0 or players[0].password != pswd):
        raise HTTPException(status_code=404, detail="Usuário ou senha inválidos")
    
    # response.set_cookie(key="session_user", value=username)
    global activePlayer
    activePlayer = players[0]
    return templates.TemplateResponse(request, "game.html", {"username": players[0].username, "game_color": players[0].game_color})




@app.get("/game", response_class=HTMLResponse)
async def showGame(request: Request):
    global activePlayer
    return templates.TemplateResponse(request, "game.html", {"username": activePlayer.username, "game_color": activePlayer.game_color})

@app.post("/game")
def saveScore(game: Game):
    with Session(engine) as session:
        newGame = Game(score=game.score, player_id=activePlayer.id)
        session.add(newGame)
        session.commit()
        session.refresh(newGame)
        return


@app.get("/menu", response_class=HTMLResponse)
async def showMenu(request: Request):
    return templates.TemplateResponse(request, "menu.html", {"username": activePlayer.username, "game_color": activePlayer.game_color})

@app.delete("/menu", response_class=HTMLResponse)
def logout(request: Request):
    global activePlayer
    activePlayer = None
    return templates.TemplateResponse(request, "login.html")



def listGames():
    with Session(engine) as session:
        query = select(Game).join(Player)
        return session.exec(query).all()
    
@app.get("/ranking", response_class=HTMLResponse)
async def showRanking(index: int, request: Request):
    with Session(engine) as session:
        query = select(Game).join(Player).order_by(Game.score.desc())
        games = session.exec(query).all()
        if(index*10>=len(games)):
            index-=1
        elif(index<0):
            index=0
        l = index*10
        r = l+10
        return templates.TemplateResponse(request, "ranking.html", {"games": games[l:r], "index":index, "game_color": activePlayer.game_color})

@app.delete("/ranking", response_class=HTMLResponse)
async def eraseScore(index: int, username: str, score: int, request: Request):
    with Session(engine) as session:
        player = session.exec(select(Player).where(Player.username == username)).first()
        game = session.exec(select(Game).where(Game.score == score, Game.player_id == player.id)).first()

        if(player == activePlayer):
            session.delete(game)
            session.commit()
        
        query = select(Game).join(Player).order_by(Game.score.desc())
        games = session.exec(query).all()
        if(index*10>=len(games)):
            index-=1
        elif(index<0):
            index=0
        l = index*10
        r = l+10
        return templates.TemplateResponse(request, "ranking.html", {"games": games[l:r], "index":index, "game_color": activePlayer.game_color})



@app.get("/change_color", response_class=HTMLResponse)
async def showColor(request: Request):
    return templates.TemplateResponse(request, "change_color.html", {"username": activePlayer.username, "game_color": activePlayer.game_color})

@app.put("/change_color", response_class=HTMLResponse)
def newColor(request: Request, game_color: str = Form(...)):
    global activePlayer
    with Session(engine) as session:
        player = session.exec(select(Player).where(Player.id == activePlayer.id)).first()
        player.game_color = game_color
        session.add(player)
        session.commit()
        session.refresh(player)
        activePlayer = player
        return templates.TemplateResponse(request, "change_color.html", {"username": player.username, "game_color": game_color})
