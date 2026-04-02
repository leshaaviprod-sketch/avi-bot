#!/usr/bin/env python3
"""
🦅 AVI Bot — Telegram бот для движения творцов

Автор: AVI
Версия: 1.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

# === НАСТРОЙКА ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PRIVATE_CHANNEL_ID = os.getenv("PRIVATE_CHANNEL_ID", "@avi_private")
PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID", "@avi_channel")

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()


# === СОСТОЯНИЯ ===
class Form(StatesGroup):
    waiting_for_payment = State()
    waiting_feedback = State()


# === КЛАВИАТУРЫ ===

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🦅 О AVI"),
        KeyboardButton(text="🎵 Музыка"),
    )
    builder.row(
        KeyboardButton(text="💎 Подписка"),
        KeyboardButton(text="🔒 Закрытый канал"),
    )
    builder.row(
        KeyboardButton(text="❓ Помощь"),
        KeyboardButton(text="💬 Обратная связь"),
    )
    return builder.as_markup(resize_keyboard=True)


def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """Приветственная клавиатура с кнопками"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🦅 Узнать о AVI", callback_data="about"),
        InlineKeyboardButton(text="🎵 Слушать музыку", callback_data="music"),
    )
    builder.row(
        InlineKeyboardButton(text="💎 Стать подписчиком", callback_data="subscription"),
        InlineKeyboardButton(text="🔒 Доступ к закрытому", callback_data="private"),
    )
    builder.row(
        InlineKeyboardButton(text="📢 Открытый канал", url=f"https://t.me/{PUBLIC_CHANNEL_ID.strip('@')}"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ Есть вопросы?", callback_data="help"),
    )
    return builder.as_markup()


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора подписки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💎 МЕСЯЦ — 100₽", callback_data="sub_month"),
    )
    builder.row(
        InlineKeyboardButton(text="👑 ГОД — 1000₽ (экономия 200₽)", callback_data="sub_year"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"),
    )
    return builder.as_markup()


def get_about_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура раздела О AVI"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎵 Моя музыка", callback_data="music"),
        InlineKeyboardButton(text="📺 Контент", url="https://tiktok.com/@avi"),  # Заменить ссылку
    )
    builder.row(
        InlineKeyboardButton(text="💬 Подписаться", callback_data="subscription"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"),
    )
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_main"))
    return builder.as_markup()


# === ТЕКСТЫ СООБЩЕНИЙ ===

WELCOME_TEXT = """
🦅 <b>Добро пожаловать в AVI!</b>

Это движение тех, кто <b>создаёт</b>, а не потребляет.

Здесь ты найдёшь:
• Мою музыку и процесс её создания
• Ежедневную мотивацию для творчества
• Комьюнити единомышленников

Выбери, что тебе интересно 👇
"""

ABOUT_TEXT = """
🦅 <b>Кто такой AVI?</b>

Я — артист, который каждый день создаёт:
• Музыку
• Контент
• Движение

<b>Моя миссия:</b>
Показать, что ты тоже можешь создавать.
Не будь зрителем — будь творцом.

<i>"Твой день нужен AVI"</i>

Выбери действие ниже 👇
"""

MUSIC_TEXT = """
🎵 <b>Музыка AVI</b>

Здесь ты найдёшь все мои треки.

🎧 <b>Свежие релизы:</b>
• [Название трека 1] — ссылка
• [Название трека 2] — ссылка

📝 <i>Скоро выйдет новый трек! Подписчики узнают первыми.</i>
"""

SUBSCRIPTION_TEXT = """
💎 <b>Подписка на AVI</b>

Стань частью движения и получи:
• 🔒 Доступ к закрытому каналу
• ⚡ Ранний доступ к трекам
• 💬 Общение с единомышленниками
• 🎁 Эксклюзивный контент

<i>Выбери тариф ниже:</i>
"""

PRIVATE_CHANNEL_TEXT = """
🔒 <b>Закрытый канал AVI</b>

Это пространство для настоящих участников движения.

Там:
• Превью новых треков раньше всех
• Закулисье создания контента
• Общение с такими же творцами
• Возможность влиять на будущее AVI

<b>Доступ — по подписке.</b>

👇 Оформить подписку:
"""

HELP_TEXT = """
❓ <b>Помощь</b>

<b>Как пользоваться ботом:</b>
• Используй кнопки меню ниже
• Или нажимай на кнопки в сообщениях

<b>Вопросы и ответы:</b>
<b>Q: Как попасть в закрытый канал?</b>
A: Оформите подписку в разделе "💎 Подписка"

<b>Q: Что даёт подписка?</b>
A: Доступ к эксклюзивному контенту и комьюнити

<b>Q: Как связаться с AVI?</b>
A: Нажми "💬 Обратная связь"

💬 <i>Остались вопросы? Напиши в обратную связь!</i>
"""

THANKS_TEXT = """
💬 <b>Спасибо за сообщение!</b>

Я прочитаю его и обязательно отвечу.

⏳ Обычно отвечаю в течение 24 часов.

🦅 Создавай. Не будь зрителем.
"""


# === HANDLERS ===

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Команда /start"""
    await message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_keyboard(message.from_user.id),
    )
    await message.answer(
        "Выбери действие:",
        reply_markup=get_welcome_keyboard(),
    )


@router.callback_query(F.data == "back_main")
async def callback_back_main(call: CallbackQuery):
    """Возврат в главное меню"""
    await call.message.edit_text(
        WELCOME_TEXT,
        reply_markup=get_welcome_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "about")
async def callback_about(call: CallbackQuery):
    """Раздел О AVI"""
    await call.message.edit_text(
        ABOUT_TEXT,
        reply_markup=get_about_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "music")
async def callback_music(call: CallbackQuery):
    """Раздел Музыка"""
    await call.message.edit_text(
        MUSIC_TEXT,
        reply_markup=get_back_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "subscription")
async def callback_subscription(call: CallbackQuery):
    """Раздел Подписка"""
    await call.message.edit_text(
        SUBSCRIPTION_TEXT,
        reply_markup=get_subscription_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "private")
async def callback_private(call: CallbackQuery):
    """Раздел Закрытый канал"""
    await call.message.edit_text(
        PRIVATE_CHANNEL_TEXT,
        reply_markup=get_subscription_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "sub_month")
async def callback_sub_month(call: CallbackQuery):
    """Подписка на месяц"""
    user_id = call.from_user.id

    # Проверка доступа к закрытому каналу
    try:
        member = await bot.get_chat_member(PRIVATE_CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            await call.answer("✅ У вас уже есть доступ к закрытому каналу!", show_alert=True)
            return
    except Exception:
        pass  # Не участник

    await call.answer("🔧 Оплата будет доступна скоро. Напишите @avi для оформления подписки вручную.", show_alert=True)


@router.callback_query(F.data == "sub_year")
async def callback_sub_year(call: CallbackQuery):
    """Подписка на год"""
    await call.answer("🔧 Оплата будет доступна скоро. Напишите @avi для оформления подписки вручную.", show_alert=True)


@router.callback_query(F.data == "help")
async def callback_help(call: CallbackQuery):
    """Раздел Помощь"""
    await call.message.edit_text(
        HELP_TEXT,
        reply_markup=get_back_keyboard(),
    )
    await call.answer()


@router.message(F.text == "🦅 О AVI")
async def msg_about(message: Message):
    """Кнопка О AVI"""
    await message.answer(
        ABOUT_TEXT,
        reply_markup=get_about_keyboard(),
    )


@router.message(F.text == "🎵 Музыка")
async def msg_music(message: Message):
    """Кнопка Музыка"""
    await message.answer(
        MUSIC_TEXT,
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == "💎 Подписка")
async def msg_subscription(message: Message):
    """Кнопка Подписка"""
    await message.answer(
        SUBSCRIPTION_TEXT,
        reply_markup=get_subscription_keyboard(),
    )


@router.message(F.text == "🔒 Закрытый канал")
async def msg_private(message: Message):
    """Кнопка Закрытый канал"""
    await message.answer(
        PRIVATE_CHANNEL_TEXT,
        reply_markup=get_subscription_keyboard(),
    )


@router.message(F.text == "❓ Помощь")
async def msg_help(message: Message):
    """Кнопка Помощь"""
    await message.answer(
        HELP_TEXT,
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == "💬 Обратная связь")
async def msg_feedback(message: Message, state: FSMContext):
    """Обратная связь"""
    await state.set_state(Form.waiting_feedback)
    await message.answer(
        "💬 <b>Напишите ваше сообщение:</b>\n\nЭто может быть вопрос, предложение или просто доброе слово)",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(Form.waiting_feedback)
async def process_feedback(message: Message, state: FSMContext):
    """Обработка обратной связи"""
    feedback = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "нет username"

    # Отправляем админу (замени ADMIN_ID на свой ID)
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    if ADMIN_ID != 0:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"📨 <b>Новое сообщение от пользователя!</b>\n\n"
                f"👤 ID: {user_id}\n"
                f"🔗 Username: @{username}\n\n"
                f"💬 <b>Сообщение:</b>\n{feedback}",
            )
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {e}")

    await state.clear()
    await message.answer(
        THANKS_TEXT,
        reply_markup=get_main_keyboard(user_id),
    )


# === ЗАПУСК ===

async def main():
    """Запуск бота"""
    dp.include_router(router)

    # Удаляем вебхуки, если были
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("🦅 AVI Bot запущен!")

    # Стартуем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
