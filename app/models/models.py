from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    BigInteger,
    Float,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    law = Column(String)
    status = Column(String)
    company = Column(BigInteger)
    type_purchase = Column(String)
    site = Column(String)
    code = Column(BigInteger)
    price = Column(Float)
    purchase_id = Column(Integer)
    date_posted = Column(Date, default=datetime.utcnow())
    date_updated = Column(Date)

    codes = relationship("ContractFile", back_populates="contract")


class ContractFile(Base):
    __tablename__ = 'contractfiles'

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger, ForeignKey('contractfiles.code'))
    name = Column(Text)
    link = Column(Text)

    contract = relationship("Contract", back_populates="codes")


class Site(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    # site = Column(Text)
