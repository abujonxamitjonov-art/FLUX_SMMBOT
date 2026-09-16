# -*- coding: utf-8 -*-
"""LockSMM panel API (https://locksmm.com/api/v2) bilan ishlash."""
import aiohttp
from config import SMM_API_URL, SMM_API_KEY


async def _request(params: dict) -> dict:
    params = {**params, "key": SMM_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.post(SMM_API_URL, data=params, timeout=aiohttp.ClientTimeout(total=40)) as resp:
            try:
                return await resp.json(content_type=None)
            except Exception:
                text = await resp.text()
                return {"error": f"Noto'g'ri javob: {text[:200]}"}


async def get_balance() -> dict:
    """Panel balansini tekshirish (bepul)."""
    return await _request({"action": "balance"})


async def get_services() -> list:
    """Barcha faol xizmatlar ro'yxati."""
    result = await _request({"action": "services"})
    if isinstance(result, list):
        return result
    return []


async def add_order(service_id: int, link: str, quantity: int) -> dict:
    """Yangi buyurtma berish. {order, charge, currency} yoki {error} qaytaradi."""
    return await _request({
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity,
    })


async def get_order_status(order_id: int) -> dict:
    """Bitta buyurtma holatini tekshirish."""
    return await _request({"action": "status", "order": order_id})


async def get_orders_status(order_ids: list) -> dict:
    """Bir nechta buyurtma holatini birdan tekshirish (100 tagacha)."""
    ids_str = ",".join(str(i) for i in order_ids)
    return await _request({"action": "status", "orders": ids_str})


async def get_orders_history(limit: int = 20, offset: int = 0) -> list:
    result = await _request({"action": "orders", "limit": limit, "offset": offset})
    if isinstance(result, list):
        return result
    return []


def apply_margin(base_price_per_1000: float, margin_percent: float) -> float:
    """Admin foydasini narxga qo'shish."""
    return base_price_per_1000 * (1 + margin_percent / 100)


def calculate_order_price(rate_per_1000: float, quantity: int, margin_percent: float) -> int:
    """Berilgan miqdor uchun yakuniy narxni hisoblash (so'mda, margin bilan)."""
    base = (rate_per_1000 / 1000) * quantity
    final = apply_margin(base, margin_percent)
    return max(1, round(final))
