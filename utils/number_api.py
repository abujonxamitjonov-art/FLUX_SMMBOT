# -*- coding: utf-8 -*-
"""Nomer olish API (https://locksmm.uz) bilan ishlash."""
import aiohttp
from config import NUMBER_API_URL, NUMBER_API_KEY


async def _request(params: dict) -> dict:
    params = {**params, "key": NUMBER_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.post(NUMBER_API_URL, data=params, timeout=aiohttp.ClientTimeout(total=40)) as resp:
            try:
                return await resp.json(content_type=None)
            except Exception:
                text = await resp.text()
                return {"error": f"Noto'g'ri javob: {text[:200]}"}


async def get_balance() -> dict:
    return await _request({"action": "balance"})


async def get_countries() -> list:
    """Davlatlar va narxlar ro'yxati."""
    result = await _request({"action": "countries"})
    if isinstance(result, dict) and "countries" in result:
        return result["countries"]
    return []


async def buy_number(country_code: str) -> dict:
    """Tanlangan davlatdan raqam sotib olish. {phone, hash, price, ...} yoki {error}."""
    return await _request({"action": "getnum", "code": country_code})


async def get_sms(phone_hash: str) -> dict:
    """SMS kodni olish. {sms, password, phone} yoki {error}."""
    return await _request({"action": "getsms", "hash": phone_hash})


def apply_margin(price: float, margin_percent: float) -> int:
    return max(1, round(price * (1 + margin_percent / 100)))
