import os
import csv
from typing import Optional
from gymguide.models.suplemento import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "Suplementos.csv")
columns=["id","name","type","brand","benefits","status"]

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

def saveSuplementoID(suplemento:SuplementoID):
    suplemento_exist = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if not suplemento_exist:
            writer.writeheader()
        writer.writerow(suplemento.model_dump())

def createSuplemento(suplemento:Suplemento):
    ensure_file()
    id =newID()
    new_suplemento=SuplementoID(id=id,**suplemento.model_dump())
    saveSuplementoID(new_suplemento)
    return new_suplemento

def showSuplementos(include_inactive: bool = False):
    ensure_file()
    with open(CSV_FILE) as csvfile:
        reader= csv.DictReader(csvfile)
        all_suplementos = [SuplementoID(**row) for row in reader]
        if include_inactive:
            return all_suplementos
        return [s for s in all_suplementos if s.status == "active"]
    
def showSuplemento_ID(id:int, include_inactive: bool = False):
    ensure_file()
    with open (CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['id'])==id:
                suplemento = SuplementoID(**row)
                if include_inactive or suplemento.status == "active":
                    return suplemento
            
def updateSuplemento(id:int,suplemento:SuplementoUpdate):
    ensure_file()
    suplemento_update: Optional[SuplementoID]=None
    suplementos = showSuplementos(include_inactive=True)
    for num, suplemento_ in enumerate(suplementos):
        if suplemento_.id==id:
            suplementos[num]=(suplemento_update)=suplemento_.model_copy(update=suplemento)
    with open(CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for suplemento_ in suplementos:
            writer.writerow(suplemento_.model_dump())
    if suplemento_update:
        return suplemento_update

def deleteSuplemento(id:int):
    ensure_file()
    suplemento_deleted: Optional[Suplemento]=None
    suplementos = showSuplementos(include_inactive=True)
    with open (CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for suplemento_ in suplementos:
            if suplemento_.id == id:
                suplemento_deleted = suplemento_
                suplemento_.status = "inactive"
                writer.writerow(suplemento_.model_dump())
            else:
                writer.writerow(suplemento_.model_dump())
    if suplemento_deleted:
        dict_suplemento_no_id = suplemento_deleted.model_dump()
        del dict_suplemento_no_id["id"]
        return Suplemento(**dict_suplemento_no_id)
    
def showSuplementosType(type: str):
    ensure_file()
    suplementos = []

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['type'].lower() == type.lower() and row['status'] == 'active':
                suplementos.append(SuplementoID(**row))

    return suplementos

def showSuplementosName(name: str):
    ensure_file()
    suplementos = []

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if name.lower() in row['name'].lower() and row['status'] == 'active':
                suplementos.append(SuplementoID(**row))

    return suplementos

def showInactiveSuplementos():
    ensure_file()
    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        return [SuplementoID(**row) for row in reader if row['status'] == 'inactive']

def restoreSuplemento(id: int):
    ensure_file()
    suplemento_restored: Optional[SuplementoID] = None
    suplementos = showSuplementos(include_inactive=True)
    for num, suplemento_ in enumerate(suplementos):
        if suplemento_.id == id and suplemento_.status == "inactive":
            suplementos[num] = suplemento_restored = suplemento_.model_copy(update={"status": "active"})
    with open(CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for suplemento_ in suplementos:
            writer.writerow(suplemento_.model_dump())
    if suplemento_restored:
        return suplemento_restored