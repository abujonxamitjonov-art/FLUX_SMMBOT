# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import t


def topup_methods_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_card_uzcard"), callback_data="topup_uzcard")],
        [InlineKeyboardButton(text=t(lang, "btn_card_foreign"), callback_data="topup_foreign")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="back_main_menu")],
    ])


def cancel_topup_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="topup_cancel")],
    ])


def admin_topup_review_kb(topup_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"topup_approve_{topup_id}"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"topup_reject_{topup_id}")],
    ])


def admin_confirm_kb(action: str, ref_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha", callback_data=f"conf_{action}_{ref_id}"),
         InlineKeyboardButton(text="❌ Yo'q", callback_data=f"back_{action}_{ref_id}")],
    ])
