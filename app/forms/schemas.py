from typing import List, Optional

from pydantic import BaseModel


class ContractForm(BaseModel):
    name: str
    law: str
    status: str
    company: str
    type_purchase: str
    site: str
    code: str
    price: float
    purchase_id: str
    date_posted: str


class ContractFilesForm(BaseModel):
    name: str
    link: str


class ContractInfo(ContractForm):
    files: List = []
