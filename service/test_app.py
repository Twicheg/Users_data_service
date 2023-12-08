from fastapi.testclient import TestClient
from service.app import app
from service.services import token_generator

email = "AlexMurphy@mail.com"
password = "12345"
client = TestClient(app)
client.cookies = {"Bearer": token_generator(email, password)}
user_id = 0
name = "Alex"
last_name = "Murphy"


def test_create():
    global user_id

    response = client.post("/private/users", json={
        "first_name": name,
        "last_name": last_name,
        "is_admin": True,
        "email": email,
        "password": password,
        "city": 1
    }, cookies=client.cookies)
    assert response.status_code == 201

    user_id = response.json().get("id")

    assert response.json() == {
        "id": user_id,
        "first_name": name,
        "last_name": last_name,
        "other_name": None,
        "email": email,
        "phone": None,
        "birthday": None,
        "city": 1,
        "additional_info": None,
        "is_admin": True
    }


def test_login():
    response = client.post('/login/', json={"email": email,
                                            "password": password})
    assert response.status_code == 200
    assert response.json() == {
        "first_name": name,
        "last_name": last_name,
        "other_name": None,
        "email": email,
        "phone": None,
        "birthday": None,
        "is_admin": True,
        "city": 1,
        "additional_info": None
    }


def test_current_user():
    response = client.get("/users/current/", cookies=client.cookies)
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
        "first_name": name,
        "last_name": last_name,
        "other_name": None,
        "email": email,
        "phone": None,
        "birthday": None,
        "is_admin": True,
        "city": 1,
        "additional_info": None
    }


def test_patch_current_user():
    response = client.patch("/users/current/", cookies=client.cookies, json={
        "first_name": None,
        "last_name": None,
        "other_name": "Robo",
        "email": None,
        "phone": "911",
        "birthday": "1987-01-01T00:00:01"
    })
    assert response.status_code == 200
    assert response.json().get("phone") == "911"
    assert response.json().get("other_name") == "Robo"
    assert response.json().get("birthday") == "1987-01-01T00:00:01"


# def test_users_get():
#     # page = 1
#     # size = 2
#     response = client.patch(f"/users/",
#                             params={"page": 1,
#                                     "size": 2},
#                             cookies=client.cookies)
#     assert response.status_code == 200
#     assert type(response.json()) == list


def test_logout():
    response = client.get("/logout", cookies=client.cookies)
    assert response.status_code == 200
    assert response.json() == {"msg": "Successfully logout"}


def test_delete():
    response = client.delete(f"/private/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Successfully delete"}
