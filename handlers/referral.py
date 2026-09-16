# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from texts import t
from keyboards.common import back_kb
from config import REFERRAL_SIGNUP_BONUS, REFERRAL_FIRST_PAYMENT_BONUS

router = Router()


@router.callback_query(F.data == "menu_referral")
async def cb_referral(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    bot_info = await callback.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=ref_{user['referral_code']}"
    count = await db.count_referrals(user["user_id"])
    text = t(
        lang, "referral_info",
        link=link, count=count,
        signup_bonus=REFERRAL_SIGNUP_BONUS,
        first_payment_bonus=REFERRAL_FIRST_PAYMENT_BONUS,
    )
    await callback.message.edit_text(text, reply_markup=back_kb(lang, "back_main_menu"))
    await callback.answer()
