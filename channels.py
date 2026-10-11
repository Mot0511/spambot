import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

from keyboards import BTN_CHANNELS_LIST, BTN_ADD_CHANNEL, admin_keyboard, channel_delete_kb

router = Router(name="channels")


class AddChannelStates(StatesGroup):
    waiting_link = State()


# ----------------------------------------------------------------------
# 📋 Список каналов
# ----------------------------------------------------------------------

@router.message(F.text == BTN_CHANNELS_LIST)
async def show_channels(message: Message, channel_service):
    channels = channel_service.get_channels()
    if not channels:
        await message.answer("Список пуст.")
        return
    for i, ch in enumerate(channels):
        await message.answer(
            f"{i+1}. {ch['title']} — {ch['link']}",
            reply_markup=channel_delete_kb(ch["id"]),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )


# ----------------------------------------------------------------------
# 🗑 Удалить канал из списка
# ----------------------------------------------------------------------

@router.callback_query(F.data.startswith("del_channel:"))
async def delete_channel(callback: CallbackQuery, channel_service):
    channel_id = int(callback.data.split(":")[1])
    try:
        deleted = channel_service.delete_channel(channel_id)
        if deleted:
            await callback.message.delete()
            await callback.answer("Канал удалён")
        else:
            await callback.answer("Канал не найден", show_alert=True)
    except Exception as e:
        logging.exception("Ошибка при удалении канала")
        await callback.answer(
            f"⚠️ Ошибка удаления: {e}",
            show_alert=True,
        )


# ----------------------------------------------------------------------
# ➕ Добавить канал
# ----------------------------------------------------------------------

@router.message(F.text == BTN_ADD_CHANNEL)
async def add_channel_start(message: Message, state: FSMContext):
    await state.set_state(AddChannelStates.waiting_link)
    await message.answer(
        "Отправь ссылку (или ссылки, каждая в новой строке) на канал или его @username\n"
        "Для отмены — /start"
    )


@router.message(AddChannelStates.waiting_link, F.text)
async def add_channel_process(message: Message, state: FSMContext, tg_service, channel_service):
    links = message.text.strip().split('\n')
    try:
        for link in links:
            title = await tg_service.get_channel_title(link)
            channel_service.add_channel(title, link)
            await message.answer(
                f"✅ Канал <b>{title}</b> добавлен",
                reply_markup=admin_keyboard(),
            )
    except Exception as e:
        logging.exception("Ошибка при добавлении канала")
        await message.answer(
            f"⚠️ Не удалось добавить канал\n\n"
            f"{e}"
        )
    finally:
        await state.clear()
