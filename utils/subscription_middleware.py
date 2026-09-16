# -*- coding: utf-8 -*-
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import ADMIN_ID
from database import db
from texts import t
from keyboards.common import subscribe_kb


class MandatorySubscriptionMiddleware(BaseMiddleware):
    """Oddiy foydalanuvchining bot funksiyalaridan foydalanishidan oldin obunani tekshiradi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        user_id = user.id

        # Admin uchun majburiy obuna ishlamaydi.
        if user_id == ADMIN_ID:
            return await handler(event, data)

        # /start, til tanlash va kontakt yuborish orqali ro'yxatdan o'tish
        # majburiy obunadan oldin bajarilishi kerak.
        if isinstance(event, Message):
            event_text = event.text or ""
            if event_text == "/start" or event_text.startswith("/start "):
                return await handler(event, data)

            db_user = await db.get_user(user_id)
            if not db_user or not db_user.get("language") or db_user.get("registered") == 0:
                return await handler(event, data)

        elif isinstance(event, CallbackQuery):
            # Til tanlash va obunani tekshirish tugmalari bloklanmasin.
            callback_data = event.data or ""
            if callback_data.startswith("lang_") or callback_data == "check_subs":
                return await handler(event, data)

            db_user = await db.get_user(user_id)
            if not db_user or not db_user.get("language") or db_user.get("registered") == 0:
                return await handler(event, data)

        bot: Bot = data["bot"]
        channels = await db.get_mandatory_channels()
        if not channels:
            return await handler(event, data)

        subscribed = True
        for ch in channels:
            try:
                member = await bot.get_chat_member(ch["chat_id"], user_id)
                if member.status in ("left", "kicked"):
                    subscribed = False
                    break
            except Exception:
                subscribed = False
                break

        if subscribed:
            return await handler(event, data)

        db_user = await db.get_user(user_id)
        lang = db_user["language"] if db_user and db_user.get("language") else "uz"
        markup = subscribe_kb(channels, lang)

        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.answer(t(lang, "subscribe_required"), reply_markup=markup)
        else:
            await event.answer(t(lang, "subscribe_required"), reply_markup=markup)

        return None
