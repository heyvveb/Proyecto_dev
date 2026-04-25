import os
import csv
from typing import Optional
from gymguide.models.influencer import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "Influencers.csv")
columns=["id","name","Categoria","logros","red_social","rutina_recomendada_id"]

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

def saveInfluencerID(influencer:InfluencerID):
    influencer_exist = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if not influencer_exist:
            writer.writeheader()
        writer.writerow(influencer.model_dump())

def createInfluencer(influencer:Influencer):
    ensure_file()
    id =newID()
    new_influencer=InfluencerID(id=id,**influencer.model_dump())
    saveInfluencerID(new_influencer)
    return new_influencer

def showInfluencers():
    ensure_file()
    with open(CSV_FILE) as csvfile:
        reader= csv.DictReader(csvfile)
        return [InfluencerID(**row) for row in reader]
    
def showInfluencer_ID(id:int):
    ensure_file()
    with open (CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['id'])==id:
                return InfluencerID(**row)
            
def updateInfluencer(id:int,influencer:InfluencerUpdate):
    ensure_file()
    influencer_update: Optional[InfluencerID]=None
    influencers = showInfluencers()
    for num, influencer_ in enumerate(influencers):
        if influencer_.id==id:
            influencers[num]=(influencer_update)=influencer_.model_copy(update=influencer)
    with open(CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for influencer_ in influencers:
            writer.writerow(influencer_.model_dump())
    if influencer_update:
        return influencer_update

def deleteInfluencer(id:int):
    ensure_file()
    influencer_deleted: Optional[Influencer]=None
    influencers = showInfluencers()
    with open (CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for influencer_ in influencers:
            if influencer_.id == id:
                influencer_deleted = influencer_
                continue
            writer.writerow(influencer_.model_dump())
    if influencer_deleted:
        dict_influencer_no_id = influencer_deleted.model_dump()
        del dict_influencer_no_id["id"]
        return Influencer(**dict_influencer_no_id)
    
def showInfluencersCategory(categoria: str):
    ensure_file()
    influencers = []

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Categoria'].lower() == categoria.lower():
                influencers.append(InfluencerID(**row))

    return influencers