import aiohttp
import asyncio


async def main():
    session = aiohttp.ClientSession()

    # -----Запросы для записи, получения, изменения и удаления пользователя в бд-----

    # -----Запись нового пользователя и его пароля----------
    response = await session.post(
        "http://127.0.0.1:8080/user/",
        json={'name': 'user_1', 'password': '12345'},)
    print(response.status)
    print(await response.json())

    # -----Получение данных о пользователе по его id----------
    response = await session.get(
        "http://127.0.0.1:8080/user/1/", )
    print(response.status)
    print(await response.json())

    # -----Изменение данных о пользователе по его id----------
    # response = await session.patch(
    #     "http://127.0.0.1:8080/user/1/",
    #     json={
    #         'name': 'new_name',
    #         'password': '1234567'})
    # print(response.status)
    # print(await response.json())

    # -----Удаление пользователя по его id---------------------
    # response = await session.delete(
    #     "http://127.0.0.1:8080/user/1/",)
    # print(response.status)
    # print(await response.json())

    #---------------------------------------------------------------------------
    # -----Запросы для записи, получения, изменения и удаления объявлений в бд-----

    # -----Запись нового объявления, привязанного к пользователю по его id----------
    response = await session.post(
        "http://127.0.0.1:8080/post/",
        json={'heading': 'Post_1',
        'description': 'text_text_text_1',
        'user_id': 1})
    print(response.status)
    print(await response.json())

    # -----Получение данных об объявлении, по его id-------------------------------
    response = await session.get(
        "http://127.0.0.1:8080/post/1/", )
    print(response.status)
    print(await response.json())

    # -----Изменение значений заголовка, текста, пользователя объявления по его id----------
    # response = await session.patch(
    #     "http://127.0.0.1:8080/post/1/",
    #     json={'heading': 'Post_22222',
    #           'description': 'text_text_text_22222',
    #           'user_id': 1})
    # print(response.status)
    # print(await response.json())

    # -----Удаление объявления по его id----------
    # response = await session.delete(
    #     "http://127.0.0.1:8080/post/1/",)
    # print(response.status)
    # print(await response.json())

    await session.close()


asyncio.run(main())
