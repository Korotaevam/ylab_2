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

    # Создание dish
    new_dish = {"title": "New dish", "description": "New dish description", "price": '10.99'}
    response_dish = await ac.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json=new_dish)
    assert response_dish.status_code == 201

    dish = schemas.Dish(**response_dish.json())

    assert dish.title == new_dish["title"]
    assert dish.description == new_dish["description"]
    assert dish.price == "10.99"


# Тест на получение списка всех dish
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

    # получение списка submenu по dish
    response_dish = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes")
    assert response_dish.status_code == 200
    dishes = [schemas.Dish(**dish) for dish in response_dish.json()]
    assert len(dishes) > 0
    assert isinstance(dishes[0], schemas.Dish)


# Тест на получение списка dish по ID
async def test_read_single_dish(ac):
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

    # Получаем ID существующего dish
    response_dish = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes")
    assert response_submenu.status_code == 200
    dishes = response_dish.json()
    assert len(dishes) > 0
    dish_id = dishes[0]["id"]

    # получение списка dish по ID
    response_single_dish = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")

    assert response_single_dish.status_code == 200
    dish = schemas.Dish(**response_single_dish.json())
    assert dish.id == uuid.UUID(str(dish_id))  # преобразуем строку в UUID
    assert dish.title == 'New dish'
    assert dish.description == 'New dish description'


# Тест на обновление dish
async def test_update_dish(ac):
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

    # Получаем ID существующего dish
    response_dish = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes")
    assert response_submenu.status_code == 200
    dishes = response_dish.json()
    assert len(dishes) > 0
    dish_id = dishes[0]["id"]

    # Обновление блюда
    update_dish = {"title": "My updated dish 1", "description": "My updated dish description 1", "price": "12.99"}
    response_update_dish = await ac.patch(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                                          json=update_dish)
    assert response_update_dish.status_code == 200
    updated_dish_data = schemas.Dish(**response_update_dish.json())

    # Проверка обновленных данных
    assert updated_dish_data.title == update_dish["title"]
    assert updated_dish_data.price == update_dish["price"]
    assert updated_dish_data.description == update_dish["description"]


# Тест на удаление dish
async def test_delete_single_dish(ac):
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

    # Получаем ID существующего dish
    response_dish = await ac.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes")
    assert response_submenu.status_code == 200
    dishes = response_dish.json()
    assert len(dishes) > 0
    dish_id = dishes[0]["id"]

    response_delete_dish = await ac.delete(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
    assert response_delete_dish.status_code == 200
    assert response_delete_dish.json() == {"message": 'Dish deleted successfully'}

    response_delete_dish = await ac.delete(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
    assert response_delete_dish.status_code == 404


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
