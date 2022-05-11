from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_session
from app.models.models import Contract



class ContractService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_contracts(self, code: str):  # Получение контрактов по инн
        return self.session.query(Contract).filter(Contract.company == code).all()