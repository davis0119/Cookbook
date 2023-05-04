import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from redis import Redis

app = FastAPI()
conn = Redis.from_url(os.getenv("REDIS_URL", "redis://exampleredisuri/0"))
templates = Jinja2Templates(directory="/templates")

auth_required = os.getenv("AUTH_REQUIRED", "false").lower() in ["true", "t"]


@app.get("/")
def hello_view():
    return {"Root path!"}


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


@app.post("/recipe")
def add_recipe(recipe: Recipe):
    recipe_details = f"Cuisine: {recipe.cuisine} | URL: {recipe.url}"
    conn.set(recipe.name, recipe_details)
    return {"message": f"Wrote down the details for {recipe.name}!"}


@app.get("/recipe")
def get_recipe(name: str):
    if len(name) == 0:
        raise HTTPException(status_code=400, detail="Invalid recipe.")
    value = conn.get(name)
    if value is None:
        raise HTTPException(status_code=404, detail="Recipe does not exist.")

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
