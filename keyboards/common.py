# -*- coding: utf-8 -*-
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from texts import t


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ])


def contact_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def subscribe_kb(channels: list, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        title = ch.get("title") or ch.get("chat_id")
        chat_id = ch["chat_id"]
        url = f"https://t.me/{chat_id.lstrip('@')}" if str(chat_id).startswith("@") else None
        if url:
            rows.append([InlineKeyboardButton(text=f"📢 {title}", url=url)])
    rows.append([InlineKeyboardButton(text=t(lang, "subscribe_check_btn"), callback_data="check_subs")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    """Doimiy asosiy Reply Keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_number")), KeyboardButton(text=t(lang, "btn_services"))],
            [KeyboardButton(text=t(lang, "btn_my_orders")), KeyboardButton(text=t(lang, "btn_balance"))],
            [KeyboardButton(text=t(lang, "btn_referral")), KeyboardButton(text=t(lang, "btn_topup"))],
            [KeyboardButton(text=t(lang, "btn_guide"))],
            [KeyboardButton(text=t(lang, "btn_support"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        selective=False,
        input_field_placeholder="Kerakli bo‘limni tanlang...",
    )


def back_btn(lang: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=callback_data)


def back_kb(lang: str, callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn(lang, callback_data)]])


def confirm_cancel_kb(lang: str, confirm_cb: str, cancel_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_confirm"), callback_data=confirm_cb),
         InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data=cancel_cb)],
    ])


def yes_no_kb(lang: str, yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_yes"), callback_data=yes_cb),
         InlineKeyboardButton(text=t(lang, "btn_no"), callback_data=no_cb)],
    ])
