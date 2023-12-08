from fastapi.testclient import TestClient
from service.app import app
from fastapi import FastAPI, Response , Cookie
from service.services import token_generator

client = TestClient(app)



def test_create():
    head = {"Cookie": "Bearer=" + token_generator("AlexMurphy@mail.com", "12345")}
    # client.headers=z
    client.cookies=head
    #print(client.headers,client.cookies)
    response = client.post("/private/users", json={
        "first_name": "Alex",
        "last_name": "Murphy",
        "is_admin": True,
        "email": "AlexM@mail.com",
        "password": "12345",
        "city": 1
    },)
    #print(z,client.cookies)
    assert response.status_code == 201
    # assert response.json() == {
    #     "id": 1,
    #     "first_name": "Alex",
    #     "last_name": "Murphy",
    #     "other_name": None,
    #     "email": "Alex@mail.com",
    #     "phone": None,
    #     "birthday": None,
    #     "city": 1,
    #     "additional_info": None,
    #     "is_admin": None
    # }

# def test_login():
#     global JWT
#     response = client.post('/login/', json={"email": "12345@mail.com", "password": "12345"})
#     assert response.json() == {
#         "first_name": "zzz",
#         "last_name": "zz",
#         "other_name": "AAAA",
#         "email": "12345@mail.com",
#         "phone": "1333-555",
#         "birthday": "2023-12-07T14:09:45",
#         "is_admin": True,
#         "city": None,
#         "additional_info": None
#     }
#     assert response.status_code == 200
