# -*- coding: utf-8 -*-
import asyncio
import time
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import db
from texts import t
from states import TopUp
from keyboards.topup import topup_methods_kb, cancel_topup_kb, admin_topup_review_kb, admin_confirm_kb
from config import (
    MIN_TOPUP_AMOUNT, PAYMENT_TIMEOUT_MINUTES, BLOCK_DURATION_HOURS,
    HUMO_CARD, VISA_CARD, MASTERCARD_CARD, CARD_OWNER, ADMIN_ID,
    REFERRAL_FIRST_PAYMENT_BONUS,
)

router = Router()


@router.callback_query(F.data == "menu_topup")
async def cb_topup_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await state.set_state(TopUp.choosing_method)
    await callback.message.edit_text(t(lang, "choose_topup_method"), reply_markup=topup_methods_kb(lang))
    await callback.answer()


@router.callback_query(F.data.in_(["topup_uzcard", "topup_foreign"]))
async def cb_topup_method(callback: CallbackQuery, state: FSMContext):
    method = "humo" if callback.data == "topup_uzcard" else "foreign"
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await state.update_data(method=method)
    await state.set_state(TopUp.entering_amount)
    await callback.message.edit_text(t(lang, "enter_topup_amount", min=f"{MIN_TOPUP_AMOUNT:,}".replace(",", " ")))
    await callback.answer()


@router.message(TopUp.entering_amount)
async def process_topup_amount(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user["language"]
    try:
        amount = int("".join(ch for ch in message.text if ch.isdigit()))
    except ValueError:
        amount = 0

    if amount < MIN_TOPUP_AMOUNT:
        await message.answer(t(lang, "amount_too_low", min=f"{MIN_TOPUP_AMOUNT:,}".replace(",", " ")))
        return

    data = await state.get_data()
    method = data["method"]
    expires_at = int(time.time()) + PAYMENT_TIMEOUT_MINUTES * 60

    topup_id = await db.create_topup(user["user_id"], amount, method, expires_at)
    await state.update_data(topup_id=topup_id, amount=amount)
    await state.set_state(TopUp.waiting_receipt)

    if method == "humo":
        text = t(lang, "card_details_uz", card=HUMO_CARD, owner=CARD_OWNER,
                  amount=f"{amount:,}".replace(",", " "), minutes=PAYMENT_TIMEOUT_MINUTES,
                  block_hours=BLOCK_DURATION_HOURS)
    else:
        text = t(lang, "card_details_foreign", visa=VISA_CARD, mastercard=MASTERCARD_CARD,
                  owner=CARD_OWNER, amount=f"{amount:,}".replace(",", " "),
                  minutes=PAYMENT_TIMEOUT_MINUTES, block_hours=BLOCK_DURATION_HOURS)

    await message.answer(text, reply_markup=cancel_topup_kb(lang))
    await message.answer(t(lang, "send_receipt"))

    asyncio.create_task(_expire_topup_later(message.bot, topup_id, PAYMENT_TIMEOUT_MINUTES * 60, state))


async def _expire_topup_later(bot: Bot, topup_id: int, delay_seconds: int, state: FSMContext):
    await asyncio.sleep(delay_seconds)
    topup = await db.get_topup(topup_id)
    if not topup or topup["status"] != "waiting_receipt":
        return
    await db.set_topup_status(topup_id, "expired")
    user = await db.get_user(topup["user_id"])
    lang = user["language"] if user else "uz"
    try:
        current_state = await state.get_state()
        if current_state == TopUp.waiting_receipt.state:
            data = await state.get_data()
            if data.get("topup_id") == topup_id:
                await state.clear()
    except Exception:
        pass
    try:
        await bot.send_message(topup["user_id"], t(lang, "topup_expired", minutes=PAYMENT_TIMEOUT_MINUTES))
    except Exception:
        pass


@router.callback_query(F.data == "topup_cancel")
async def cb_topup_cancel(callback: CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    data = await state.get_data()
    if data.get("topup_id"):
        await db.set_topup_status(data["topup_id"], "expired")
    await state.clear()
    await callback.message.edit_text(t(lang, "cancelled"))
    await callback.answer()


@router.message(TopUp.waiting_receipt, F.photo | F.document)
async def process_receipt(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user["language"]
    data = await state.get_data()
    topup_id = data.get("topup_id")
    if not topup_id:
        return

    topup = await db.get_topup(topup_id)
    if not topup or topup["status"] != "waiting_receipt":
        await message.answer(t(lang, "topup_expired", minutes=PAYMENT_TIMEOUT_MINUTES))
        await state.clear()
        return

    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    await db.set_topup_receipt(topup_id, file_id)
    await state.clear()

    await message.answer(t(lang, "receipt_received"))

    customer_name = f"{message.from_user.full_name} (@{message.from_user.username})" if message.from_user.username else message.from_user.full_name
    caption = (
        f"🧾 Yangi to'lov cheki\n\n"
        f"👤 Mijoz: {customer_name}\n"
        f"🆔 ID: {user['user_id']}\n"
        f"💵 Summa: {topup['amount']:,} so'm\n"
        f"💳 Usul: {topup['method']}\n"
        f"🆔 Topup: #{topup_id}"
    ).replace(",", " ")

    if message.photo:
        admin_msg = await message.bot.send_photo(
            ADMIN_ID, file_id, caption=caption, reply_markup=admin_topup_review_kb(topup_id)
        )
    else:
        admin_msg = await message.bot.send_document(
            ADMIN_ID, file_id, caption=caption, reply_markup=admin_topup_review_kb(topup_id)
        )
    await db.set_topup_admin_message(topup_id, admin_msg.message_id)


@router.callback_query(F.data.startswith("topup_approve_"))
async def cb_topup_approve_step1(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔️ Ruxsat yo'q", show_alert=True)
        return
    topup_id = int(callback.data.replace("topup_approve_", ""))
    await callback.message.edit_reply_markup(reply_markup=admin_confirm_kb("approve", topup_id))
    await callback.answer()


@router.callback_query(F.data.startswith("topup_reject_"))
async def cb_topup_reject_step1(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔️ Ruxsat yo'q", show_alert=True)
        return
    topup_id = int(callback.data.replace("topup_reject_", ""))
    await callback.message.edit_reply_markup(reply_markup=admin_confirm_kb("reject", topup_id))
    await callback.answer()


@router.callback_query(F.data.startswith("back_approve_") | F.data.startswith("back_reject_"))
async def cb_topup_back_to_review(callback: CallbackQuery):
    topup_id = int(callback.data.split("_")[-1])
    await callback.message.edit_reply_markup(reply_markup=admin_topup_review_kb(topup_id))
    await callback.answer()


@router.callback_query(F.data.startswith("conf_approve_"))
async def cb_topup_confirm_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔️ Ruxsat yo'q", show_alert=True)
        return
    topup_id = int(callback.data.replace("conf_approve_", ""))
    topup = await db.get_topup(topup_id)
    if not topup or topup["status"] not in ("pending_review",):
        await callback.answer("❌ Bu chek allaqachon ko'rib chiqilgan", show_alert=True)
        return

    await db.set_topup_status(topup_id, "approved")
    await db.update_balance(topup["user_id"], topup["amount"])

    user = await db.get_user(topup["user_id"])
    lang = user["language"] if user else "uz"

    # Referal - birinchi to'lov bonusi
    if user and user["referrer_id"] and not user["ref_first_payment_done"]:
        await db.update_balance(user["referrer_id"], REFERRAL_FIRST_PAYMENT_BONUS)
        await db.mark_ref_first_payment_done(user["user_id"])
        try:
            ref_user = await db.get_user(user["referrer_id"])
            ref_lang = ref_user["language"] if ref_user else "uz"
            await callback.bot.send_message(
                user["referrer_id"],
                f"🎉 Taklif qilgan do'stingiz birinchi to'lovni amalga oshirdi! "
                f"+{REFERRAL_FIRST_PAYMENT_BONUS} so'm bonus hisobingizga qo'shildi."
            )
        except Exception:
            pass

    try:
        await callback.bot.send_message(
            topup["user_id"],
            t(lang, "topup_approved", amount=f"{topup['amount']:,}".replace(",", " "))
        )
    except Exception:
        pass

    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ TASDIQLANDI") if callback.message.caption else None
    await callback.answer("✅ Tasdiqlandi")


@router.callback_query(F.data.startswith("conf_reject_"))
async def cb_topup_confirm_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔️ Ruxsat yo'q", show_alert=True)
        return
    topup_id = int(callback.data.replace("conf_reject_", ""))
    topup = await db.get_topup(topup_id)
    if not topup or topup["status"] not in ("pending_review",):
        await callback.answer("❌ Bu chek allaqachon ko'rib chiqilgan", show_alert=True)
        return

    await db.set_topup_status(topup_id, "rejected")

    user = await db.get_user(topup["user_id"])
    lang = user["language"] if user else "uz"
    block_until = int(time.time()) + BLOCK_DURATION_HOURS * 3600
    await db.set_block(topup["user_id"], block_until)

    try:
        await callback.bot.send_message(
            topup["user_id"],
            t(lang, "topup_rejected", hours=BLOCK_DURATION_HOURS)
        )
    except Exception:
        pass

    if callback.message.caption:
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ BEKOR QILINDI")
    await callback.answer("❌ Bekor qilindi, mijoz bloklandi")
