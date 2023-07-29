import uuid
from src.restaurant import schemas
from tests.conftest import async_session_maker
from sqlalchemy import text


# удаляем все в начале
async def test_start_clean_dish_table():
    async with async_session_maker() as session:
        async with session.begin():
            query1 = text("DELETE FROM dish")
            result1 = await session.execute(query1)
            print(f"{result1.rowcount} rows deleted from dish table")

            query2 = text("DELETE FROM submenu")
            result2 = await session.execute(query2)
            print(f"{result2.rowcount} rows deleted from submenu table")

            query3 = text("DELETE FROM menu")
            result3 = await session.execute(query3)
            print(f"{result3.rowcount} rows deleted from menu table")


# Создание dish
async def test_create_dish(ac):
    # Создаем новое меню
    data_menu = {"title": "My menu 1", "description": "My menu description 1"}
    response_menu = await ac.post("/api/v1/menus", json=data_menu)
    assert response_menu.status_code == 201

    menu_id = response_menu.json()["id"]

    menu = schemas.Menu(**response_menu.json())
    assert menu.id == uuid.UUID(str(menu_id))  # преобразуем строку в UUID
    assert menu.title == "My menu 1"
    assert menu.description == "My menu description 1"

    # Создаем новое submenu
    data_submenu = {"title": "My submenu 1", "description": "My submenu description 1"}
    response_submenu = await ac.post(f"/api/v1/menus/{menu_id}/submenus", json=data_submenu)
    assert response_submenu.status_code == 201

    submenu_id = response_submenu.json()["id"]

    submenu = schemas.Submenu(**response_submenu.json())
    assert submenu.id == uuid.UUID(str(submenu_id))  # преобразуем строку в UUID
    assert submenu.title == data_submenu["title"]
    assert submenu.description == data_submenu["description"]

    # Создание dish 1
    new_dish = {"title": "New dish 1", "description": "New dish description 1", "price": '10.99'}
    response_dish = await ac.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json=new_dish)
    assert response_dish.status_code == 201

    dish = schemas.Dish(**response_dish.json())

    assert dish.title == new_dish["title"]
    assert dish.description == new_dish["description"]
    assert dish.price == "10.99"

    # Создание dish 2
    new_dish = {"title": "New dish 2", "description": "New dish description 2", "price": '15.99'}
    response_dish = await ac.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json=new_dish)
    assert response_dish.status_code == 201

    dish = schemas.Dish(**response_dish.json())

    assert dish.title == new_dish["title"]
    assert dish.description == new_dish["description"]
    assert dish.price == "15.99"

    # проверяем количество dish и submenu в menu
    response_dish_submenu_counts = await ac.get(f'/api/v1/menus/{menu_id}')
    assert response_dish_submenu_counts.status_code == 200
    dish_counts_menu = schemas.Menu(**response_dish_submenu_counts.json())

    assert dish_counts_menu.submenus_count == 1
    assert dish_counts_menu.dishes_count == 2

    # проверяем количество dish в submenu
    response_dish_counts = await ac.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    assert response_dish_counts.status_code == 200
    dish_counts_submenu = schemas.Submenu(**response_dish_counts.json())

    assert dish_counts_submenu.dishes_count == 2


# удаляем все в конце
async def test_end_clean_dish_table():
    async with async_session_maker() as session:
        async with session.begin():
            query1 = text("DELETE FROM dish")
            result1 = await session.execute(query1)
            print(f"{result1.rowcount} rows deleted from dish table")

            query2 = text("DELETE FROM submenu")
            result2 = await session.execute(query2)
            print(f"{result2.rowcount} rows deleted from submenu table")

            query3 = text("DELETE FROM menu")
            result3 = await session.execute(query3)
            print(f"{result3.rowcount} rows deleted from menu table")
