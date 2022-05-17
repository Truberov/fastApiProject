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
    __tablename__ = 'contract'

    name = Column(String)
    law = Column(String)
    status = Column(String)
    company = Column(String)
    type_purchase = Column(String)
    site = Column(Integer, ForeignKey('site.id'))
    code = Column(String, primary_key=True)
    price = Column(Float)
    purchase_id = Column(BigInteger)
    date_posted = Column(String)
    date_updated = Column(String)


class ContractFiles(Base):
    __tablename__ = 'ContractFiles'

    code = Column(BigInteger, ForeignKey('contract.code'), primary_key=True)
    name = Column(String)
    link = Column(String)


class Site(Base):
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    sitelink = Column(Text)
    purchaselink = Column(Text)
