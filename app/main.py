from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.handlers import router as auth_router
# from app.handlers.projects import router as project_router
from app.database import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)


def get_application():
    application = FastAPI()
    origins = ["*"]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(auth_router)
    # application.include_router(project_router)
    return application


app = get_application()