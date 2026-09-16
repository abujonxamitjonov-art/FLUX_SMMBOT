# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import t
import re


def _clean_country_name(name: str) -> str:
    # API ba'zan nom boshiga globe/flag emoji qo'shadi. Tugmada faqat nom qolsin.
    name = str(name or "").strip()
    name = re.sub(r"^[\W_]*🌍\s*", "", name, flags=re.UNICODE)
    name = re.sub(r"^[\U0001F1E6-\U0001F1FF]{2}\s*", "", name)
    return name.strip()


def countries_kb(lang: str, countries: list) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for c in countries[:60]:
        row.append(InlineKeyboardButton(
            text=f"{_clean_country_name(c['name'])} — {c['price']:,} so'm".replace(",", " "),
            callback_data=f"num_country_{c['code']}"
        ))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="back_main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_sms_kb(lang: str, order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "get_sms_btn"), callback_data=f"num_getsms_{order_id}")],
    ])
