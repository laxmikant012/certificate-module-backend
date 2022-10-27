from routers import admin, login
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database.database import engine


app = FastAPI()

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
