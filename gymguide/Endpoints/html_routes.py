from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.Operaciones.influencers_op import get_influencer_stats, showInfluencersName
from gymguide.Operaciones.rutina_OP import get_rutina_stats, showRutinasName
from gymguide.Operaciones.suplemento_OP import get_suplemento_stats, showSuplementosName
from gymguide.Operaciones.ejercicio_OP import get_ejercicio_stats, showEjerciciosName
from gymguide.template_utils import render

router_html = APIRouter(tags=["Pages"])

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
