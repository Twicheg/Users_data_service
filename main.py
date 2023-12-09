import os

import uvicorn

if __name__ == "__main__":
   #os.system('alembic revision --autogenerate -m "<3" ')
    os.system("alembic upgrade head")
    uvicorn.run(app_dir="service", app="app:app", host="0.0.0.0", port=8000, log_level="info", reload=True)