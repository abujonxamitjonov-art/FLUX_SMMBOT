# -*- coding: utf-8 -*-
"""
SMM panelidan kelgan xizmatlarni (services) tarmoq (Telegram/Instagram/TikTok/YouTube)
va xizmat turiga (Obunachilar/Reaksiyalar/Ko'rishlar va h.k.) ajratish uchun klassifikator.

Panel category/name matnida kalit so'zlarga qarab ishlaydi.
Agar avtomatik aniqlanmasa "Boshqa" toifasiga tushadi - admin buni keyinchalik
qo'lda sozlashi mumkin.
"""

NETWORKS = ["telegram", "instagram", "tiktok", "youtube"]

NETWORK_KEYWORDS = {
    "telegram": ["telegram", "tg "],
    "instagram": ["instagram", "insta", "ig "],
    "tiktok": ["tiktok", "tik tok"],
    "youtube": ["youtube", "yt "],
}

SERVICE_TYPES = {
    "subscribers": {
        "name_uz": "Oddiy Obunachilar",
        "name_ru": "👤 Обычные подписчики",
        "keywords": ["subscriber", "follower", "member", "obunachi", "подписчик"],
    },
    "views": {
        "name_uz": "Ko'rishlar (Prasmotr)",
        "name_ru": "👁 Просмотры",
        "keywords": ["view", "просмотр", "ko'rish"],
    },
    "reactions": {
        "name_uz": "Reaksiyalar",
        "name_ru": "🔥 Реакции",
        "keywords": ["like", "reaction", "лайк", "реакция", "layk"],
    },
    "shares_repost_save": {
        "name_uz": "Ulashish | Repost | Save",
        "name_ru": "📈 Поделиться | Репост | Сохранение",
        "keywords": ["share", "repost", "save", "репост", "сохран"],
    },
    "comments": {
        "name_uz": "Kommentariya | Sharxlar",
        "name_ru": "✉️ Комментарии",
        "keywords": ["comment", "коммент"],
    },
    "boost": {
        "name_uz": "Boost (Kanal/Guruhga)",
        "name_ru": "📣 Буст (Канал/Группа)",
        "keywords": ["boost", "буст"],
    },
    "bot_subscribers": {
        "name_uz": "Bot uchun (Obunachilar)",
        "name_ru": "🤖 Для бота (Подписчики)",
        "keywords": ["bot subscriber", "bot follower"],
    },
    "poll_vote": {
        "name_uz": "So'rovnomaga ovoz | Like",
        "name_ru": "📊 Голос в опросе",
        "keywords": ["poll", "vote", "опрос", "голос"],
    },
    "uzbek": {
        "name_uz": "O'zbek xizmatlar",
        "name_ru": "🇺🇿 Узбекские услуги",
        "keywords": ["uzbek", "o'zbek", "узбек"],
    },
    "history": {
        "name_uz": "Istoriya xizmatlari",
        "name_ru": "📖 Истории",
        "keywords": ["story", "stories", "истори"],
    },
    "other": {
        "name_uz": "📦 Boshqa xizmatlar",
        "name_ru": "📦 Другие услуги",
        "keywords": [],
    },
}


def detect_network(service: dict):
    text = f"{service.get('category', '')} {service.get('name', '')}".lower()
    for network, keywords in NETWORK_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return network
    return None


def detect_service_type(service: dict) -> str:
    text = f"{service.get('category', '')} {service.get('name', '')}".lower()
    priority_order = ["history", "bot_subscribers", "poll_vote", "boost",
                       "comments", "shares_repost_save", "reactions", "views",
                       "subscribers", "uzbek"]
    for type_key in priority_order:
        for kw in SERVICE_TYPES[type_key]["keywords"]:
            if kw in text:
                return type_key
    return "other"


def classify_services(services: list) -> dict:
    """Natija: { network: { service_type: [service, ...] } }"""
    result = {net: {} for net in NETWORKS}
    for s in services:
        network = detect_network(s)
        if network is None:
            continue
        stype = detect_service_type(s)
        result[network].setdefault(stype, []).append(s)
    return result
