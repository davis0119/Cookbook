import json
from fastapi.testclient import TestClient

from main import app, conn

client = TestClient(app)

def test_hello_view():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello there, Toph!"}

# def test_add_recipe():
#     recipe = {
#         "name": "Lasagna",
#         "cuisine": "Italian",
#         "url": "https://example.com/lasagna"
#     }
#     response = client.post("/recipe", json=recipe)
#     assert response.status_code == 200
#     assert response.json() == {"message": "Wrote down the details for Lasagna!"}
#     assert conn.get("Lasagna") == b"Cuisine: Italian | URL: https://example.com/lasagna"

# def test_get_recipe():
#     conn.set("Pasta", "Cuisine: Italian | URL: https://example.com/pasta")
#     response = client.get("/recipe?name=Pasta")
#     assert response.status_code == 200
#     assert response.json() == {"name": "Pasta", "recipe": "Cuisine: Italian | URL: https://example.com/pasta"}
