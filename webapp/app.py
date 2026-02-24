from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session, Product, Seller, User, Favorite, CartItem
from sqlalchemy import select
from bot.config import settings
import os

app = FastAPI(title="Marketplace WebApp")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def webapp_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/catalog")
async def get_catalog(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product, Seller)
        .join(Seller, Product.seller_id == Seller.id)
        .where(Product.is_available == True)
        .order_by(Product.created_at.desc())
    )

    products = []
    for product, seller in result.all():
        products.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "seller_name": seller.company_name
        })

    return {"products": products}


@app.get("/favorites/{telegram_id}")
async def get_favorites(telegram_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product, Seller)
        .join(Favorite, Favorite.product_id == Product.id)
        .join(Seller, Product.seller_id == Seller.id)
        .where(Favorite.user_id == telegram_id)
    )

    favorites = []
    for product, seller in result.all():
        favorites.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "seller_name": seller.company_name
        })

    return {"favorites": favorites}


@app.get("/cart/{telegram_id}")
async def get_cart(telegram_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product, CartItem)
        .join(CartItem, CartItem.product_id == Product.id)
        .where(CartItem.user_id == telegram_id)
    )

    cart = []
    total = 0
    for product, cart_item in result.all():
        item_total = product.price * cart_item.quantity
        total += item_total
        cart.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": cart_item.quantity,
            "total": item_total
        })

    return {"cart": cart, "total": total}


@app.post("/favorites/add")
async def add_favorite(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    existing = await session.execute(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    if existing.scalar_one_or_none():
        return {"status": "already_exists"}

    favorite = Favorite(user_id=user_id, product_id=product_id)
    session.add(favorite)
    await session.commit()

    return {"status": "success"}


@app.post("/favorites/remove")
async def remove_favorite(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    result = await session.execute(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    favorite = result.scalar_one_or_none()

    if favorite:
        await session.delete(favorite)
        await session.commit()

    return {"status": "success"}


@app.post("/cart/add")
async def add_to_cart(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    cart_item = result.scalar_one_or_none()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(cart_item)

    await session.commit()
    return {"status": "success"}


@app.post("/cart/remove")
async def remove_from_cart(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    cart_item = result.scalar_one_or_none()

    if cart_item:
        await session.delete(cart_item)
        await session.commit()

    return {"status": "success"}


@app.post("/cart/clear")
async def clear_cart(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    user_id = data.get("user_id")

    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    cart_items = result.scalars().all()

    for item in cart_items:
        await session.delete(item)

    await session.commit()
    return {"status": "success"}