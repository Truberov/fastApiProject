from fastapi import (
    APIRouter,
    Depends,
    status, Query,
)


router = APIRouter(
    prefix='/api',
    tags=['Contracts'],
)