from pydantic import BaseModel,ConfigDict,Field
class AppCreate(BaseModel):
    name:str=Field(
        min_length=2,
        max_length=100
    )
    price:int=Field(
        ge=0
    )
class AppResponse(BaseModel):
    id:int
    name:str
    price:int
    model_config=ConfigDict(from_attributes=True)