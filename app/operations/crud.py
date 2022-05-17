from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_session
from app.models.models import Contract, ContractFiles



class ContractService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_contracts_codes(self, company: str):  # Получение кодов контрактов по инн
        return self.session.query(Contract.code).filter(Contract.company == company).all()

    def get_contracts(self, company: str):  # Получение контрактов по инн
        return self.session.query(Contract).filter(Contract.company == company).order_by(Contract.code).all()

    def get_contract_files(self, code):  # Получение файлов для контракта
        f = self.session.query(ContractFiles.name, ContractFiles.link).order_by(ContractFiles.code).filter(ContractFiles.code == code).all()
        print(f)
        return f