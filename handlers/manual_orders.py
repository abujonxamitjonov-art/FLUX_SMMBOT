# -*- coding: utf-8 -*-
import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from texts import t
from states import UsernameOrder
from keyboards.common import confirm_cancel_kb, back_kb
from keyboards.admin import admin_order_action_kb
from utils.order_channel import post_new_order
from config import ADMIN_ID

router = Router()


@router.message(UsernameOrder.entering_username)
async def process_username(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user["language"]
    username = message.text.strip()
    if not username:
        await message.answer(t(lang, "enter_username"))
        return

    data = await state.get_data()
    await state.update_data(username=username)
    await state.set_state(UsernameOrder.confirming)

    text = t(lang, "confirm_order_username", service=data["title"], username=username,
              price=f"{data['price']:,}".replace(",", " "))
    await message.answer(text, reply_markup=confirm_cancel_kb(lang, "manual_confirm", "manual_cancel"))


@router.callback_query(F.data == "manual_cancel")
async def cb_manual_cancel(callback: CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await state.set_state(UsernameOrder.entering_username)
    await callback.message.edit_text(t(lang, "enter_username"))
    await callback.answer()


@router.callback_query(F.data == "manual_confirm")
async def cb_manual_confirm(callback: CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    data = await state.get_data()
    price = data["price"]

    if user["balance"] < price:
        await callback.message.edit_text(t(lang, "not_enough_balance"))
        await state.clear()
        await callback.answer()
        return

    await db.update_balance(user["user_id"], -price)
    order_id = await db.create_order(
        user["user_id"], data["order_kind"], data["title"], data["amount"], price,
        status="processing", extra=json.dumps({"username": data["username"]}),
    )

    customer_name = f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
    await post_new_order(callback.bot, order_id, customer_name, data["title"], price, data["amount"])

    await callback.bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi buyurtma\n\n"
        f"🛍 Xizmat: {data['title']}\n"
        f"📦 Miqdor: {data['amount']}\n"
        f"👤 Username/ID: {data['username']}\n"
        f"💰 Narx: {price:,} so'm\n"
        f"🆔 Buyurtma: #{order_id}\n\n"
        f"Bajargandan so'ng 'Bajarildi' tugmasini bosing.".replace(",", " "),
        reply_markup=admin_order_action_kb(order_id),
    )

    await callback.message.edit_text(t(lang, "order_accepted_wait"))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("order_done_"))
async def cb_order_done(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔️ Sizga ruxsat yo'q", show_alert=True)
        return

    order_id = int(callback.data.replace("order_done_", ""))
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("❌ Buyurtma topilmadi", show_alert=True)
        return

    await db.update_order_status(order_id, "completed")

    order_user = await db.get_user(order["user_id"])
    lang = order_user["language"] if order_user else "uz"

    if order["order_type"] == "premium":
        text = t(lang, "order_completed_premium", duration=order["amount"], user_id=order["user_id"])
    else:
        text = t(lang, "order_completed_generic")

    try:
        await callback.bot.send_message(order["user_id"], text)
    except Exception:
        pass

    try:
        await callback.message.edit_text(callback.message.text + "\n\n✅ BAJARILDI")
    except Exception:
        pass

    # Kanal xabarini yangilash
    if order["channel_message_id"]:
        from config import ORDERS_CHANNEL
        from utils.order_channel import channel_order_status_kb
        try:
            await callback.bot.edit_message_reply_markup(
                ORDERS_CHANNEL, order["channel_message_id"],
                reply_markup=channel_order_status_kb(order_id),
            )
        except Exception:
            pass

    await callback.answer("✅ Bajarildi deb belgilandi")


@router.callback_query(F.data.startswith("order_status_"))
async def cb_order_status_check(callback: CallbackQuery):
    order_id = int(callback.data.replace("order_status_", ""))
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("❌ Buyurtma topilmadi", show_alert=True)
        return

    status = order["status"]

    # API orqali bajariladigan buyurtmalar uchun real vaqtda tekshirish
    if order["order_type"] == "smm" and order["external_id"]:
        from utils import smm_api
        result = await smm_api.get_order_status(int(order["external_id"]))
        api_status = result.get("status", "").lower()
        if "complet" in api_status:
            status = "completed"
            await db.update_order_status(order_id, "completed")
        elif "cancel" in api_status:
            status = "cancelled"
            await db.update_order_status(order_id, "cancelled")
        else:
            status = "processing"

    from utils.order_channel import status_label
    await callback.answer(status_label(status), show_alert=True)
