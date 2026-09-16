# -*- coding: utf-8 -*-
import json
import time
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from texts import t
from keyboards.numbers import countries_kb, get_sms_kb
from utils import number_api

router = Router()

_countries_cache = {"data": None, "ts": 0}


async def get_cached_countries():
    if _countries_cache["data"] is None or time.time() - _countries_cache["ts"] > 300:
        margin = float(await db.get_setting("number_margin_percent", 20))
        countries = await number_api.get_countries()
        for c in countries:
            c["price"] = number_api.apply_margin(c["price"], margin)
        _countries_cache["data"] = countries
        _countries_cache["ts"] = time.time()
    return _countries_cache["data"]


@router.callback_query(F.data == "menu_number")
async def cb_menu_number(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    countries = await get_cached_countries()
    if not countries:
        await callback.answer("⏳ Hozircha davlatlar mavjud emas.", show_alert=True)
        return
    await callback.message.edit_text(t(lang, "choose_country"), reply_markup=countries_kb(lang, countries))
    await callback.answer()


@router.callback_query(F.data.startswith("num_country_"))
async def cb_pick_country(callback: CallbackQuery):
    code = callback.data.replace("num_country_", "")
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    countries = await get_cached_countries()
    country = next((c for c in countries if c["code"] == code), None)
    if not country:
        await callback.answer("❌ Topilmadi", show_alert=True)
        return

    price = round(country["price"])
    if user["balance"] < price:
        await callback.message.edit_text(t(lang, "not_enough_balance"))
        await callback.answer()
        return

    result = await number_api.buy_number(code)
    if "error" in result or "phone" not in result:
        await callback.answer(f"❌ {result.get('error', 'Xatolik')}", show_alert=True)
        return

    await db.update_balance(user["user_id"], -price)
    order_id = await db.create_order(
        user["user_id"], "number", f"Nomer olish - {country['name']}", result["phone"], price,
        status="completed", external_id=result["hash"], extra=json.dumps({"phone": result["phone"]}),
    )

    from utils.order_channel import post_new_order
    customer_name = f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
    await post_new_order(callback.bot, order_id, customer_name, f"Nomer - {country['name']}", price)

    await callback.message.edit_text(
        t(lang, "number_given", phone=result["phone"]),
        reply_markup=get_sms_kb(lang, order_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("num_getsms_"))
async def cb_get_sms(callback: CallbackQuery):
    order_id = int(callback.data.replace("num_getsms_", ""))
    order = await db.get_order(order_id)
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    if not order or order["user_id"] != callback.from_user.id:
        await callback.answer("❌ Xatolik", show_alert=True)
        return

    result = await number_api.get_sms(order["external_id"])
    if "error" in result or not result.get("sms"):
        await callback.answer(t(lang, "sms_not_yet"), show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(t(lang, "sms_received", code=result["sms"]))
