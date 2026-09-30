from pydantic import BaseModel, Field, EmailStr

class PostSchema(BaseModel):
    id: int | None = None
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

class UserSchema(BaseModel):
    fullname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
