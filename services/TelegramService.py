from telethon import TelegramClient
from telethon.tl.functions.messages import GetDiscussionMessageRequest


class TelegramService:
    client: TelegramClient

    def __init__(self, api_id, api_hash):
        self.client = TelegramClient("session", int(api_id), api_hash)

    async def _post_comment(self, channel_link: str, text: str):
        channel = await self.client.get_entity(channel_link)
        messages = await self.client.get_messages(channel, limit=10)
        if not messages:
            raise RuntimeError("Posts not found")

        post = messages[0]
        print(f"The last post: {post.id}")

        result = await self.client(
            GetDiscussionMessageRequest(
                peer=channel,
                msg_id=post.id
            )
        )

        if not result.messages:
            raise RuntimeError("Discussion not found")

        discussion_message = result.messages[0]
        comment = await self.client.send_message(
            entity=discussion_message.peer_id,
            message=text,
            reply_to=discussion_message.id
        )

        print(f'Comment "{text}" was sent')
        return comment

    async def post_comment(self, channel_link: str, text: str):
        with self.client:
            self.client.loop.run_until_complete(self._post_comment(channel_link, text))

