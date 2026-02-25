from aiogram import Router
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)
from bot.config import settings

router = Router()


def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")],
            [KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="👤 Личный кабинет")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_main_menu_webapp():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🛍️ Открыть магазин",
                web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )],
            [InlineKeyboardButton(text="⭐ Избранное", callback_data="favorites")],
            [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
            [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        ]
    )
    return keyboard


def get_profile_menu(user_role: str = "user"):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="📜 История покупок", callback_data="order_history")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="💎 Рекомендации", callback_data="recommendations")])

    if user_role == "user":
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🏪 Стать продавцом", callback_data="become_seller")])
    elif user_role == "seller":
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="📦 Мои товары", callback_data="my_products")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="📊 Статистика продаж", callback_data="sales_stats")])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

    return keyboard


def get_admin_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Продавцы", callback_data="admin_sellers")],
            [InlineKeyboardButton(text="📦 Все товары", callback_data="admin_products")],
            [InlineKeyboardButton(text="🛒 Все заказы", callback_data="admin_orders")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")],
        ]
    )
    return keyboard


def get_seller_approval_keyboard(seller_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_seller_{seller_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_seller_{seller_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_sellers")],
        ]
    )
    return keyboard


def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]
    )
    return keyboard