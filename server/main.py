from fastapi import FastAPI

from .routers import actions, auth, companies, departments, employees, reports

from .database import engine, Base


app = FastAPI()
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(actions.router)
app.include_router(reports.router)


Base.metadata.create_all(bind=engine)
