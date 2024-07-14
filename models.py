import os
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, String, func, Text, ForeignKey

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5435")

PG_DSN = (f"postgresql+asyncpg://"
          f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
          f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


# Таблица User (пользователи)
class User(Base):
    __tablename__ = "app_user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    # Запись значений полей в словарь json
    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'registration_time': self.registration_time.isoformat()
        }


# Таблица Post (объявления)
class Post(Base):
    __tablename__ = "app_post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    heading: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    registration_time_post: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id = mapped_column(Integer, ForeignKey("app_user.id", ondelete="CASCADE"))
    user = relationship("User", lazy="joined")

    # Запись значений полей в словарь json
    @property
    def json(self):
        return {
            "id": self.id,
            "heading": self.heading,
            "description": self.description,
            "registration_time_post": self.registration_time_post.isoformat(),
            "user_id": self.user_id
        }
