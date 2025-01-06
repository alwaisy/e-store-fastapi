import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UserStoreSchema(BaseModel):
    f_name: str = Field(max_length=25)
    l_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "f_name": "John",
                "l_name": "Doe",
                "username": "johndoe",
                "email": "b0w6R@example.com",
                "password": "password123",
            }
        }
    }


class UserLoginSchema(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class UserSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    f_name: str
    l_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    update_at: datetime
