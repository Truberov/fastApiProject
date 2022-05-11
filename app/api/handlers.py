from typing import List

from fastapi import (
    APIRouter,
    Depends,
    status, Query,
)
from app.forms.schemas import ContractForm
from app.operations.crud import ContractService

router = APIRouter(
    prefix='/api',
    tags=['Contracts'],
)

@router.get(
    '/get/',
)
def get_projects(contract_service: ContractService = Depends(),
    inn: str = Query(..., description="ИНН Компании")):
    return contract_service.get_contracts(inn)
