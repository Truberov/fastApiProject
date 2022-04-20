from typing import List, Optional

from pydantic import BaseModel


"""
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class ContractCreate(UserBase):
    law: string
    status: string
    company: BigInteger
    type_purchase: string
    site: string
    code: integer
    price: float
    purchase_id: integer
    date_posted: date


class Contract(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True
"""