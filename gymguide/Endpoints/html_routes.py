from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.Operaciones.influencers_op import get_influencer_stats
from gymguide.Operaciones.rutina_OP import get_rutina_stats
from gymguide.Operaciones.suplemento_OP import get_suplemento_stats
from gymguide.Operaciones.ejercicio_OP import get_ejercicio_stats, showEjercicios, showEjerciciosName, showEjerciciosMuscle
from gymguide.Operaciones.influencers_op import showInfluencers, showInfluencersName, showInfluencersCategory
from gymguide.Operaciones.rutina_OP import showRutinas, showRutinasName, showRutinasLevel, showRutinasObjective
from gymguide.Operaciones.suplemento_OP import showSuplementos, showSuplementosName, showSuplementosType
from sqlalchemy import select
from gymguide.models.models_sql import InfluencerModel, RutinaModel, SuplementoModel, EjercicioModel
import os

router_html = APIRouter(tags=["Pages"])

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
print(f"[GYMGUIDE] Templates directory: {os.path.abspath(templates_dir)}")
jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    auto_reload=False
)
jinja_env.cache = None


def render(name: str, context: dict) -> HTMLResponse:
    template = jinja_env.get_template(name)
    return HTMLResponse(template.render(**context))


@router_html.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    istats = await get_influencer_stats(db)
    rstats = await get_rutina_stats(db)
    sstats = await get_suplemento_stats(db)
    estats = await get_ejercicio_stats(db)
    return render("index.html", {
        "request": request,
        "istats": istats,
        "rstats": rstats,
        "sstats": sstats,
        "estats": estats,
        "total_active": istats["active"] + rstats["active"] + sstats["active"] + estats["active"]
    })


@router_html.get("/influencers", response_class=HTMLResponse)
async def influencers_page(request: Request, db: AsyncSession = Depends(get_db)):
    influencers = await showInfluencers(db, include_inactive=False)
    return render("influencers.html", {
        "request": request,
        "influencers": influencers
    })


@router_html.get("/rutinas", response_class=HTMLResponse)
async def rutinas_page(request: Request, db: AsyncSession = Depends(get_db)):
    rutinas = await showRutinas(db, include_inactive=False)
    return render("rutinas.html", {
        "request": request,
        "rutinas": rutinas
    })


@router_html.get("/suplementos", response_class=HTMLResponse)
async def suplementos_page(request: Request, db: AsyncSession = Depends(get_db)):
    suplementos = await showSuplementos(db, include_inactive=False)
    return render("suplementos.html", {
        "request": request,
        "suplementos": suplementos
    })


@router_html.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_page(request: Request, db: AsyncSession = Depends(get_db)):
    ejercicios = await showEjercicios(db, include_inactive=False)
    return render("ejercicios.html", {
        "request": request,
        "ejercicios": ejercicios
    })


@router_html.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: AsyncSession = Depends(get_db)):
    istats = await get_influencer_stats(db)
    rstats = await get_rutina_stats(db)
    sstats = await get_suplemento_stats(db)
    estats = await get_ejercicio_stats(db)
    return render("dashboard.html", {
        "request": request,
        "istats": istats,
        "rstats": rstats,
        "sstats": sstats,
        "estats": estats
    })


@router_html.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "", db: AsyncSession = Depends(get_db)):
    results = {"influencers": [], "rutinas": [], "suplementos": [], "ejercicios": []}
    if q:
        results["influencers"] = await showInfluencersName(db, q)
        results["rutinas"] = await showRutinasName(db, q)
        results["suplementos"] = await showSuplementosName(db, q)
        results["ejercicios"] = await showEjerciciosName(db, q)
    return render("search.html", {
        "request": request,
        "q": q,
        "results": results
    })
