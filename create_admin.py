from service.models import User, City
from service.services import get_db, password_hash

city = {"name": "London"}

user = {
    "first_name": "string",
    "last_name": "string",
    "email": "admin@mail.ru",
    "hashed_password": password_hash("12345"),
    'other_name': "adminich",
    'phone': 777,
    'birthday': '1999-12-31',
    "is_admin": True,
    "city": 1,
    "additional_info": "not specified"
}

db = get_db()
db = next(db)
user = User(**user)
city = City(**city)
db.add(city)
db.commit()

db.add(user)
db.commit()



