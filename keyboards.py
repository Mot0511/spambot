from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

BTN_CHANNELS_LIST = "📋 Список каналов"
BTN_ADD_CHANNEL = "➕ Добавить канал"
BTN_MESSAGES_LIST = "📝 Список сообщений"
BTN_ADD_MESSAGE = "➕ Добавить сообщение"


def admin_keyboard() -> ReplyKeyboardMarkup:
    """Создаёт стартовую админ-клавиатуру."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_CHANNELS_LIST),
                KeyboardButton(text=BTN_ADD_CHANNEL),
            ],
            [
                KeyboardButton(text=BTN_MESSAGES_LIST),
                KeyboardButton(text=BTN_ADD_MESSAGE),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


def channel_delete_kb(channel_id: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура с кнопкой удаления канала."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить из списка",
                    callback_data=f"del_channel:{channel_id}",
                ),
            ],
        ],
    )


def message_actions_kb(message_id: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура с кнопками рассылки и удаления текста рассылки."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Разослать",
                    callback_data=f"broadcast:{message_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить из списка",
                    callback_data=f"del_message:{message_id}",
                ),
            ],
        ],
    )
