import os
import csv
from typing import Optional
from gymguide.models.influencer import *

CSV_FILE= "Influncers.csv"
columns=["id","name","Categoria","logros","red_social","rutina_recomendada_id"]

def newID():
    try:
        with open(CSV_FILE, mode="r",newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            max_id=max(int(row['id']) for row in reader)
            return max_id+1
    except (FileNotFoundError, csv.Error):
        return 1

def saveInfluencerID(influencer:InfluencerID):
    influencer_exist = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if not influencer_exist:
            writer.writeheader()
        writer.writerow(influencer.model_dump())

def createInfluencer(influencer:Influencer):
    id =newID()
    new_influencer=InfluencerID(id=id,**influencer.model_dump())
    saveInfluencerID(new_influencer)
    return new_influencer

def showInfluencers():
    with open(CSV_FILE) as csvfile:
        reader= csv.DictReader(csvfile)
        return [InfluencerID(**row) for row in reader]
    
def showInfluencer_ID(id:int):
    with open (CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['id'])==id:
                return InfluencerID(**row)
            
def updateInfluencer(id:int,influencer:Influencer):
    influencer_update: Optional[InfluencerID]=None
    influencers = showInfluencers()
    for num, influencer_ in enumerate(influencers):
        if influencer_.id==id:
            influencer[num]=(influencer_update)=influencer_.model_copy(update=influencer)
    with open(CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for influencer_ in influencers:
            writer.writerow(influencer_.model_dump())
    if influencer_update:
        return influencer_update

def deleteInfluencer(id:int):
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