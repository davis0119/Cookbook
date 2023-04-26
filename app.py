import time

import redis
from flask import Flask, jsonify, request
from pydantic import BaseModel

app = Flask(__name__)
cache = redis.Redis(host="redis", port=6379)

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

@app.route('/recipes', methods=['POST'])
def create_recipe():
    data = request.get_json()
    recipe = Recipe(**data)
    recipes.append(recipe.to_dict())
    return jsonify(recipe.to_dict())

@app.route('/recipes', methods=['GET'])
def get_recipes():
    return jsonify(recipes)


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr("hits")
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route("/")
def hello():
    count = get_hit_count()
    return "Hello World! I have been seen {} times.\n".format(count)

