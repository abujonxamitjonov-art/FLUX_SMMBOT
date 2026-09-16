# -*- coding: utf-8 -*-
"""
LOCK SMM BOT - Konfiguratsiya fayli
Barcha sozlamalar, narxlar, API kalitlar shu yerda saqlanadi.
"""
import os

# ============================================================
# BOT TOKEN - Render Environment Variables orqali beriladi
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ============================================================
# ADMIN
# ============================================================
ADMIN_ID = 8735103455  # Yagona admin
ADMIN_USERNAME = "Xamidov_xalal"  # Premium 1 oylik va Qo'llab-quvvatlash uchun

# ============================================================
# KANALLAR
# ============================================================
ORDERS_CHANNEL = "@FLUX_buyurtmalar"  # Buyurtmalar kanali (bot admin bo'lishi kerak)

# ============================================================
# SMM PANEL API (Telegram/Instagram/TikTok/YouTube xizmatlari)
# ============================================================
SMM_API_URL = "https://locksmm.com/api/v2"
SMM_API_KEY = "5deb4e020007944fc0e1164af1d4390e"

# Admin foydasi (foiz) - SMM xizmatlari narxiga qo'shiladi
# /set_margin buyrug'i orqali admin buni o'zgartira oladi (database'da saqlanadi)
DEFAULT_SMM_MARGIN_PERCENT = 30  # boshlang'ich qiymat, keyin DB'dan o'qiladi

# ============================================================
# NOMER OLISH API
# ============================================================
NUMBER_API_URL = "https://locksmm.uz"
NUMBER_API_KEY = "5deb4e020007944fc0e1164af1d4390e"
# Nomer olish narxiga ham xuddi shunday margin qo'llanadi (dinamik, DB'da saqlanadi)
DEFAULT_NUMBER_MARGIN_PERCENT = 20

# ============================================================
# TO'LOV KARTALARI
# ============================================================
CARD_OWNER = "Xamitjonov Abdulxamid"

HUMO_CARD = "9860 0966 0130 8230"
VISA_CARD = "4685 9701 3412 1589"
MASTERCARD_CARD = "5130 2500 0321 6960"

MIN_TOPUP_AMOUNT = 2000  # so'm
PAYMENT_TIMEOUT_MINUTES = 5  # to'lov uchun berilgan vaqt
BLOCK_DURATION_HOURS = 24  # soxta chek uchun blok muddati

# ============================================================
# REFERAL TIZIMI
# ============================================================
REFERRAL_SIGNUP_BONUS = 150  # do'st ro'yxatdan o'tganda
REFERRAL_FIRST_PAYMENT_BONUS = 500  # do'st birinchi to'lov qilganda

# ============================================================
# TELEGRAM PREMIUM NARXLARI (so'm)
# ============================================================
PREMIUM_PRICES = {
    "1": 48_000,
    "3": 175_000,
    "6": 230_000,
    "12": 389_000,
}

# ============================================================
# TELEGRAM STARS NARXLARI (so'm)
# ============================================================
STARS_PRICES = {
    50: 14_000,
    100: 26_000,
    150: 39_000,
    200: 50_000,
    250: 62_000,
    300: 75_000,
    350: 86_000,
    400: 98_000,
    450: 109_000,
    500: 121_000,
    600: 143_000,
    700: 168_000,
    800: 190_000,
    900: 214_000,
    1000: 239_000,
    1500: 350_000,
    2000: 472_000,
    2500: 589_000,
    3000: 692_000,
}

# ============================================================
# TELEGRAM GIFTLAR NARXLARI (so'm)
# ============================================================
# Har bir gift guruhi va o'sha guruhdagi giftlar
GIFT_GROUPS = {
    "15": {
        "price": 5_000,
        "gifts": {
            "ayiqcha": {"emoji": "🧸", "name": "Ayiqcha hadyasi"},
            "yurakcha": {"emoji": "💝", "name": "Yurakcha hadyasi"},
        },
    },
    "25": {
        "price": 9_000,
        "gifts": {
            "sovgaqutisi": {"emoji": "🎁", "name": "Sovg'a qutisi hadyasi"},
            "atirgul": {"emoji": "🌹", "name": "Atirgul hadyasi"},
        },
    },
    "50": {
        "price": 16_000,
        "gifts": {
            "tort": {"emoji": "🎂", "name": "Tort hadyasi"},
            "guldasta": {"emoji": "💐", "name": "Guldasta hadyasi"},
            "raketa": {"emoji": "🚀", "name": "Raketa hadyasi"},
        },
    },
    "100": {
        "price": 26_000,
        "gifts": {
            "kubok": {"emoji": "🏆", "name": "Kubok hadyasi"},
            "uzuk": {"emoji": "💍", "name": "Uzuk hadyasi"},
            "olmos": {"emoji": "💎", "name": "Olmos hadyasi"},
        },
    },
}

# ============================================================
# PUBG UC NARXLARI (so'm)
# ============================================================
PUBG_UC_PRICES = {
    60: 14_000,
    325: 65_000,
    660: 128_000,
    985: 191_000,
    1320: 249_990,
    1800: 319_800,
    2460: 432_000,
    3850: 623_000,
    5650: 939_000,
    8100: 1_249_000,
}

# ============================================================
# DATABASE
# ============================================================
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

# ============================================================
# TILLAR
# ============================================================
SUPPORTED_LANGUAGES = ["uz", "ru"]
DEFAULT_LANGUAGE = "uz"
