from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from gymguide.database import SessionDep
from gymguide.Operaciones.influencers_op import get_influencer_stats, showInfluencersName
from gymguide.Operaciones.rutina_OP import get_rutina_stats, showRutinasName
from gymguide.Operaciones.suplemento_OP import get_suplemento_stats, showSuplementosName
from gymguide.Operaciones.ejercicio_OP import get_ejercicio_stats, showEjerciciosName
from gymguide.template_utils import render

router_html = APIRouter(tags=["Pages"])

#Incio de la pagina
@router_html.get("/", response_class=HTMLResponse)
def index(request: Request, db: SessionDep):
    # Obtiene estadísticas de cada módulo
    istats = get_influencer_stats(db)
    rstats = get_rutina_stats(db)
    sstats = get_suplemento_stats(db)
    estats = get_ejercicio_stats(db)
    # Renderiza la página principal
    return render("index.html", {
        "request": request,
        "istats": istats,
        "rstats": rstats,
        "sstats": sstats,
        "estats": estats,
        # Total de registros activos
        "total_active": istats["active"] + rstats["active"] + sstats["active"] + estats["active"]
    })

#Dashboard
@router_html.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: SessionDep):
    # Obtiene estadísticas generales
    istats = get_influencer_stats(db)
    rstats = get_rutina_stats(db)
    sstats = get_suplemento_stats(db)
    estats = get_ejercicio_stats(db)
    # Renderiza la vista del dashboard
    return render("dashboard.html", {
        "request": request,
        "istats": istats,
        "rstats": rstats,
        "sstats": sstats,
        "estats": estats
    })
#Resultados de la busqueda
@router_html.get("/search", response_class=HTMLResponse)
def search_page(request: Request, db: SessionDep, q: str = ""):
    # Diccionario para almacenar resultados
    results = {"influencers": [], "rutinas": [], "suplementos": [], "ejercicios": []}
    # Realiza búsqueda si existe
    if q:
        results["influencers"] = showInfluencersName(db, q)
        results["rutinas"] = showRutinasName(db, q)
        results["suplementos"] = showSuplementosName(db, q)
        results["ejercicios"] = showEjerciciosName(db, q)
    # Renderiza la vista de búsqueda
    return render("search.html", {
        "request": request,
        "q": q,
        "results": results
    })
