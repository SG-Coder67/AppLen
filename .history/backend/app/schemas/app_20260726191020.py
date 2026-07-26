from pydantic import BaseModel
class AppCreate(BaseModel):
    name:str
    price:int
class AppResponse(BaseModel):
    id:int
    name:str
    price:int
    class Config:
        from_attributes=True