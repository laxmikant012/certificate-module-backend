from re import template
from urllib.request import Request
from routers import admin, login
from fastapi import FastAPI, status, UploadFile, HTTPException, Response
from fastapi import File, BackgroundTasks, Depends

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

import models
from database.database import engine, SessionLocal, get_db
import pandas as pd

app = FastAPI()

templates = Jinja2Templates(directory="templates")

models.UploadDetails.metadata.create_all(engine)

app.include_router(login.router)
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



