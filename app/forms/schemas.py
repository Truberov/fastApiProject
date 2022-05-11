from pydantic import BaseModel


class ContractForm(BaseModel):
    name: str
    law: str
    status: str
    company: int
    type_purchase: str
    site: str
    code: str
    price: float
    purchase_id: int
    date_posted: str


class ContractFilesForm(BaseModel):
    code: str
    name: str
    link: str


class SiteForm(BaseModel):
    name: str
    sitelink: str
    purchaselink: str

