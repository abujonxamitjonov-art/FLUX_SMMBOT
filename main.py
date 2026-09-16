# -*- coding: utf-8 -*-
import asyncio
import logging
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from config import BOT_TOKEN, ADMIN_ID
from database import db
from texts import t

from handlers import user, services, numbers, premium_stars_gifts, manual_orders, topup, orders, referral, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def unblock_watcher(bot: Bot):
    """Blok muddati tugagan foydalanuvchilarni tekshirib, ularga xabar beradi."""
    while True:
        await asyncio.sleep(60)
        try:
            conn = db.get_db()
            cur = await conn.execute(
                "SELECT user_id, language FROM users WHERE is_blocked=1 AND blocked_until>0 AND blocked_until<=?",
                (int(time.time()),),
            )
            rows = await cur.fetchall()
            for user_id, lang in rows:
                await db.unblock_user(user_id)
                try:
                    await bot.send_message(user_id, t(lang or "uz", "unblocked_msg"))
                except Exception:
                    pass
        except Exception as e:
            logger.exception("unblock_watcher xatosi: %s", e)


async def active_reminder_task(bot: Bot):
    """Har 24 soatda oddiy foydalanuvchilarga bot faolligi haqida xabar."""
    while True:
        await asyncio.sleep(24 * 3600)
        try:
            user_ids = await db.get_all_user_ids()
            for uid in user_ids:
                if uid == ADMIN_ID:
                    continue
                try:
                    user_row = await db.get_user(uid)
                    lang = user_row["language"] if user_row else "uz"
                    await bot.send_message(uid, t(lang, "active_reminder"))
                except Exception:
                    pass
                await asyncio.sleep(0.05)  # flood limitga tushmaslik uchun
        except Exception as e:
            logger.exception("active_reminder_task xatosi: %s", e)


async def set_admin_commands(bot: Bot):
    default_commands = [BotCommand(command="start", description="Botni ishga tushirish")]
    await bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())

    admin_commands = default_commands + [
        BotCommand(command="admin", description="Admin buyruqlari ro'yxati"),
        BotCommand(command="stats", description="Statistika"),
        BotCommand(command="broadcast", description="Barchaga xabar yuborish"),
        BotCommand(command="add_channel", description="Majburiy kanal qo'shish"),
        BotCommand(command="list_channels", description="Majburiy kanallar ro'yxati"),
        BotCommand(command="remove_channel", description="Majburiy kanalni o'chirish"),
        BotCommand(command="set_smm_margin", description="SMM margin sozlash"),
        BotCommand(command="set_number_margin", description="Nomer olish margin sozlash"),
        BotCommand(command="user", description="Foydalanuvchi ma'lumoti"),
    ]
    try:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
    except Exception:
        pass  # admin hali botga /start bosmagan bo'lishi mumkin


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable topilmadi! Render'da sozlang.")

    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(services.router)
    dp.include_router(numbers.router)
    dp.include_router(premium_stars_gifts.router)
    dp.include_router(manual_orders.router)
    dp.include_router(topup.router)
    dp.include_router(orders.router)
    dp.include_router(referral.router)

    await set_admin_commands(bot)

    asyncio.create_task(unblock_watcher(bot))
    asyncio.create_task(active_reminder_task(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
