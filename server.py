from urllib import request

from aiohttp import web
from models import Base, engine, User, Session, Post
from sqlalchemy.exc import IntegrityError
import json
import bcrypt
from pydantic import ValidationError
from schema import UserCreate, UserUpdate, PostCreate, PostUpdate


# Функция преобразования пароля в хеш-значение
def hash_password(password: str) -> str:
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


# Функция сравнения хеш-значения вводимого пароля с хеш-значением пароля в бд
def check_password(password: str, hashed_password: str) -> bool:
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)


app = web.Application()


# Функция создания и очистки таблиц в бд
async def orm_context(app: web.Application):
    print('start')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('stop')


# Заменитель менеджера контекста, открытие и закрытие сессии
@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


# Функция для обработки исключений
def get_error(error_cls, error_description):
    return error_cls(
        text=json.dumps({"error": error_description}), content_type="application/json")


# Функция проверки данных, записываемых в соответствующие поля таблиц бд
def validate(json_data, schema_cls):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as err:
        error = err.errors()[0]
        error.pop('ctx', None)
        raise get_error(web.HTTPConflict, error)


# Функция получения данных пользователя из таблицы User
async def get_user(user_id: int, session: Session):
    user = await session.get(User, user_id)
    if user is None:
        raise get_error(web.HTTPNotFound, "user not found")
    return user


# Функция записи данных пользователя в таблицу User
async def add_user(user: User, session: Session):
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        error = get_error(web.HTTPConflict, "user already exists")
        raise error
    return user


# Функция получения данных об объявлении из таблицы Post по id пользователя
async def get_post(post_id: int, session: Session):
    post = await session.get(Post, post_id)
    if post is None:
        raise get_error(web.HTTPNotFound, "post not found")
    return post


# Функция записи данных объявления в таблицу Post привязанную к id пользователя
async def add_post(post: Post, session: Session):
    session.add(post)
    try:
        await session.commit()
    except IntegrityError:
        error = get_error(web.HTTPConflict, "post error")
        raise error
    return post


# Класс обработки запросов в бд для записи, получения, изменения и удаления пользователя
class UserView(web.View):
    @property
    def session(self):
        return self.request.session

    @property
    def user_id(self):
        return int(self.request.match_info['user_id'])

    # Получение пользователя
    async def get(self):
        user = await get_user(self.user_id, self.session)
        return web.json_response(user.json)

    # Создание пользователя
    async def post(self):
        json_data = validate(await self.request.json(), UserCreate)
        json_data["password"] = hash_password(json_data["password"])
        user = User(**json_data)
        user = await add_user(user, self.session)
        return web.json_response(user.json)

    # Изменение пользователя
    async def patch(self):
        json_data = validate(await self.request.json(), UserUpdate)
        if "password" in json_data:
            json_data["password"] = hash_password(json_data["password"])
        user = await get_user(self.user_id, self.session)
        for field, value in json_data.items():
            setattr(user, field, value)
        user = await add_user(user, self.session)
        return web.json_response(user.json)

    # Удаление пользователя
    async def delete(self):
        user = await get_user(self.user_id, self.session)
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})


# Класс обработки запросов в бд для записи, получения, изменения и удаления объявлений пользователя
class PostView(web.View):
    @property
    def session(self):
        return self.request.session

    @property
    def post_id(self):
        return int(self.request.match_info['post_id'])

    # Получение объявления
    async def get(self):
        post = await get_post(self.post_id, self.session)
        return web.json_response(post.json)

    # Создание объявления
    async def post(self):
        json_data = validate(await self.request.json(), PostCreate)
        post = Post(**json_data)
        post = await add_post(post, self.session)
        return web.json_response(post.json)

    # Изменение объявления
    async def patch(self):
        json_data = validate(await self.request.json(), PostUpdate)
        post = await get_post(self.post_id, self.session)
        for field, value in json_data.items():
            setattr(post, field, value)
        post = await add_user(post, self.session)
        return web.json_response(post.json)

    # Удаление объявления
    async def delete(self):
        post = await get_post(self.post_id, self.session)
        await self.session.delete(post)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})


# Маршрутизация запросов
app.add_routes([
    web.post('/user/', UserView),
    web.get('/user/{user_id:\d+}/', UserView),
    web.patch('/user/{user_id:\d+}/', UserView),
    web.delete('/user/{user_id:\d+}/', UserView),
    web.post('/post/', PostView),
    web.get('/post/{post_id:\d+}/', PostView),
    web.patch('/post/{post_id:\d+}/', PostView),
    web.delete('/post/{post_id:\d+}/', PostView),
])

web.run_app(app)
