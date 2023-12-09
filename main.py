import os

import uvicorn

from service.models import User
from service.services import get_db

if __name__ == "__main__":
    os.system("alembic upgrade head")
    db = get_db()
    db = next(db)
    if "admin@mail.ru" not in [i.email for i in db.query(User).all()]:
        os.system("python create_admin.py")

    uvicorn.run(app_dir="service", app="app:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
