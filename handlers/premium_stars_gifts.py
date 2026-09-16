# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database import db
from texts import t
from states import UsernameOrder
from keyboards.services import (
    stars_premium_root_kb, stars_amounts_kb, premium_durations_kb,
    gift_groups_kb, gift_items_kb,
)
from config import STARS_PRICES, PREMIUM_PRICES, GIFT_GROUPS, ADMIN_USERNAME

router = Router()


@router.callback_query(F.data == "svc_stars_premium")
async def cb_sp_root(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_service"), reply_markup=stars_premium_root_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "sp_root")
async def cb_sp_root_back(callback: CallbackQuery):
    await cb_sp_root(callback)


@router.callback_query(F.data == "sp_stars")
async def cb_sp_stars(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_stars_amount"), reply_markup=stars_amounts_kb(lang, STARS_PRICES))
    await callback.answer()


@router.callback_query(F.data.startswith("stars_pick_"))
async def cb_stars_pick(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.replace("stars_pick_", ""))
    price = STARS_PRICES.get(amount)
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await state.update_data(order_kind="stars", title=f"Telegram Stars {amount}", amount=f"{amount} ta", price=price)
    await state.set_state(UsernameOrder.entering_username)
    await callback.message.edit_text(t(lang, "enter_username"))
    await callback.answer()


@router.callback_query(F.data == "sp_premium")
async def cb_sp_premium(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_premium_duration"), reply_markup=premium_durations_kb(lang, PREMIUM_PRICES))
    await callback.answer()


@router.callback_query(F.data.startswith("premium_pick_"))
async def cb_premium_pick(callback: CallbackQuery, state: FSMContext):
    months = callback.data.replace("premium_pick_", "")
    price = PREMIUM_PRICES.get(months)
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]

    if months == "1":
        # 1 oylik - username so'ralmaydi, to'g'ridan-to'g'ri admin bilan bog'lanadi
        if user["balance"] < price:
            await callback.message.edit_text(t(lang, "not_enough_balance"))
            await callback.answer()
            return
        contact_text = (
            f"Assalomu alaykum, men 1 oylik premium uchun botga to'lov qildim. "
            f"Mening ID: {user['user_id']}"
        )
        import urllib.parse
        url = f"https://t.me/{ADMIN_USERNAME}?text={urllib.parse.quote(contact_text)}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "contact_admin_btn"), url=url)],
        ])
        await db.update_balance(user["user_id"], -price)
        order_id = await db.create_order(
            user["user_id"], "premium", "Telegram Premium 1 oylik", "1 oylik", price, status="processing",
        )
        from utils.order_channel import post_new_order
        customer_name = f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
        await post_new_order(callback.bot, order_id, customer_name, "Telegram Premium", price, "1 oylik")

        # adminga xabar
        from config import ADMIN_ID
        from keyboards.admin import admin_order_action_kb
        await callback.bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi premium buyurtmasi — 1 oylik, to'lov qilingan.\n"
            f"Mijoz ID: {user['user_id']}\n\n"
            f"Premium olib berganingizdan so'ng 'Bajarildi' tugmasini bosing.",
            reply_markup=admin_order_action_kb(order_id),
        )

        await callback.message.edit_text(t(lang, "premium_1m_contact"), reply_markup=kb)
        await callback.answer()
        return

    await state.update_data(order_kind="premium", title=f"Telegram Premium {months} oylik",
                             amount=f"{months} oylik", price=price)
    await state.set_state(UsernameOrder.entering_username)
    await callback.message.edit_text(t(lang, "enter_username"))
    await callback.answer()


@router.callback_query(F.data == "svc_gifts")
async def cb_gifts_root(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_gift_group"), reply_markup=gift_groups_kb(lang, GIFT_GROUPS))
    await callback.answer()


@router.callback_query(F.data.startswith("gift_group_"))
async def cb_gift_group(callback: CallbackQuery):
    group_id = callback.data.replace("gift_group_", "")
    group = GIFT_GROUPS.get(group_id)
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    if not group:
        await callback.answer("❌ Xatolik", show_alert=True)
        return
    await callback.message.edit_text(t(lang, "choose_gift"), reply_markup=gift_items_kb(lang, group_id, group["gifts"]))
    await callback.answer()


@router.callback_query(F.data.startswith("gift_pick_"))
async def cb_gift_pick(callback: CallbackQuery, state: FSMContext):
    _, _, group_id, gift_key = callback.data.split("_", 3)
    group = GIFT_GROUPS.get(group_id)
    gift = group["gifts"].get(gift_key) if group else None
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    if not gift:
        await callback.answer("❌ Xatolik", show_alert=True)
        return
    price = group["price"]
    await state.update_data(order_kind="gift", title=f"{gift['emoji']} {gift['name']}",
                             amount=f"{group_id} talik", price=price)
    await state.set_state(UsernameOrder.entering_username)
    await callback.message.edit_text(t(lang, "enter_username"))
    await callback.answer()
