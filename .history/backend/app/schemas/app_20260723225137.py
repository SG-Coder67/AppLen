from pydantic import BaseModel
class AppCreate(BaseModel):
    name:str
    price:int