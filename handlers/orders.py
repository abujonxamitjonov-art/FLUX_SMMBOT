# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from texts import t
from keyboards.common import back_kb
from utils.order_channel import status_label

router = Router()

STATUS_EMOJI = {
    "pending": "🕐",
    "processing": "🕐",
    "completed": "✅",
    "cancelled": "❌",
}


@router.callback_query(F.data == "menu_orders")
async def cb_my_orders(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    orders = await db.get_user_orders(callback.from_user.id, limit=15)

    if not orders:
        await callback.message.edit_text(t(lang, "no_orders"), reply_markup=back_kb(lang, "back_main_menu"))
        await callback.answer()
        return

    lines = [t(lang, "orders_list_title"), ""]
    for o in orders:
        emoji = STATUS_EMOJI.get(o["status"], "🕐")
        lines.append(
            f"{emoji} #{o['order_id']} — {o['title']} "
            f"({o['amount']}) — {o['price']:,} so'm — {o['status']}".replace(",", " ")
        )
    await callback.message.edit_text("\n".join(lines), reply_markup=back_kb(lang, "back_main_menu"))
    await callback.answer()
