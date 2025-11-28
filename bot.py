# bot.py
import os
import asyncio
from typing import Dict, Any

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Получаем конфиг из env
TOKEN = os.getenv("TOKEN")
MANAGER_ID = os.getenv("MANAGER_ID")  # строка, затем конвертим

if not TOKEN:
    raise RuntimeError("TOKEN env var is required (get it from @BotFather)")

try:
    MANAGER_ID = int(MANAGER_ID) if MANAGER_ID else None
except Exception:
    MANAGER_ID = None

# Оперативная история (в памяти)
REQUEST_HISTORY: list[str] = []

# ------------ Клавиатуры ------------
def main_menu() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton("📌 Типы карт", callback_data="types")],
        [InlineKeyboardButton("🌍 Для чего они нужны?", callback_data="purposes")],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")],
        [InlineKeyboardButton("👨‍💼 Перевести на менеджера", callback_data="manager")],
        [InlineKeyboardButton("🎯 Подбор карты", callback_data="choose_start")],
    ]
    return InlineKeyboardMarkup(kb)


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="back")]])


# ------------ Хэндлеры ------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "Здравствуйте! Выберите раздел ниже:",
        reply_markup=main_menu()
    )


async def types_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text = (
        "📌 *Типы карт*\n\n"
        "🔹 *Виртуальные* — быстро и удобно для онлайн-покупок и подписок.\n"
        "🔹 *Пластиковые* — подходят для офлайн-оплат и банкоматов.\n"
        "🔹 *Мультивалютные* — удобны если нужна поддержка USD/EUR и т.п.\n\n"
        "_(Тексты можно редактировать под конкретные продукты)_"
    )
    await update.callback_query.edit_message_text(text, reply_markup=back_kb(), parse_mode="Markdown")


async def purposes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text = (
        "🌍 *Для чего нужны зарубежные карты?*\n\n"
        "✔ Оплата зарубежных сервисов (Netflix, Steam, магазины)\n"
        "✔ Подписки (Google, Apple, Spotify и др.)\n"
        "✔ Интернет-покупки (Amazon, eBay)\n"
        "✔ Рекламные кабинеты (Google Ads, Meta Ads)\n"
        "✔ Удобство при поездках и владение валютой\n\n"
        "_(Уточни условия для каждой конкретной карты)_"
    )
    await update.callback_query.edit_message_text(text, reply_markup=back_kb(), parse_mode="Markdown")


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text = (
        "❓ *Частые вопросы*\n\n"
        "🔸 *Можно ли пополнять карту?* — Зависит от продукта.\n"
        "🔸 *Работает ли в РФ?* — В онлайне чаще всего да.\n"
        "🔸 *Нужен ли паспорт?* — Иногда, в зависимости от KYC.\n"
        "🔸 *Подходит ли для подписок?* — Да, виртуальные карты часто удобны.\n\n"
        "_(Добавь конкретные ответы по своим картам)_"
    )
    await update.callback_query.edit_message_text(text, reply_markup=back_kb(), parse_mode="Markdown")


async def manager_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user = update.effective_user
    # уведомление менеджеру
    summary = f"📩 Запрос от @{user.username if user.username else user.full_name} (ID: {user.id})"
    if MANAGER_ID:
        try:
            await context.bot.send_message(MANAGER_ID, summary)
        except Exception as e:
            # не критично — продолжаем, но логируем в чат пользователя
            await update.callback_query.message.reply_text(
                f"Ошибка уведомления менеджера: {e}\nПроверь MANAGER_ID."
            )
    else:
        # если менеджер не задан — сообщаем об этом
        await update.callback_query.message.reply_text(
            "⚠️ MANAGER_ID не задан. Уведомление менеджера не отправлено."
        )
    await update.callback_query.edit_message_text(
        "👨‍💼 Ваш запрос отправлен менеджеру. Он свяжется с вами.", reply_markup=back_kb()
    )


# ---------------- Подбор карты: мини-опрос через callback_data ---------------
# структура в context.user_data:
# context.user_data["choose"] = {"purpose": "...", "cardtype": "...", "anon": "..."}

async def choose_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Подписки", callback_data="choose:purpose:p_subs")],
        [InlineKeyboardButton("Покупки", callback_data="choose:purpose:p_shop")],
        [InlineKeyboardButton("Путешествия", callback_data="choose:purpose:p_travel")],
        [InlineKeyboardButton("Другое", callback_data="choose:purpose:p_other")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")]
    ])
    await update.callback_query.edit_message_text("Для чего вам нужна карта?", reply_markup=kb)


async def choose_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # callback_data: choose:purpose:<value>
    _, _, value = update.callback_query.data.split(":", maxsplit=2)
    context.user_data.setdefault("choose", {})["purpose"] = value

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Виртуальная", callback_data="choose:cardtype:t_virtual")],
        [InlineKeyboardButton("Пластиковая", callback_data="choose:cardtype:t_plastic")],
        [InlineKeyboardButton("Не важно", callback_data="choose:cardtype:t_any")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])
    await update.callback_query.edit_message_text("Какой тип карты предпочитаете?", reply_markup=kb)


async def choose_cardtype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    _, _, value = update.callback_query.data.split(":", maxsplit=2)
    context.user_data.setdefault("choose", {})["cardtype"] = value

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Максимальная", callback_data="choose:anon:a_max")],
        [InlineKeyboardButton("Средняя", callback_data="choose:anon:a_med")],
        [InlineKeyboardButton("Не важно", callback_data="choose:anon:a_any")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])
    await update.callback_query.edit_message_text("Насколько важна анонимность?", reply_markup=kb)


async def choose_anon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    _, _, value = update.callback_query.data.split(":", maxsplit=2)
    data = context.user_data.setdefault("choose", {})
    data["anon"] = value

    # простая логика подбора:
    purpose = data.get("purpose")
    card_recommendation = "⭐ Универсальная виртуальная карта — оптимальный выбор."
    if purpose == "p_subs":
        card_recommendation = "⭐ Вам подойдёт Виртуальная USD-карта."
    elif purpose == "p_travel":
        card_recommendation = "⭐ Пластиковая мультивалютная карта — лучший выбор."

    result_text = (
        "*🎯 Результат подбора:*\n\n"
        f"{card_recommendation}\n\n"
        "_Менеджер уже получил вашу заявку._"
    )

    # Формируем заявку и отправляем менеджеру
    user = update.effective_user
    req = (
        "📩 *Новая заявка по подбору карты!*\n\n"
        f"Пользователь: @{user.username if user.username else user.full_name} (ID: {user.id})\n"
        f"Цель: {data.get('purpose')}\n"
        f"Тип карты: {data.get('cardtype')}\n"
        f"Анонимность: {data.get('anon')}\n"
    )

    if MANAGER_ID:
        try:
            await context.bot.send_message(MANAGER_ID, req, parse_mode="Markdown")
        except Exception as e:
            # уведомление пользователю о проблеме
            await update.callback_query.message.reply_text(f"Не удалось уведомить менеджера: {e}")

    # сохраняем историю
    REQUEST_HISTORY.append(req)

    await update.callback_query.edit_message_text(result_text, reply_markup=back_kb(), parse_mode="Markdown")
    # очищаем данные опроса
    context.user_data.pop("choose", None)


# -------------- Назад: возвращаемся в меню ----------------
async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Главное меню:", reply_markup=main_menu())


# -------------- История заявок (команда /history) -------------
async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if MANAGER_ID is None or user.id != MANAGER_ID:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not REQUEST_HISTORY:
        await update.message.reply_text("История пуста.")
        return

    # Отправляем последние 20 заявок
    text = "*📜 История заявок:* \n\n" + "\n\n".join(REQUEST_HISTORY[-20:])
    # если очень длинно, разобьем на сообщения
    MAX_LEN = 4000
    if len(text) <= MAX_LEN:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        # простая нарезка
        chunk = ""
        for line in REQUEST_HISTORY[-20:]:
            if len(chunk) + len(line) + 4 > MAX_LEN:
                await update.message.reply_text(chunk, parse_mode="Markdown")
                chunk = ""
            chunk += line + "\n\n"
        if chunk:
            await update.message.reply_text(chunk, parse_mode="Markdown")


# -------------- Регистрация обработчиков ----------------
def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("history", history_cmd))

    # callbacks (menu)
    app.add_handler(CallbackQueryHandler(types_handler, pattern="^types$"))
    app.add_handler(CallbackQueryHandler(purposes_handler, pattern="^purposes$"))
    app.add_handler(CallbackQueryHandler(faq_handler, pattern="^faq$"))
    app.add_handler(CallbackQueryHandler(manager_handler, pattern="^manager$"))

    # choose flow
    app.add_handler(CallbackQueryHandler(choose_start, pattern="^choose_start$"))
    app.add_handler(CallbackQueryHandler(choose_purpose, pattern="^choose:purpose:"))
    app.add_handler(CallbackQueryHandler(choose_cardtype, pattern="^choose:cardtype:"))
    app.add_handler(CallbackQueryHandler(choose_anon, pattern="^choose:anon:"))

    # back
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back$"))


# -------------- Запуск приложения ----------------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)
    print("Bot starting...")
    await app.initialize()
    # use polling — простая и надёжная опция
    await app.start()
    await app.updater.start_polling()
    # блокируем текущий поток до остановки
    await app.updater.idle()
    await app.stop()
    await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
