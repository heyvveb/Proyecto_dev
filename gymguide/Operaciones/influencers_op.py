from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from gymguide.models.influencer import Influencer, InfluencerRead, InfluencerUpdate
from gymguide.models.rutina import Rutina
from gymguide.models.suplemento import Suplemento, SuplementoRead
from typing import Optional

#Crear un influencer
def createInfluencer(db: Session, influencer: Influencer) -> InfluencerRead:
    #Mirar si la rutina si existe
    if influencer.rutina_recomendada_id is not None:
        result = db.execute(select(Rutina).where(Rutina.id == influencer.rutina_recomendada_id, Rutina.status == "active"))
        if not result.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {influencer.rutina_recomendada_id} no existe")
    model = Influencer(**influencer.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return _row_to_read(model)

#Mostrar los influencers
def showInfluencers(db: Session, include_inactive: bool = False) -> list[InfluencerRead]:
    query = select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos))
    #Filtrar por estatus
    if not include_inactive:
        query = query.where(Influencer.status == "active")
    #Obetener datos y transformarlos
    result = db.execute(query.order_by(Influencer.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]

#Mostrar un influencer
def showInfluencer_ID(db: Session, id: int, include_inactive: bool = False) -> Optional[InfluencerRead]:
    query = select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id)
    #Filtrar por estatus
    if not include_inactive:
        query = query.where(Influencer.status == "active")
    #Obetener datos y transformarlos
    result = db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None

#Actualizar un influencer
def updateInfluencer(db: Session, id: int, data: dict) -> Optional[InfluencerRead]:
    #Obtener datos del influencer, su rutina y sus suplementos
    result = db.execute(select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    #Verifica si la rutina existe
    if "rutina_recomendada_id" in data and data["rutina_recomendada_id"] is not None:
        r = db.execute(select(Rutina).where(Rutina.id == data["rutina_recomendada_id"], Rutina.status == "active"))
        if not r.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {data['rutina_recomendada_id']} no existe")
    #Aplica solo los campos que se entregaron
    for key, val in data.items():
        setattr(row, key, val)
    #Devuelve los cambios realizados
    db.commit()
    db.refresh(row)
    return _row_to_read(row)

#Eliminar un influencer
def deleteInfluencer(db: Session, id: int) -> Optional[Influencer]:
    #Buscar un ejercicio
    result = db.execute(select(Influencer).where(Influencer.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    #Actualiza el estado a inactivo
    row.status = "inactive"
    db.commit()
    db.refresh(row)
    return row

#Mostrar influencer por categoria
def showInfluencersCategory(db: Session, categoria: str) -> list[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.categoria.ilike(categoria), Influencer.status == "active")
        .order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]

#Mostrar ejercicios por nombre
def showInfluencersName(db: Session, name: str) -> list[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.name.ilike(f"%{name}%"), Influencer.status == "active")
        .order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]

#Mostrar los inactivos
def showInactiveInfluencers(db: Session) -> list[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.status == "inactive").order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]

#Restaurar un eliminado
def restoreInfluencer(db: Session, id: int) -> Optional[InfluencerRead]:
    #Obtener eliminado
    result = db.execute(select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id, Influencer.status == "inactive"))
    row = result.scalar_one_or_none()
    #Si no esta no devulve nada
    if not row:
        return None
    #Pasar el estado a activo
    row.status = "active"
    db.commit()
    db.refresh(row)
    return _row_to_read(row)

#Obtener la cantidad de activos y inactivos
def get_influencer_stats(db: Session) -> dict:
    total = db.execute(select(Influencer))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    cats = {}
    #Cuantos hay por categoria
    for r in all_rows:
        if r.status == "active":
            cats[r.categoria] = cats.get(r.categoria, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_category": cats}

#Obtener los suplementos de un influencer
def get_influencer_suplementos(db: Session, influencer_id: int) -> list[SuplementoRead]:
    #Obtener datos
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.suplementos)).where(Influencer.id == influencer_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    #Devuelve la lsita de suplementos
    return [SuplementoRead(
        id=s.id, name=s.name, type=s.type, brand=s.brand,
        benefits=s.benefits or "", price=s.price,
        image_url=s.image_url or "", status=s.status
    ) for s in (row.suplementos or []) if s.status == "active"]

#Actualización la lista de suplementos
def set_influencer_suplementos(db: Session, id: int, suplemento_ids: list[int]) -> Optional[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id)
    )
    row = result.scalar_one_or_none()
   
    if not row:
        return None
    #Busca los suplementos que corresponden a lso ids recibidos
    if suplemento_ids:
        #Busca los suplementos 
        sups = db.execute(select(Suplemento).where(Suplemento.id.in_(suplemento_ids)))
        row.suplementos = list(sups.scalars().all())
    else:
        row.suplementos = []
    db.commit()
    db.refresh(row)
    return _row_to_read(row)

#Forma en la que se devuelven los datos
def _row_to_read(row: Influencer) -> InfluencerRead:
    rutina_nombre = row.rutina_recomendada.name if row.rutina_recomendada else None
    suplemento_ids = [s.id for s in (row.suplementos or []) if s.status == "active"]
    return InfluencerRead(
        id=row.id,
        name=row.name,
        categoria=row.categoria,
        logros=row.logros or "",
        red_social=row.red_social or "",
        rutina_recomendada_id=row.rutina_recomendada_id,
        rutina_recomendada_nombre=rutina_nombre,
        suplemento_ids=suplemento_ids,
        image_url=row.image_url or "",
        status=row.status
    )
