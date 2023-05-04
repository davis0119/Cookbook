from fastapi.testclient import TestClient

from main import app

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
#     expected_msg = "Wrote down the details for Lasagna!"
#     response = client.post("/recipe", json=recipe)
#     assert response.status_code == 200
#     assert response.json() == {"message": expected_msg}

# def test_get_recipe():
#     conn.set("Pasta", "Cuisine: Italian | URL: https://example.com/pasta")
#     response = client.get("/recipe?name=Pasta")
#     recipe_str = "Cuisine: Italian | URL: https://example.com/pasta"
#     assert response.status_code == 200
#     assert response.json() == {"name": "Pasta", "recipe": recipe_str}
