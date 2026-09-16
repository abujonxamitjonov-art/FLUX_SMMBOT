# -*- coding: utf-8 -*-
"""Buyurtmalar kanaliga (ORDERS_CHANNEL) post qilish."""
from aiogram import Bot
from config import ORDERS_CHANNEL
from keyboards.admin import channel_order_status_kb
from database import db


async def post_new_order(bot: Bot, order_id: int, customer_name: str, service_title: str,
                          price: int, amount: str = ""):
    text = (
        f"🆕 <b>Yangi buyurtma</b>\n\n"
        f"👤 Mijoz: {customer_name}\n"
        f"🛍 Xizmat: {service_title}"
        f"{f' ({amount})' if amount else ''}\n"
        f"💰 Narx: {price:,} so'm\n"
        f"🆔 Buyurtma: #{order_id}"
    ).replace(",", " ")
    try:
        msg = await bot.send_message(
            ORDERS_CHANNEL, text, parse_mode="HTML",
            reply_markup=channel_order_status_kb(order_id),
        )
        await db.set_order_channel_message(order_id, msg.message_id)
    except Exception:
        pass  # kanal sozlanmagan bo'lishi mumkin, botni to'xtatmaymiz


STATUS_LABELS = {
    "pending": "🕐 Jarayonda",
    "processing": "🕐 Jarayonda",
    "completed": "✅ Bajarildi",
    "cancelled": "❌ Bekor qilindi",
}


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status.lower(), f"🕐 {status}")
