import asyncio
import logging

from telethon import TelegramClient
from telethon.errors import MsgIdInvalidError
from telethon.tl.functions.messages import GetDiscussionMessageRequest

logger = logging.getLogger(__name__)


class TelegramService:
    # Пауза между отправками, чтобы не упереться в flood-лимиты Telegram.
    delay_between_posts: float = 2.0

    client: TelegramClient

    def __init__(self, api_id, api_hash):
        self.client = TelegramClient("session", int(api_id), api_hash)

    async def start(self):
        """Подключается к Telegram и проверяет авторизацию аккаунта."""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError(
                "Telegram-аккаунт не авторизован. "
                "Необходимо пройти авторизацию (session.session)."
            )

    async def get_channel_title(self, channel_link: str) -> str:
        """Возвращает название канала по ссылке или @username."""
        channel = await self.client.get_entity(channel_link)
        title = getattr(channel, "title", None)
        if not title:
            raise RuntimeError(f"Не удалось получить название для '{channel_link}'")
        return title

    async def post_comment(self, channel_link: str, text: str):
        """Отправляет комментарий под самым свежим постом канала."""
        channel = await self.client.get_entity(channel_link)

        # get_messages возвращает посты от новых к старым — берём первые,
        # пропуская service-сообщения (pinned, привязка группы и т.п.).
        posts = [m for m in await self.client.get_messages(channel, limit=20) if m and not m.action][:5]
        if not posts:
            raise RuntimeError("Posts not found")

        last_error: Exception | None = None

        for post in posts:
            logger.info("The last post: %s", post.id)

            try:
                comment = await self.client.send_message(
                    entity=channel,
                    message=text,
                    comment_to=post.id,
                )
            except MsgIdInvalidError as e:
                # Пост удалён, скрыт или это не пост канала — идём к следующему.
                last_error = e
                logger.warning(
                    "Пост %s в %s не принимает комментарии, пробуем следующий",
                    post.id,
                    channel_link,
                )
                continue

            logger.info('Comment "%s" was sent to %s', text, channel_link)
            return comment

        raise RuntimeError(f"Не удалось отправить комментарий в {channel_link}: {last_error}")

    async def broadcast(self, channels: list[dict], text: str) -> list[dict]:
        """Рассылает текст по всем каналам, поочерёдно комментируя их.

        Возвращает список результатов вида
        {"link": str, "ok": bool, "error": str | None}.
        """
        results: list[dict] = []

        for index, channel in enumerate(channels, start=1):
            link = channel["link"]
            try:
                await self.post_comment(link, text)
                results.append({"link": link, "ok": True, "error": None})
            except Exception as e:
                logger.exception("Ошибка рассылки в %s", link)
                results.append({"link": link, "ok": False, "error": str(e)})

            if index < len(channels):
                await asyncio.sleep(self.delay_between_posts)

        return results

