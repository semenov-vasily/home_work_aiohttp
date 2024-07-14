import pydantic
from typing import Optional
from models import Session, User


# Проверка правильности заполнения полей таблицы User
class BaseUser(pydantic.BaseModel):
    name: str
    password: str

    @pydantic.field_validator("password")
    @classmethod
    def secure_password(cls, value):
        if len(value) < 5:
            raise ValueError("password small")
        return value


# При создании пользователя
class UserCreate(BaseUser):
    pass


# При изменении пользователя
class UserUpdate(BaseUser):
    name: Optional[str]
    password: Optional[str]


# Проверка правильности заполнения полей таблицы Post
class BasePost(pydantic.BaseModel):
    heading: str
    description: str
    user_id: int

    # @pydantic.field_validator("user_id")
    # @classmethod
    # def user_se(cls, user_id):
    #     print(user_id)
    #     user = Session().get(User, user_id)
    #     print(user)
    #     if user is None:
    #         raise ValueError("not user")
    #     return user_id


# При создании объявления
class PostCreate(BasePost):
    pass


# При изменении объявления
class PostUpdate(BasePost):
    heading: Optional[str]
    description: Optional[str]
    user_id: Optional[int]
