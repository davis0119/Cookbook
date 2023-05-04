import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from redis import Redis

app = FastAPI()
conn = Redis.from_url(os.getenv("REDIS_URL", "redis://exampleredisuri/0"))
templates = Jinja2Templates(directory="/templates")

security = HTTPBasic()
auth_required = os.getenv("AUTH_REQUIRED", "false").lower() in ["true", "t"]


def get_admin_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if not auth_required:
        return "guestuser"
    return credentials.username


@app.get("/hello")
def hello_view(name: str = "Toph"):
    return {"message": f"Hello there, {name}!"}


class Recipe(BaseModel):
    name: str
    cuisine: str
    url: str

    def to_dict(self):
        return {
            "name": self.name,
            "cuisine": self.cuisine,
            "url": self.url,
        }
recipes = []


@app.post("/recipe")
def add_recipe(recipe: Recipe):
    recipe_details = f"Cuisine: {recipe.cuisine} | URL: {recipe.url}"
    conn.set(recipe.name, recipe_details)
    return {"message": f"Wrote down the details for {recipe.name}!"}


@app.get("/recipe")
def get_recipe(name: str):
    if len(name) == 0:
        raise HTTPException(status_code=400, detail="Please search for a valid recipe.")
    value = conn.get(name)
    if value is None:
        raise HTTPException(status_code=404, detail="We do not have the details for this recipe.")

    return {"name": name, "recipe": value}


@app.get("/info", response_class=HTMLResponse)
def get_info(request: Request):
    recipe_names = conn.keys()
    recipe_dict = dict(
        [
            (name.decode("utf-8"), conn.get(name).decode("utf-8"))
            for name in recipe_names
        ]
    )
    return templates.TemplateResponse(
        "info.html.j2", {"request": request, "recipes": recipe_dict}
    )










# class Bender(BaseModel):
#     name: str
#     element: str

# @app.post("/bender")
# def add_bender(bender: Bender):
#     conn.set(bender.name, bender.element)
#     return {"message": f"Set element for {bender.name}!"}


# @app.get("/bender")
# def get_bender(name: str):
#     if len(name) == 0:
#         raise HTTPException(status_code=400, detail="Bender must have a name.")
#     value = conn.get(name)
#     if value is None:
#         raise HTTPException(status_code=404, detail="bender not found.")

#     return {"name": name, "element": value}


# @app.get("/info", response_class=HTMLResponse)
# def get_info(request: Request):
#     bender_names = conn.keys()
#     bender_dict = dict(
#         [
#             (name.decode("utf-8"), conn.get(name).decode("utf-8"))
#             for name in bender_names
#         ]
#     )
#     return templates.TemplateResponse(
#         "info.html.j2", {"request": request, "benders": bender_dict}
#     )
