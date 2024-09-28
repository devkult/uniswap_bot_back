from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
import json
import logging

import httpx

logger = logging.getLogger("UniSwapBot")

@dataclass
class TelegramNotifier:
    token_bot: str
    http_client: httpx.AsyncClient = httpx.AsyncClient(timeout=30.0)
    delay: int = 0

    async def notify(
        self,
        chat_id: str,
        text: str,
        photo_url: str | None = None,
        button_url: str | None = None,
    ) -> None:
        """
        Send a notification to the specified chat ID. The notification
        can be either a text message or a photo message with a button.
        """
        if self.delay > 0:
            await asyncio.sleep(self.delay)
            self.delay = 0

        params = {
            "chat_id": chat_id,
            "parse_mode": "HTML",
        }

        if photo_url:
            params["photo"] = photo_url
            params["caption"] = text
            method = self.http_client.post
            url = f"https://api.telegram.org/bot{self.token_bot}/sendPhoto"
        else:
            method = self.http_client.post
            params["text"] = text
            url = f"https://api.telegram.org/bot{self.token_bot}/sendMessage"

        if button_url:
            params["reply_markup"] = json.dumps(
                {"inline_keyboard": [[{"text": "Explore", "url": button_url}]]}
            )

        try:
            response = await method(url, params=params)
            response.raise_for_status()
        except httpx.ReadTimeout:
            logger.error(f"Request to Telegram API timed out for chat ID {chat_id}")
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc, chat_id, text)
        except Exception as exc:
            logger.error(
                f"An unexpected error occurred while sending notification to chat ID {chat_id}: {exc}"
            )

    def _handle_http_error(
        self, exc: httpx.HTTPStatusError, reciever: str, notification: str
    ) -> None:
        if exc.response.status_code == 429:
            self.delay = int(exc.response.json().get("retry_after", 60))
            logger.warning(
                f"Rate limit exceeded. Setting delay for {self.delay} seconds for receiver {reciever}."
            )
            asyncio.create_task(self.retry_notify(reciever, notification))
        else:
            logger.error(
                f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
            )

    async def retry_notify(self, reciever: str, notification: str) -> None:
        await asyncio.sleep(self.delay)
        await self.notify(reciever, notification)
