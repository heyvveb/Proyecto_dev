from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.Operaciones.influencers_op import get_influencer_stats, showInfluencers, showInfluencersName, showInfluencersCategory, showInfluencer_ID, get_influencer_suplementos
from gymguide.Operaciones.rutina_OP import get_rutina_stats, showRutinas, showRutinasName, showRutinasLevel, showRutinasObjective, showRutina_ID, get_rutina_ejercicios, get_rutina_influencers
from gymguide.Operaciones.suplemento_OP import get_suplemento_stats, showSuplementos, showSuplementosName, showSuplementosType, showSuplemento_ID, get_suplemento_influencers
from gymguide.Operaciones.ejercicio_OP import get_ejercicio_stats, showEjercicios, showEjerciciosName, showEjerciciosMuscle, showEjercicio_ID, get_ejercicio_rutinas
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
async def influencers_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        influencers = await showInfluencers(db, include_inactive=True)
        influencers = [r for r in influencers if r.status == "inactive"]
    else:
        influencers = await showInfluencers(db, include_inactive=False)
    return render("influencers.html", {
        "request": request,
        "influencers": influencers,
        "showing_inactive": showing_inactive
    })


@router_html.get("/rutinas", response_class=HTMLResponse)
async def rutinas_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        rutinas = await showRutinas(db, include_inactive=True)
        rutinas = [r for r in rutinas if r.status == "inactive"]
    else:
        rutinas = await showRutinas(db, include_inactive=False)
    return render("rutinas.html", {
        "request": request,
        "rutinas": rutinas,
        "showing_inactive": showing_inactive
    })


@router_html.get("/suplementos", response_class=HTMLResponse)
async def suplementos_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        suplementos = await showSuplementos(db, include_inactive=True)
        suplementos = [r for r in suplementos if r.status == "inactive"]
    else:
        suplementos = await showSuplementos(db, include_inactive=False)
    return render("suplementos.html", {
        "request": request,
        "suplementos": suplementos,
        "showing_inactive": showing_inactive
    })


@router_html.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        ejercicios = await showEjercicios(db, include_inactive=True)
        ejercicios = [r for r in ejercicios if r.status == "inactive"]
    else:
        ejercicios = await showEjercicios(db, include_inactive=False)
    return render("ejercicios.html", {
        "request": request,
        "ejercicios": ejercicios,
        "showing_inactive": showing_inactive
    })


@router_html.get("/influencers/{id}", response_class=HTMLResponse)
async def influencer_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    inf = await showInfluencer_ID(db, id)
    if not inf:
        return HTMLResponse("Influencer no encontrado", status_code=404)
    suplementos = await get_influencer_suplementos(db, id)
    return render("influencer_detail.html", {
        "request": request,
        "inf": inf,
        "suplementos": suplementos
    })


@router_html.get("/rutinas/{id}", response_class=HTMLResponse)
async def rutina_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    rut = await showRutina_ID(db, id)
    if not rut:
        return HTMLResponse("Rutina no encontrada", status_code=404)
    ejercicios = await get_rutina_ejercicios(db, id)
    influencers = await get_rutina_influencers(db, id)
    return render("rutina_detail.html", {
        "request": request,
        "rut": rut,
        "ejercicios": ejercicios,
        "influencers": influencers
    })


@router_html.get("/suplementos/{id}", response_class=HTMLResponse)
async def suplemento_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    sup = await showSuplemento_ID(db, id)
    if not sup:
        return HTMLResponse("Suplemento no encontrado", status_code=404)
    influencers = await get_suplemento_influencers(db, id)
    return render("suplemento_detail.html", {
        "request": request,
        "sup": sup,
        "influencers": influencers
    })


@router_html.get("/ejercicios/{id}", response_class=HTMLResponse)
async def ejercicio_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    ej = await showEjercicio_ID(db, id)
    if not ej:
        return HTMLResponse("Ejercicio no encontrado", status_code=404)
    rutinas = await get_ejercicio_rutinas(db, id)
    return render("ejercicio_detail.html", {
        "request": request,
        "ej": ej,
        "rutinas": rutinas
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
