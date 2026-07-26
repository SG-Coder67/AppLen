from sqlalchemy import Column, Integer, String
from app.database import Base
class App(Base):
    __tablename__="apps"
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String)
    price=Column(Integer)