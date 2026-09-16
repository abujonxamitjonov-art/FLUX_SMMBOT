# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import t
import re

def _clean_country_name(name: str) -> str:
    name = str(name or '').strip()
    name = re.sub(r"^[\W_]*🌍\s*", "", name, flags=re.UNICODE)
    name = re.sub(r"^[\U0001F1E6-\U0001F1FF]{2}\s*", "", name)
    return name.strip()

def countries_kb(lang: str, countries: list, page: int = 0, per_page: int = 60) -> InlineKeyboardMarkup:
    rows=[]
    start=page*per_page; page_items=countries[start:start+per_page]
    row=[]
    for c in page_items:
        row.append(InlineKeyboardButton(text=f"{_clean_country_name(c['name'])} — {int(c['price']):,} so'm".replace(',', ' '), callback_data=f"num_country_{c['key']}"))
        if len(row)==2: rows.append(row); row=[]
    if row: rows.append(row)
    nav=[]
    if page>0: nav.append(InlineKeyboardButton(text='⬅️ Oldingi', callback_data=f'num_page_{page-1}'))
    if start+per_page<len(countries): nav.append(InlineKeyboardButton(text='Keyingi ➡️', callback_data=f'num_page_{page+1}'))
    if nav: rows.append(nav)
    rows.append([InlineKeyboardButton(text=t(lang,'btn_back'), callback_data='back_main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def manual_numbers_kb(lang: str, numbers: list, country_id: int, page: int = 0, per_page: int = 20, api_code: str | None = None) -> InlineKeyboardMarkup:
    rows=[]; start=page*per_page
    for n in numbers[start:start+per_page]:
        rows.append([InlineKeyboardButton(text=n['phone'], callback_data=f"num_manual_{n['id']}")])
    nav=[]
    if page>0: nav.append(InlineKeyboardButton(text='⬅️ Oldingi', callback_data=f'num_manual_page_{country_id}_{page-1}'))
    if start+per_page<len(numbers): nav.append(InlineKeyboardButton(text='Keyingi ➡️', callback_data=f'num_manual_page_{country_id}_{page+1}'))
    if nav: rows.append(nav)
    if api_code:
        rows.append([InlineKeyboardButton(text='API nomer olish', callback_data=f'num_api_buy_{api_code}')])
    rows.append([InlineKeyboardButton(text=t(lang,'btn_back'), callback_data='menu_number')])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_sms_kb(lang: str, order_id: int, manual: bool=False) -> InlineKeyboardMarkup:
    rows=[]
    if manual:
        rows.append([InlineKeyboardButton(text='📩 Kod yuborish', callback_data=f'num_getsms_{order_id}')])
    else:
        rows.append([InlineKeyboardButton(text=t(lang, 'get_sms_btn'), callback_data=f'num_getsms_{order_id}')])
    return InlineKeyboardMarkup(inline_keyboard=rows)
