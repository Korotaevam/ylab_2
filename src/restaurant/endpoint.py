from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select, and_
from starlette import status
from src.database import get_async_session
from src.restaurant import models, schemas
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

# redis
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache import FastAPICache
# from redis import asyncio as aioredis
# from fastapi_cache.decorator import cache
# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
#
# cache
# @cache(expire=30)

router = APIRouter()


# Определяем CRUD операции для модели Menu

@router.get("/api/v1/menus", response_model=list[schemas.Menu])
async def read_menus(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session)):
    menus = await session.execute(select(models.Menu).offset(skip).limit(limit))
    return menus.scalars().all()


@router.post("/api/v1/menus", response_model=schemas.Menu, status_code=status.HTTP_201_CREATED)
async def create_menu(menu: schemas.MenuCreate, session: AsyncSession = Depends(get_async_session)):
    db_menu = models.Menu(title=menu.title, description=menu.description)
    session.add(db_menu)
    await session.commit()
    await session.refresh(db_menu)
    return db_menu


@router.get("/api/v1/menus/{menu_id}", response_model=schemas.Menu)
async def read_menu(menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    db_menu = await session.get(models.Menu, menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    submenus_count = await session.scalar(
        select(func.count(models.Submenu.id)).join(models.Menu).where(models.Menu.id == menu_id))
    dishes_count = await session.scalar(
        select(func.count(models.Dish.id)).join(models.Submenu).join(models.Menu).where(models.Menu.id == menu_id))
    return {"id": db_menu.id, "title": db_menu.title, "description": db_menu.description,
            "submenus_count": submenus_count, "dishes_count": dishes_count}


@router.patch("/api/v1/menus/{menu_id}", response_model=schemas.Menu)
async def update_menu(menu_id: UUID, menu: schemas.MenuUpdate, session: AsyncSession = Depends(get_async_session)):
    db_menu = await session.get(models.Menu, menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    for field, value in menu.dict(exclude_unset=True).items():
        setattr(db_menu, field, value)
    await session.commit()
    await session.refresh(db_menu)
    return db_menu


@router.delete("/api/v1/menus/{menu_id}")
async def delete_menu(menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    db_menu = await session.get(models.Menu, menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    await session.delete(db_menu)
    await session.commit()
    return {"message": "Menu deleted successfully"}


# Определяем CRUD операции для модели Submenu

@router.get("/api/v1/menus/{menu_id}/submenus", response_model=list[schemas.Menu])
async def get_submenus(menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    db_submenus = await session.execute(select(models.Submenu).filter(models.Submenu.menu_id == menu_id))
    return db_submenus.scalars().all()


@router.post("/api/v1/menus/{menu_id}/submenus", status_code=status.HTTP_201_CREATED)
async def create_submenu(menu_id: UUID, submenu: schemas.SubmenuBase,
                         session: AsyncSession = Depends(get_async_session)):
    db_submenu = models.Submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    session.add(db_submenu)
    await session.commit()
    await session.refresh(db_submenu)
    return db_submenu


@router.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.Submenu)
async def read_submenu(menu_id: UUID, submenu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    db_submenu = await session.get(models.Submenu, submenu_id)
    if db_submenu is None or db_submenu.menu_id != menu_id:
        raise HTTPException(status_code=404, detail="submenu not found")
    dishes_count = await session.scalar(
        select(func.count(models.Dish.id)).join(models.Submenu).where(models.Submenu.id == submenu_id))
    return {"id": db_submenu.id, "title": db_submenu.title, "description": db_submenu.description,
            "menu_id": db_submenu.menu_id, "dishes_count": dishes_count}


@router.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.Submenu)
async def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: schemas.SubmenuUpdate,
                         session: AsyncSession = Depends(get_async_session)):
    db_submenu = await session.get(models.Submenu, submenu_id)
    if db_submenu is None or db_submenu.menu_id != menu_id:
        raise HTTPException(status_code=404, detail="submenu not found")
    for field, value in submenu.dict(exclude_unset=True).items():
        setattr(db_submenu, field, value)
    await session.commit()
    await session.refresh(db_submenu)
    return db_submenu


@router.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
async def delete_submenu(menu_id: UUID, submenu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    db_submenu = await session.get(models.Submenu, submenu_id)
    if db_submenu is None or db_submenu.menu_id != menu_id:
        raise HTTPException(status_code=404, detail="submenu not found")
    await session.delete(db_submenu)
    await session.commit()

    return {"message": "Submenu and all associated dishes deleted successfully"}


# # Определяем CRUD операции для модели Dish

@router.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=list[schemas.Dish])
async def read_dishes(menu_id: UUID, submenu_id: UUID, skip: int = 0, limit: int = 100,
                      session: AsyncSession = Depends(get_async_session)):
    db_dishes = await session.execute(select(models.Dish).join(models.Submenu).where(and_(
        models.Dish.submenu_id == submenu_id, models.Submenu.menu_id == menu_id)).offset(skip).limit(limit))
    return db_dishes.scalars().all()


@router.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=schemas.Dish,
             status_code=status.HTTP_201_CREATED)
async def create_dish(submenu_id: UUID, dish: schemas.DishCreate,
                      session: AsyncSession = Depends(get_async_session)):
    db_dish = models.Dish(title=dish.title, description=dish.description, price=str(dish.price), submenu_id=submenu_id)
    session.add(db_dish)
    await session.commit()
    await session.refresh(db_dish)
    return {"id": db_dish.id, "title": db_dish.title, "description": db_dish.description,
            "price": str(float(round(float(db_dish.price), 2))), 'submenu_id': db_dish.submenu_id}


@router.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
async def read_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, session: AsyncSession = Depends(get_async_session)):
    db_dish = await session.execute(select(models.Dish).join(models.Submenu).join(models.Menu).where(and_(
        models.Dish.id == dish_id, models.Submenu.id == submenu_id, models.Menu.id == menu_id)))

    db_dish_row = db_dish.fetchone()
    if db_dish_row is None:
        raise HTTPException(status_code=404, detail="dish not found")
    else:
        db_dish = db_dish_row[0]

    return {"id": db_dish.id, "title": db_dish.title, "description": db_dish.description,
            "price": str(float(round(float(db_dish.price), 2))), 'submenu_id': db_dish.submenu_id}


@router.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: schemas.DishUpdate,
                      session: AsyncSession = Depends(get_async_session)):
    db_dish = await session.execute(select(models.Dish).join(models.Submenu).join(models.Menu).where(and_(
        models.Dish.id == dish_id, models.Submenu.id == submenu_id, models.Menu.id == menu_id)))
    db_dish = db_dish.fetchone()[0]
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    for field, value in dish.dict(exclude_unset=True).items():
        setattr(db_dish, field, value)
    await session.commit()
    await session.refresh(db_dish)
    return {"id": db_dish.id, "title": db_dish.title, "description": db_dish.description,
            "price": str(float(db_dish.price)), 'submenu_id': db_dish.submenu_id}


@router.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID,
                      session: AsyncSession = Depends(get_async_session)):
    db_dish = await session.execute(select(models.Dish).join(models.Submenu).join(models.Menu).where(and_(
        models.Dish.id == dish_id, models.Submenu.id == submenu_id, models.Menu.id == menu_id)))
    db_dish_row = db_dish.fetchone()
    if db_dish_row is None:
        raise HTTPException(status_code=404, detail="dish not found")
    else:
        db_dish = db_dish_row[0]

    await session.delete(db_dish)
    await session.commit()
    return {"message": "Dish deleted successfully"}
