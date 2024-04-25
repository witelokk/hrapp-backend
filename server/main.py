from fastapi import FastAPI

from . import auth


app = FastAPI()
app.include_router(auth.router)
