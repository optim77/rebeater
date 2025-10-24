from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from database import Base, engine

from models import user, company, client, invitation, click

from routes import auth, clients, invitations, tracking, company, service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Client ReBetter API")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(invitations.router)
app.include_router(tracking.router)
app.include_router(company.router)
app.include_router(service.router)
