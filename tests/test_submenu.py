import uuid
from src.restaurant import schemas
from tests.conftest import async_session_maker
from sqlalchemy import text


# удаляем все в начале
async def test_start_clean_submenu_table():
    async with async_session_maker() as session:
        async with session.begin():
            query1 = text("DELETE FROM submenu")
            result1 = await session.execute(query1)
            print(f"{result1.rowcount} rows deleted from submenu table")

            query2 = text("DELETE FROM menu")
            result2 = await session.execute(query2)
            print(f"{result2.rowcount} rows deleted from menu table")


# Тест на создание submenu
async def test_create_submenu(ac):
    # Создаем новое меню
    data_menu = {"title": "My menu 1", "description": "My menu description 1"}
    response_menu = await ac.post("/api/v1/menus", json=data_menu)
    assert response_menu.status_code == 201

    # Получаем ID созданного menu
    menu_id = response_menu.json()["id"]

    # Создаем новое submenu
    data_submenu = {"title": "My submenu 1", "description": "My submenu description 1"}
    response_submenu = await ac.post(f"/api/v1/menus/{menu_id}/submenus", json=data_submenu)
    assert response_submenu.status_code == 201
    submenu_id = response_submenu.json()["id"]
    submenu = schemas.Submenu(**response_submenu.json())
    assert submenu.id == uuid.UUID(str(submenu_id))  # преобразуем строку в UUID
    assert submenu.title == data_submenu["title"]
    assert submenu.description == data_submenu["description"]


# Тест на получение списка всех submenu
async def test_read_submenu(ac):
    # Получаем ID существующего menu
    response_menu = await ac.get("/api/v1/menus")
    assert response_menu.status_code == 200
    menu_id = response_menu.json()[0]["id"]

    # получение списка всех submenu
    response_submenu = await ac.get(f"/api/v1/menus/{menu_id}/submenus")
    assert response_submenu.status_code == 200
    submenus = [schemas.Submenu(**submenu) for submenu in response_submenu.json()]
    assert len(submenus) > 0
    assert isinstance(submenus[0], schemas.Submenu)


# Тест на получение списка submenu по ID
async def test_read_single_submenu(ac):
    # Получаем ID существующего menu
    response_menu = await ac.get("/api/v1/menus")
    assert response_menu.status_code == 200
    menu_id = response_menu.json()[0]["id"]

    # Получаем ID существующего submenu
    response_submenu = await ac.get(f"/api/v1/menus/{menu_id}/submenus")
    assert response_submenu.status_code == 200
    submenus = response_submenu.json()
    assert len(submenus) > 0
    submenu_id = submenus[0]["id"]

    # получение списка submenu по ID
    response_single_submenu = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}")
    assert response_single_submenu.status_code == 200
    submenu = schemas.Submenu(**response_single_submenu.json())
    assert submenu.id == uuid.UUID(str(submenu_id))  # преобразуем строку в UUID
    assert submenu.title == 'My submenu 1'
    assert submenu.description == 'My submenu description 1'


# Тест на обновление submenu
async def test_update_single_submenu(ac):
    # Получаем ID существующего menu
    response_menu = await ac.get("/api/v1/menus")
    assert response_menu.status_code == 200
    menu_id = response_menu.json()[0]["id"]

    # Получаем ID существующего submenu
    response_submenu = await ac.get(f"/api/v1/menus/{menu_id}/submenus")
    assert response_submenu.status_code == 200
    submenus = response_submenu.json()
    assert len(submenus) > 0
    submenu_id = submenus[0]["id"]

    # обновление submenu
    updated_submenu = {"title": "My updated submenu 1", "description": "My updated submenu description 1"}
    response_update_submenu = await ac.patch(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}", json=updated_submenu)
    assert response_update_submenu.status_code == 200
    updated_submenu_data = schemas.Submenu(**response_update_submenu.json())

    assert updated_submenu_data.id == uuid.UUID(str(submenu_id))  # преобразуем строку в UUID
    assert updated_submenu_data.title == updated_submenu["title"]
    assert updated_submenu_data.description == updated_submenu["description"]


# Тест на удаление submenu
async def test_delete_single_submenu(ac):
    # Получаем ID существующего menu
    response_menu = await ac.get("/api/v1/menus")
    assert response_menu.status_code == 200
    menu_id = response_menu.json()[0]["id"]

    # Получаем ID существующего submenu
    response_submenu = await ac.get(f"/api/v1/menus/{menu_id}/submenus")
    assert response_submenu.status_code == 200
    submenus = response_submenu.json()
    assert len(submenus) > 0
    submenu_id = submenus[0]["id"]

    response_delete_submenu = await ac.delete(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}")
    assert response_delete_submenu.status_code == 200
    assert response_delete_submenu.json() == {"message": "Submenu and all associated dishes deleted successfully"}

    response_deleted_submenu = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}")
    assert response_deleted_submenu.status_code == 404


# удаляем все в конце
async def test_end_clean_submenu_table():
    async with async_session_maker() as session:
        async with session.begin():
            query1 = text("DELETE FROM submenu")
            result1 = await session.execute(query1)
            print(f"{result1.rowcount} rows deleted from submenu table")

            query2 = text("DELETE FROM menu")
            result2 = await session.execute(query2)
            print(f"{result2.rowcount} rows deleted from menu table")
