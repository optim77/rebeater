from fastapi import FastAPI
from fastapi_pagination import add_pagination

from database import Base, engine

from models import user, company, client, invitation, click

from routes import auth, clients, invitations, tracking, company

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Client ReBetter API")
add_pagination(app)
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(invitations.router)
app.include_router(tracking.router)
app.include_router(company.router)
