# -*- coding: utf-8 -*-
import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import db
from texts import t
from states import ServiceOrder
from keyboards.common import back_kb
from keyboards.services import (
    services_root_kb, service_types_kb, services_list_kb,
    game_donat_kb, pubg_uc_kb,
)
from utils import smm_api
from utils.service_classifier import classify_services, NETWORK_KEYWORDS
from utils.order_channel import post_new_order
from config import PUBG_UC_PRICES

router = Router()

NETWORK_TITLES = {"telegram": "Telegram", "instagram": "Instagram", "tiktok": "TikTok", "youtube": "YouTube"}

_services_cache = {"data": None, "ts": 0}


async def get_cached_services():
    import time
    if _services_cache["data"] is None or time.time() - _services_cache["ts"] > 300:
        services = await smm_api.get_services()

        # Stars/Premium/Gifts SMM panel xizmatlari emas. Ular botning
        # ichki (API'siz) Premium/Stars/Gifts bo'limlari orqali ishlaydi.
        api_smm_services = []
        blocked_terms = (
            "telegram stars", "telegram star", "stars", "star",
            "telegram premium", "premium", "telegram gift", "gift", "gifts",
            "telegram gifts", "telegram gift",
        )
        for service in services:
            blob = f"{service.get('category', '')} {service.get('name', '')}".casefold()
            # Stars / Premium / Gifts faqat botning ichki tizimidan sotiladi.
            # API panelidagi shu nomdagi xizmatlar har qanday kategoriyadan chiqarib tashlanadi.
            if any(term in blob for term in blocked_terms):
                continue
            api_smm_services.append(service)

        _services_cache["data"] = classify_services(api_smm_services)
        _services_cache["ts"] = time.time()
    return _services_cache["data"]


@router.callback_query(F.data == "menu_services")
async def cb_services_root(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_network"), reply_markup=services_root_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("svc_net_"))
async def cb_choose_network(callback: CallbackQuery, state: FSMContext):
    network = callback.data.replace("svc_net_", "")
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]

    classified = await get_cached_services()
    # Noma'lum xizmatlarni "Boshqa xizmatlar" sifatida ko'rsatmaymiz.
    # Faqat aniq tasniflangan SMM kategoriyalari chiqadi.
    types_available = [
        stype for stype in classified.get(network, {}).keys()
        if stype != "other"
    ]

    if not types_available:
        await callback.answer("⏳ Xizmatlar hozircha mavjud emas yoki yuklanmoqda.", show_alert=True)
        return

    await state.update_data(network=network)
    await state.set_state(ServiceOrder.choosing_type)
    await callback.message.edit_text(
        t(lang, "choose_service_type"),
        reply_markup=service_types_kb(lang, network, types_available),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("svc_type_"))
async def cb_choose_type(callback: CallbackQuery, state: FSMContext):
    _, _, network, stype = callback.data.split("_", 3)
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]

    classified = await get_cached_services()
    services = classified.get(network, {}).get(stype, [])
    if not services:
        await callback.answer("⏳ Xizmat topilmadi.", show_alert=True)
        return

    await state.update_data(network=network, stype=stype)
    await state.set_state(ServiceOrder.choosing_service)
    await callback.message.edit_text(
        t(lang, "choose_service"),
        reply_markup=services_list_kb(lang, network, stype, services),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("svc_pick_"))
async def cb_pick_service(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.replace("svc_pick_", ""))
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]

    classified = await get_cached_services()
    data = await state.get_data()
    network, stype = data.get("network"), data.get("stype")
    services = classified.get(network, {}).get(stype, [])
    service = next((s for s in services if s["service"] == service_id), None)
    if not service:
        await callback.answer("❌ Xizmat topilmadi.", show_alert=True)
        return

    await state.update_data(service=service)
    await state.set_state(ServiceOrder.entering_link)
    await callback.message.edit_text(t(lang, "enter_link"), reply_markup=back_kb(lang, f"svc_type_{network}_{stype}"))
    await callback.answer()


@router.message(ServiceOrder.entering_link)
async def process_link(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user["language"]
    link = message.text.strip()
    if not link:
        await message.answer(t(lang, "enter_link"))
        return

    data = await state.get_data()
    service = data["service"]
    await state.update_data(link=link)
    await state.set_state(ServiceOrder.entering_quantity)
    await message.answer(t(lang, "enter_quantity", min=service["min"], max=service["max"]))


@router.message(ServiceOrder.entering_quantity)
async def process_quantity(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user["language"]
    data = await state.get_data()
    service = data["service"]

    try:
        quantity = int(message.text.strip())
    except ValueError:
        await message.answer(t(lang, "enter_quantity", min=service["min"], max=service["max"]))
        return

    if quantity < service["min"] or quantity > service["max"]:
        await message.answer(t(lang, "enter_quantity", min=service["min"], max=service["max"]))
        return

    margin = float(await db.get_setting("smm_margin_percent", 30))
    price = smm_api.calculate_order_price(service["rate"], quantity, margin)

    await state.update_data(quantity=quantity, price=price)
    await state.set_state(ServiceOrder.confirming)

    from keyboards.common import confirm_cancel_kb
    text = t(lang, "order_summary", service=service["name"], link=data["link"],
              quantity=quantity, price=f"{price:,}".replace(",", " "))
    await message.answer(text, reply_markup=confirm_cancel_kb(lang, "svc_confirm", "svc_cancel_order"))


@router.callback_query(F.data == "svc_cancel_order")
async def cb_cancel_order(callback: CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await state.clear()
    await callback.message.edit_text(t(lang, "cancelled"))
    await callback.answer()


@router.callback_query(F.data == "svc_confirm")
async def cb_confirm_order(callback: CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    data = await state.get_data()
    service, link, quantity, price = data["service"], data["link"], data["quantity"], data["price"]

    if user["balance"] < price:
        await callback.message.edit_text(t(lang, "not_enough_balance"))
        await state.clear()
        await callback.answer()
        return

    result = await smm_api.add_order(service["service"], link, quantity)
    if "error" in result or "order" not in result:
        await callback.message.edit_text(t(lang, "order_failed", error=result.get("error", "noma'lum")))
        await state.clear()
        await callback.answer()
        return

    await db.update_balance(user["user_id"], -price)
    order_id = await db.create_order(
        user["user_id"], "smm", service["name"], f"{quantity} dona", price,
        status="processing", external_id=str(result["order"]),
        extra=json.dumps({"link": link}),
    )

    customer_name = f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
    await post_new_order(callback.bot, order_id, customer_name, service["name"], price, f"{quantity} dona")

    await callback.message.edit_text(t(lang, "order_success", order_id=order_id))
    await state.clear()
    await callback.answer()


# -------------------- GAME DONAT (PUBG UC) --------------------

@router.callback_query(F.data == "svc_game_donat")
async def cb_game_donat(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_network"), reply_markup=game_donat_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "pubg_uc")
async def cb_pubg_uc(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text(t(lang, "choose_service"), reply_markup=pubg_uc_kb(lang, PUBG_UC_PRICES))
    await callback.answer()


@router.callback_query(F.data.startswith("pubg_pick_"))
async def cb_pubg_pick(callback: CallbackQuery, state: FSMContext):
    uc = int(callback.data.replace("pubg_pick_", ""))
    price = PUBG_UC_PRICES.get(uc)
    if price is None:
        await callback.answer("❌ Xatolik", show_alert=True)
        return
    from states import UsernameOrder
    await state.update_data(order_kind="pubg", title=f"PUBG UC {uc}", amount=f"{uc} UC", price=price)
    await state.set_state(UsernameOrder.entering_username)
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    await callback.message.edit_text("🎮 PUBG Player ID'ingizni yuboring:")
    await callback.answer()
