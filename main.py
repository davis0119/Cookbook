import os

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from redis import Redis

app = FastAPI()
conn = Redis.from_url(os.getenv("REDIS_URL", "redis://exampleredisuri/0"))
templates = Jinja2Templates(directory="/templates")

class Recipe(BaseModel):
    name: str
    cuisine: str
    url: str

@app.post('/recipes/')
def add_recipe(recipe: Recipe):
    conn.set(recipe.name, recipe.cuisine, recipe.url)
    return {"message": "Recipe added successfully."}


# @app.get('/recipes/{cuisine}')
# def get_recipes(cuisine: str):
#     recipes = redis.smembers(cuisine)
#     return {'recipes': [recipe.decode() for recipe in recipes]}
