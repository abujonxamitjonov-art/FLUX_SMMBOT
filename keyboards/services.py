# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.service_classifier import SERVICE_TYPES
from texts import t


NETWORK_LABELS = {
    "telegram": ("📱", "Telegram"),
    "instagram": ("📷", "Instagram"),
    "tiktok": ("🎵", "TikTok"),
    "youtube": ("▶️", "YouTube"),
}


def services_root_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="Telegram", callback_data="svc_net_telegram"),
         InlineKeyboardButton(text="Instagram", callback_data="svc_net_instagram")],
        [InlineKeyboardButton(text="TikTok", callback_data="svc_net_tiktok"),
         InlineKeyboardButton(text="YouTube", callback_data="svc_net_youtube")],
        [InlineKeyboardButton(text="Stars | Premium", callback_data="svc_stars_premium")],
        [InlineKeyboardButton(text="Telegram Gifts", callback_data="svc_gifts")],
        [InlineKeyboardButton(text="Game Donat", callback_data="svc_game_donat")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="back_main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def service_types_kb(lang: str, network: str, available_types: list) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for stype in available_types:
        label = SERVICE_TYPES[stype]["name_uz"] if lang == "uz" else SERVICE_TYPES[stype]["name_ru"]
        row.append(InlineKeyboardButton(text=label, callback_data=f"svc_type_{network}_{stype}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_services")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def services_list_kb(lang: str, network: str, stype: str, services: list) -> InlineKeyboardMarkup:
    rows = []
    for s in services[:40]:  # juda uzun bo'lmasligi uchun cheklov
        rows.append([InlineKeyboardButton(
            text=f"{s['name']} — {s['rate']} so'm/1000",
            callback_data=f"svc_pick_{s['service']}"
        )])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=f"svc_net_{network}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def game_donat_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 PUBG UC", callback_data="pubg_uc")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_services")],
    ])


def pubg_uc_kb(lang: str, prices: dict) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for uc, price in prices.items():
        row.append(InlineKeyboardButton(text=f"{uc} UC — {price:,} so'm".replace(",", " "),
                                         callback_data=f"pubg_pick_{uc}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="svc_game_donat")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def stars_premium_root_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Stars Olish", callback_data="sp_stars")],
        [InlineKeyboardButton(text="⭐ Premium Olish", callback_data="sp_premium")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_services")],
    ])


def stars_amounts_kb(lang: str, prices: dict) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for amount, price in prices.items():
        row.append(InlineKeyboardButton(text=f"{amount} Stars — {price:,} so'm".replace(",", " "),
                                         callback_data=f"stars_pick_{amount}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="sp_root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def premium_durations_kb(lang: str, prices: dict) -> InlineKeyboardMarkup:
    rows = []
    for months, price in prices.items():
        rows.append([InlineKeyboardButton(
            text=f"Premium {months} oy — {price:,} so'm".replace(",", " "),
            callback_data=f"premium_pick_{months}"
        )])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="sp_root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def gift_groups_kb(lang: str, groups: dict) -> InlineKeyboardMarkup:
    rows = []
    for group_id, data in groups.items():
        rows.append([InlineKeyboardButton(
            text=f"Gifts ({group_id} talik) — {data['price']:,} so'm".replace(",", " "),
            callback_data=f"gift_group_{group_id}"
        )])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_services")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def gift_items_kb(lang: str, group_id: str, gifts: dict) -> InlineKeyboardMarkup:
    rows = []
    for gift_key, gift_data in gifts.items():
        rows.append([InlineKeyboardButton(
            text=f"{gift_data['emoji']} {gift_data['name']}",
            callback_data=f"gift_pick_{group_id}_{gift_key}"
        )])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="svc_gifts")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
