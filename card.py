import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8548721313:AAF-AzsSNVieZbb_9kB_vBsnv3m9Op255Gw"
MANAGER_ID = 399920862  # Укажи свой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# История заявок в оперативной памяти
REQUEST_HISTORY = []


# ---------- Главное меню ----------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Типы карт", callback_data="types")],
        [InlineKeyboardButton(text="🌍 Для чего они нужны?", callback_data="purposes")],
        [InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq")],
        [InlineKeyboardButton(text="👨‍💼 Написать менеджеру", callback_data="manager")],
        [InlineKeyboardButton(text="🎯 Подбор карты", callback_data="choose_start")],
    ])


def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])


# ---------- START ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Здравствуйте! Выберите раздел ниже:",
        reply_markup=main_menu()
    )


# =====================================================
# 1. Типы карт
# =====================================================
@dp.callback_query(lambda c: c.data == "types")
async def types_info(call: types.CallbackQuery):

    text = (
        "📌 <b>Типы карт</b>\n\n"
        "🔹 Виртуальные — удобны для подписок и онлайн оплаты.\n"
        "🔹 Пластиковые — подходят для офлайн магазинов и банкоматов.\n"
        "🔹 Мультивалютные — удобно для сервисов США/ЕС.\n"
    )

    await call.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")


# =====================================================
# 2. Для чего нужны
# =====================================================
@dp.callback_query(lambda c: c.data == "purposes")
async def purposes_info(call: types.CallbackQuery):

    text = (
        "🌍 <b>Для чего нужны зарубежные карты?</b>\n\n"
        "✔ Оплата зарубежных сервисов\n"
        "✔ Подписки (Google, Apple, Netflix, Steam)\n"
        "✔ Онлайн-магазины (Amazon и др.)\n"
        "✔ Реклама (Meta Ads, Google Ads)\n"
        "✔ Путешествия и поездки\n"
        "✔ Экономия на комиссиях\n"
    )

    await call.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")


# =====================================================
# 3. FAQ
# =====================================================
@dp.callback_query(lambda c: c.data == "faq")
async def faq_info(call: types.CallbackQuery):

    text = (
        "❓ <b>Частые вопросы:</b>\n\n"
        "🔸 Можно ли пополнять карту? — Да, зависит от типа.\n"
        "🔸 Работает ли в РФ? — В онлайне да.\n"
        "🔸 Нужен ли паспорт? — Для некоторых — да.\n"
        "🔸 Подходит ли для подписок? — Да.\n"
    )

    await call.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")


# =====================================================
# 4. Связь с менеджером
# =====================================================
@dp.callback_query(lambda c: c.data == "manager")
async def contact_manager(call: types.CallbackQuery):

    await bot.send_message(
        MANAGER_ID,
        f"📩 Новый запрос от @{call.from_user.username} (ID: {call.from_user.id})"
    )

    text = (
        "👨‍💼 Ваш запрос отправлен менеджеру.\n"
        "Он свяжется с вами в ближайшее время."
    )

    await call.message.edit_text(text, reply_markup=back_button())


# =====================================================
# 5. Подбор карты (FSM)
# =====================================================

class Choose(StatesGroup):
    purpose = State()
    cardtype = State()
    anon = State()


@dp.callback_query(lambda c: c.data == "choose_start")
async def choose_start(call: types.CallbackQuery, state: FSMContext):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписки", callback_data="p_subs")],
        [InlineKeyboardButton(text="Покупки", callback_data="p_shop")],
        [InlineKeyboardButton(text="Путешествия", callback_data="p_travel")],
        [InlineKeyboardButton(text="Другое", callback_data="p_other")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")],
    ])

    await call.message.edit_text("Для чего вам нужна карта?", reply_markup=kb)
    await state.set_state(Choose.purpose)


# --- Вопрос 1 ---
@dp.callback_query(Choose.purpose)
async def choose_purpose(call: types.CallbackQuery, state: FSMContext):

    await state.update_data(purpose=call.data)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Виртуальная", callback_data="t_virtual")],
        [InlineKeyboardButton(text="Пластиковая", callback_data="t_plastic")],
        [InlineKeyboardButton(text="Не важно", callback_data="t_any")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")],
    ])

    await call.message.edit_text("Какой тип карты предпочитаете?", reply_markup=kb)
    await state.set_state(Choose.cardtype)


# --- Вопрос 2 ---
@dp.callback_query(Choose.cardtype)
async def choose_type(call: types.CallbackQuery, state: FSMContext):

    await state.update_data(cardtype=call.data)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Максимальная", callback_data="a_max")],
        [InlineKeyboardButton(text="Средняя", callback_data="a_med")],
        [InlineKeyboardButton(text="Не важно", callback_data="a_any")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")],
    ])

    await call.message.edit_text("Насколько важна анонимность?", reply_markup=kb)
    await state.set_state(Choose.anon)


# --- Вопрос 3 (финал) ---
@dp.callback_query(Choose.anon)
async def choose_finish(call: types.CallbackQuery, state: FSMContext):

    await state.update_data(anon=call.data)
    data = await state.get_data()

    # Мини-логика подбора
    if data["purpose"] == "p_subs":
        card = "⭐ Вам подойдёт Виртуальная USD-карта."
    elif data["purpose"] == "p_travel":
        card = "⭐ Пластиковая мультивалютная карта — лучший выбор."
    else:
        card = "⭐ Универсальная виртуальная карта — оптимальный вариант."

    text_result = (
        "<b>🎯 Результат подбора:</b>\n\n"
        f"{card}\n\n"
        "<i>Менеджер уже получил вашу заявку.</i>"
    )

    # Формируем заявку
    req = (
        "📩 Новая заявка!\n\n"
        f"Пользователь: @{call.from_user.username}\n"
        f"Цель: {data['purpose']}\n"
        f"Тип карты: {data['cardtype']}\n"
        f"Анонимность: {data['anon']}\n"
    )

    # Отправка менеджеру
    await bot.send_message(MANAGER_ID, req)

    # Сохраняем в историю
    REQUEST_HISTORY.append(req)

    await call.message.edit_text(text_result, reply_markup=back_button(), parse_mode="HTML")
    await state.clear()


# =====================================================
# Кнопка НАЗАД
# =====================================================
@dp.callback_query(lambda c: c.data == "back")
async def go_back(call: types.CallbackQuery):

    await call.message.edit_text("Главное меню:", reply_markup=main_menu())


# =====================================================
# История заявок (только админ)
# =====================================================
@dp.message(Command("history"))
async def history(message: types.Message):

    if message.from_user.id != MANAGER_ID:
        return await message.answer("❌ Нет доступа.")

    if not REQUEST_HISTORY:
        return await message.answer("История пуста.")

    text = "📜 <b>История заявок:</b>\n\n" + "\n\n".join(REQUEST_HISTORY[-20:])
    await message.answer(text, parse_mode="HTML")


# =====================================================
# Запуск
# =====================================================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
