import os
from sqlmodel import Session, create_engine, SQLModel
from typing import Annotated
from fastapi import Depends, FastAPI
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
