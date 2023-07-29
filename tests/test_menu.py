import uuid
from src.restaurant import schemas
from tests.conftest import async_session_maker
from sqlalchemy import text

# удаляем все с начала
async def test_start_clean_menu_table():
    async with async_session_maker() as session:
        async with session.begin():
            query = text("DELETE FROM menu")
            result = await session.execute(query)
            print(f"{result.rowcount} rows deleted from menu table")


# Тест на создание menu
async def test_create_menu(ac):
    data_menu = {"title": "My menu 1", "description": "My menu description 1"}
    response_menu = await ac.post("/api/v1/menus", json=data_menu)
    assert response_menu.status_code == 201
    menu = schemas.Menu(**response_menu.json())
    assert menu.title == "My menu 1"
    assert menu.description == "My menu description 1"


# Тест на получение списка всех menu
async def test_read_menus(ac):
    response_menu = await ac.get("/api/v1/menus")
    assert response_menu.status_code == 200
    menus = [schemas.Menu(**menu) for menu in response_menu.json()]
    assert len(menus) > 0


# Тест на получение одного menu по ID
async def test_read_menu(ac):
    data_menu = {"title": "My menu 1", "description": "My menu description 1"}
    response_menu = await ac.post("/api/v1/menus", json=data_menu)
    assert response_menu.status_code == 201
    # Получаем ID созданного menu
    menu_id = response_menu.json()["id"]
    # Получаем данные созданного menu
    response = await ac.get(f"/api/v1/menus/{menu_id}")
    assert response.status_code == 200
    menu = schemas.Menu(**response.json())
    assert menu.id == uuid.UUID(str(menu_id))  # преобразуем строку в UUID
    assert menu.title == "My menu 1"
    assert menu.description == "My menu description 1"


# Тест на обновление menu
async def test_update_menu(ac):
    # Создаем новое меню
    data_menu = {"title": "My menu 1", "description": "My menu description 1"}
    response_menu = await ac.post("/api/v1/menus", json=data_menu)
    assert response_menu.status_code == 201
    # Получаем ID созданного menu
    menu_id = response_menu.json()["id"]
    # Обновляем menu
    data_update = {"title": "My updated menu 1", "description": "My updated menu description 1"}
    response = await ac.patch(f"/api/v1/menus/{menu_id}", json=data_update)
    assert response.status_code == 200
    menu = schemas.Menu(**response.json())
    assert menu.id == uuid.UUID(str(menu_id))  # преобразуем строку в UUID
    assert menu.title == "My updated menu 1"
    assert menu.description == "My updated menu description 1"


# Тест на удаление menu
async def test_delete_menu(ac):
    # Создаем новое меню
    data = {"title": "My menu 1", "description": "My menu description 1"}
    response_menu = await ac.post("/api/v1/menus", json=data)
    assert response_menu.status_code == 201
    # Получаем ID созданного menu
    menu_id = response_menu.json()["id"]
    # Удаляем menu
    response_menu = await ac.delete(f"/api/v1/menus/{menu_id}")
    assert response_menu.status_code == 200
    # Получаем данные удаленного menu
    response_menu = await ac.get(f"/api/v1/menus/{menu_id}")
    assert response_menu.status_code == 404
    assert response_menu.json()["detail"] == "menu not found"


# удаляем все в конце
async def test_end_clean_menu_table():
    async with async_session_maker() as session:
        async with session.begin():
            query = text("DELETE FROM menu")
            result = await session.execute(query)
            print(f"{result.rowcount} rows deleted from menu table")
