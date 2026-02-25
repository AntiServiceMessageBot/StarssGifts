from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import User, Seller, UserRole, SellerStatus, get_session
from bot.config import settings
from bot.keyboards import get_main_menu, get_main_menu_webapp, get_profile_menu, get_admin_menu, get_seller_approval_keyboard, get_back_keyboard

router = Router()


class BecomeSellerState(StatesGroup):
    company_name = State()
    iin = State()
    description = State()


@router.message(F.text == "/start")
async def cmd_start(message: Message, session: AsyncSession):
    user_id = message.from_user.id

    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        session.add(user)
        await session.commit()

    welcome_text = f"Привет, {message.from_user.first_name}! 👋\n\nДобро пожаловать в маркетплейс!\n\nВыберите действие:"

    if user.role == UserRole.ADMIN:
        await message.answer(welcome_text, reply_markup=get_admin_menu())
    else:
        await message.answer(welcome_text, reply_markup=get_main_menu_webapp())


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, session: AsyncSession):
    result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    user = result.scalar_one_or_none()

    if user and user.role == UserRole.ADMIN:
        await callback.message.edit_text("Главное меню администратора:", reply_markup=get_admin_menu())
    else:
        await callback.message.edit_text("Главное меню:", reply_markup=get_main_menu_webapp())
    await callback.answer()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, session: AsyncSession):
    result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    user = result.scalar_one_or_none()

    if not user:
        await callback.answer("Пользователь не найден")
        return

    username = user.username or "Не указан"
    role_text = {
        UserRole.USER: "Покупатель",
        UserRole.SELLER: "Продавец",
        UserRole.ADMIN: "Администратор"
    }.get(user.role, "Покупатель")

    profile_text = f"👤 Ваш профиль\n\nИмя: {user.first_name or 'Не указано'}\n"
    profile_text += f"Username: @{username}\n"
    profile_text += f"Роль: {role_text}\n"
    profile_text += f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}"

    await callback.message.edit_text(profile_text, reply_markup=get_profile_menu(user.role.value))
    await callback.answer()


@router.callback_query(F.data == "become_seller")
async def become_seller(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    user = result.scalar_one_or_none()

    if not user:
        await callback.answer("Сначала запустите бота командой /start")
        return

    if user.role != UserRole.USER:
        await callback.answer("Вы уже являетесь продавцом или администратором")
        return

    result = await session.execute(select(Seller).where(Seller.user_id == user.id))
    existing_seller = result.scalar_one_or_none()

    if existing_seller and existing_seller.status == SellerStatus.PENDING:
        await callback.message.edit_text("Ваша заявка на рассмотрении. Ожидайте подтверждения.", reply_markup=get_back_keyboard())
        await callback.answer()
        return

    await state.set_state(BecomeSellerState.company_name)
    await callback.message.edit_text("📝 Регистрация продавца\n\nВведите название вашей компании:", reply_markup=get_back_keyboard())
    await callback.answer()


@router.message(BecomeSellerState.company_name)
async def process_company_name(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await state.set_state(BecomeSellerState.iin)
    await message.answer("Введите ИИН компании (или пропустите):")


@router.message(BecomeSellerState.iin)
async def process_iin(message: Message, state: FSMContext):
    await state.update_data(iin=message.text if message.text else None)
    await state.set_state(BecomeSellerState.description)
    await message.answer("Опишите вашу деятельность:")


@router.message(BecomeSellerState.description)
async def process_description(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = result.scalar_one_or_none()

    if user:
        seller = Seller(
            user_id=user.id,
            company_name=data['company_name'],
            iin=data.get('iin'),
            description=message.text,
            status=SellerStatus.PENDING
        )
        session.add(seller)
        await session.commit()

    await state.clear()
    await message.answer("✅ Заявка отправлена на модерацию! Ожидайте подтверждения от администратора.", reply_markup=get_main_menu_webapp())


@router.callback_query(F.data.startswith("admin_sellers"))
async def admin_sellers(callback: CallbackQuery, session: AsyncSession):
    result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    user = result.scalar_one_or_none()

    if not user or user.role != UserRole.ADMIN:
        await callback.answer("У вас нет прав администратора")
        return

    result = await session.execute(select(Seller).where(Seller.status == SellerStatus.PENDING))
    pending_sellers = result.scalars().all()

    if not pending_sellers:
        await callback.message.edit_text("Нет заявок на регистрацию продавцов.", reply_markup=get_admin_menu())
        await callback.answer()
        return

    text = "📋 Заявки на регистрацию продавцов:\n\n"

    for seller in pending_sellers:
        text += f"🏢 {seller.company_name}\n"
        text += f"ИИН: {seller.iin or 'Не указан'}\n"
        text += f"Описание: {seller.description}\n\n"

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("approve_seller_"))
async def approve_seller(callback: CallbackQuery, session: AsyncSession):
    seller_id = int(callback.data.split("_")[-1])

    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()

    if seller:
        seller.status = SellerStatus.APPROVED
        result = await session.execute(select(User).where(User.id == seller.user_id))
        user = result.scalar_one_or_none()
        if user:
            user.role = UserRole.SELLER
        await session.commit()

    await callback.message.edit_text(f"✅ Продавец {seller.company_name} одобрен!", reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("reject_seller_"))
async def reject_seller(callback: CallbackQuery, session: AsyncSession):
    seller_id = int(callback.data.split("_")[-1])

    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()

    if seller:
        seller.status = SellerStatus.REJECTED
        await session.commit()

    await callback.message.edit_text(f"❌ Заявка продавца {seller.company_name} отклонена.", reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "favorites")
async def show_favorites(callback: CallbackQuery):
    await callback.message.edit_text("⭐ Избранное\n\nФункционал в разработке...", reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    await callback.message.edit_text("🛒 Корзина\n\nФункционал в разработке...", reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "order_history")
async def show_order_history(callback: CallbackQuery):
    await callback.message.edit_text("📜 История покупок\n\nФункционал в разработке...", reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "recommendations")
async def show_recommendations(callback: CallbackQuery):
    await callback.message.edit_text("💎 Рекомендации товаров\n\nФункционал в разработке...", reply_markup=get_back_keyboard())
    await callback.answer()