from typing import List

from fastapi import (
    APIRouter,
    Depends,
    status, Query,
)
from app.forms.schemas import ContractInfo
from app.operations.crud import ContractService

router = APIRouter(
    prefix='/api',
    tags=['Contracts'],
)


@router.get(
    '/get/'
)
async def get_projects(contract_service: ContractService = Depends(),
                       INN: str = Query(..., description="ИНН Компании")):
    contracts_info = contract_service.get_contracts(INN)
    contracts = []
    for contract_info in contracts_info:
        contract = ContractInfo(**contract_info.__dict__)
        contract.files = contract_service.get_contract_files(contract.code)
        contracts.append(contract)
    return contracts
