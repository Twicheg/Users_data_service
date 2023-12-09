from fastapi.testclient import TestClient
from service.app import app
from service.services import token_generator

email = "Alex________Murphy@mail.com"
password = "12345"
client = TestClient(app)
client.cookies = {"Bearer": token_generator(email, password)}
user_id = 0
name = "Alex"
last_name = "Murphy"
city_id = 0


def test_create_city_for_tests():
    response = client.post("/city", json={"id": 11119999, "name": "London"})
    assert response.status_code == 201
    global city_id
    city_id = response.json().get("id")


def test_create():
    global user_id

    response = client.post("/private/users", json={
        "first_name": name,
        "last_name": last_name,
        "is_admin": True,
        "email": email,
        "password": password,
        "city": city_id
    }, params={"cheat_for_test": 777})
    assert response.status_code == 201
    user_id = response.json().get("id")

    assert response.json() == {
        "id": user_id,
        "first_name": name,
        "last_name": last_name,
        "other_name": "not specified",
        "email": email,
        "phone": "not specified",
        "birthday": "2000-01-01",
        "city": city_id,
        "additional_info": "not specified",
        "is_admin": True
    }


def test_login():
    response = client.post('/login/', json={"email": email,
                                            "password": password})
    assert response.status_code == 200
    assert response.json() == {
        "first_name": name,
        "last_name": last_name,
        "other_name": "not specified",
        "email": email,
        "phone": "not specified",
        "birthday": "2000-01-01",
        "is_admin": True,
    }


def test_current_user():
    response = client.get("/users/current/", )
    assert response.status_code == 200
    assert response.json() == {
        "first_name": name,
        "last_name": last_name,
        "other_name": "not specified",
        "email": email,
        "phone": "not specified",
        "birthday": "2000-01-01",
        "is_admin": True,
    }


def test_patch_current_user():
    response = client.patch("/users/current/", json={
        "first_name": "Alex",
        "other_name": "Robo",
        "phone": "911",
    })
    assert response.status_code == 200
    assert response.json().get("phone") == "911"
    assert response.json().get("other_name") == "Robo"


def test_users_get():
    page = 1
    size = 2
    response = client.get(f"/users/",
                          params={"page": page,
                                  "size": size}, )
    assert response.status_code == 200
    assert type(response.json().get("data")) == list
    assert len(response.json().get("data")) == size


def test_logout():
    response = client.get("/logout")
    assert response.status_code == 200
    assert response.json() == {"msg": "Successfully logout"}


def test_delete():
    response = client.delete(f"/private/users/{user_id}")
    assert response.status_code == 204


def test_delete_city():
    response = client.delete(f"/city/{city_id}")
    assert response.status_code == 204


def test_authenticate():
    page = 1
    size = 2
    client.cookies = None
    response = client.get(f"/users/",
                          params={"page": page,
                                  "size": size})
    assert response.status_code == 401
