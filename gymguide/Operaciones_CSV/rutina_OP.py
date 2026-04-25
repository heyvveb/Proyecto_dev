import os
import csv
from typing import Optional
from gymguide.models.rutina import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "Rutinas.csv")
columns=["id","name","level","objective","duration_weeks","status"]

def ensure_file():
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()

def newID():
    try:
        with open(CSV_FILE, mode="r",newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            ids = []
            for row in reader:
                if row.get("id"):
                    try:
                        ids.append(int(row["id"]))
                    except ValueError:
                        continue

            return max(ids) + 1 if ids else 1

    except FileNotFoundError:
        return 1

def saveRutinaID(rutina:RutinaID):
    rutina_exist = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if not rutina_exist:
            writer.writeheader()
        writer.writerow(rutina.model_dump())

def createRutina(rutina:Rutina):
    ensure_file()
    id =newID()
    new_rutina=RutinaID(id=id,**rutina.model_dump())
    saveRutinaID(new_rutina)
    return new_rutina

def showRutinas(include_inactive: bool = False):
    ensure_file()
    with open(CSV_FILE) as csvfile:
        reader= csv.DictReader(csvfile)
        all_rutinas = [RutinaID(**row) for row in reader]
        if include_inactive:
            return all_rutinas
        return [r for r in all_rutinas if r.status == "active"]
    
def showRutina_ID(id:int, include_inactive: bool = False):
    ensure_file()
    with open (CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['id'])==id:
                rutina = RutinaID(**row)
                if include_inactive or rutina.status == "active":
                    return rutina
            
def updateRutina(id:int,rutina:RutinaUpdate):
    ensure_file()
    rutina_update: Optional[RutinaID]=None
    rutinas = showRutinas(include_inactive=True)
    for num, rutina_ in enumerate(rutinas):
        if rutina_.id==id:
            rutinas[num]=(rutina_update)=rutina_.model_copy(update=rutina)
    with open(CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for rutina_ in rutinas:
            writer.writerow(rutina_.model_dump())
    if rutina_update:
        return rutina_update

def deleteRutina(id:int):
    ensure_file()
    rutina_deleted: Optional[Rutina]=None
    rutinas = showRutinas(include_inactive=True)
    with open (CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for rutina_ in rutinas:
            if rutina_.id == id:
                rutina_deleted = rutina_
                rutina_.status = "inactive"
                writer.writerow(rutina_.model_dump())
            else:
                writer.writerow(rutina_.model_dump())
    if rutina_deleted:
        dict_rutina_no_id = rutina_deleted.model_dump()
        del dict_rutina_no_id["id"]
        return Rutina(**dict_rutina_no_id)
    
def showRutinasLevel(level: str):
    ensure_file()
    rutinas = []

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['level'].lower() == level.lower() and row['status'] == 'active':
                rutinas.append(RutinaID(**row))

    return rutinas

def showRutinasObjective(objective: str):
    ensure_file()
    rutinas = []

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['objective'].lower() == objective.lower() and row['status'] == 'active':
                rutinas.append(RutinaID(**row))

    return rutinas

def showRutinasName(name: str):
    ensure_file()
    rutinas = []

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if name.lower() in row['name'].lower() and row['status'] == 'active':
                rutinas.append(RutinaID(**row))

    return rutinas

def showInactiveRutinas():
    ensure_file()
    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        return [RutinaID(**row) for row in reader if row['status'] == 'inactive']

def restoreRutina(id: int):
    ensure_file()
    rutina_restored: Optional[RutinaID] = None
    rutinas = showRutinas(include_inactive=True)
    for num, rutina_ in enumerate(rutinas):
        if rutina_.id == id and rutina_.status == "inactive":
            rutinas[num] = rutina_restored = rutina_.model_copy(update={"status": "active"})
    with open(CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for rutina_ in rutinas:
            writer.writerow(rutina_.model_dump())
    if rutina_restored:
        return rutina_restored