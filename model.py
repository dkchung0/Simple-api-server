from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str = "Thorfinn"
    age: int = "28"
    

# class UserDELETE(BaseModel):
#     name: str = "Thorfinn"
    

