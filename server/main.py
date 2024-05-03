from fastapi import FastAPI

from . import auth, companies, departments, employees, actions
from .database import engine, Base


app = FastAPI()
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(actions.router)


Base.metadata.create_all(bind=engine)
