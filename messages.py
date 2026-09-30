import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards import BTN_MESSAGES_LIST, BTN_ADD_MESSAGE, admin_keyboard, message_actions_kb

router = Router(name="messages")


class AddMessageStates(StatesGroup):
    waiting_text = State()


# ----------------------------------------------------------------------
# 📝 Список сообщений
# ----------------------------------------------------------------------

@router.message(F.text == BTN_MESSAGES_LIST)
async def show_messages(message: Message, message_service):
    messages = message_service.get_messages()
    if not messages:
        await message.answer("Список пуст.")
        return
    for msg in messages:
        await message.answer(
            f"{msg['id']}. {msg['text']}",
            reply_markup=message_actions_kb(msg["id"]),
        )


# ----------------------------------------------------------------------
# 📤 Разослать сообщение по всем каналам
# ----------------------------------------------------------------------

@router.callback_query(F.data.startswith("broadcast:"))
async def broadcast_message(
    callback: CallbackQuery,
    message_service,
    channel_service,
    tg_service,
):
    message_id = int(callback.data.split(":")[1])
    record = message_service.get_message(message_id)
    if not record:
        await callback.answer("Сообщение не найдено", show_alert=True)
        return

    channels = channel_service.get_channels()
    if not channels:
        await callback.answer("Список каналов пуст", show_alert=True)
        return

    await callback.answer()
    status = await callback.message.answer(
        f"📤 Рассылаю в {len(channels)} каналов..."
    )

    results = await tg_service.broadcast(channels, record["text"])

    sent = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    report = [
        f"✅ Рассылка завершена: {len(sent)} из {len(results)} каналов"
    ]
    if failed:
        report.append("\nНе удалось отправить:")
        report += [f"• {r['link']}: {r['error']}" for r in failed]

    await status.edit_text("\n".join(report))


# ----------------------------------------------------------------------
# 🗑 Удалить сообщение из списка
# ----------------------------------------------------------------------

@router.callback_query(F.data.startswith("del_message:"))
async def delete_message(callback: CallbackQuery, message_service):
    message_id = int(callback.data.split(":")[1])
    try:
        deleted = message_service.delete_message(message_id)
        if deleted:
            # Удаляем inline-клавиатуру с кнопки "Удалить"
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.answer("Сообщение удалено")
        else:
            await callback.answer("Сообщение не найдено", show_alert=True)
    except Exception as e:
        logging.exception("Ошибка при удалении сообщения")
        await callback.answer(
            f"⚠️ Ошибка удаления: {e}",
            show_alert=True,
        )


# ----------------------------------------------------------------------
# ➕ Добавить сообщение
# ----------------------------------------------------------------------

@router.message(F.text == BTN_ADD_MESSAGE)
async def add_message_start(message: Message, state: FSMContext):
    await state.set_state(AddMessageStates.waiting_text)
    await message.answer(
        "Отправь текст сообщения для рассылки\n"
        "Для отмены — /start"
    )


@router.message(AddMessageStates.waiting_text, F.text)
async def add_message_process(message: Message, state: FSMContext, message_service):
    text = message.text.strip()
    try:
        message_service.add_message(text)
        await message.answer(
            "✅ Сообщение добавлено",
            reply_markup=admin_keyboard(),
        )
    except Exception as e:
        logging.exception("Ошибка при добавлении сообщения")
        await message.answer(
            f"⚠️ Не удалось добавить сообщение\n\n"
            f"{e}"
        )
    finally:
        await state.clear()
