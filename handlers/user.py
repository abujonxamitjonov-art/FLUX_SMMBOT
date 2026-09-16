# -*- coding: utf-8 -*-
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database import db
from texts import t
from states import Registration
from keyboards.common import (
    language_kb, contact_kb, subscribe_kb, main_menu_kb, back_kb,
)
from config import ADMIN_ID

router = Router()


async def check_subscriptions(bot: Bot, user_id: int) -> bool:
    channels = await db.get_mandatory_channels()
    if not channels:
        return True
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["chat_id"], user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            continue  # bot admin bo'lmasa yoki xatolik bo'lsa o'tkazib yuboramiz
    return True


async def show_main_menu(message_or_cb, lang: str, edit: bool = False):
    """Asosiy Reply Keyboard'ni yuboradi. Inline xabarni tahrirlashga urinmaydi."""
    text = t(lang, "main_menu")
    kb = main_menu_kb(lang)
    target = message_or_cb.message if isinstance(message_or_cb, CallbackQuery) else message_or_cb
    await target.answer(text, reply_markup=kb)
    await db.mark_main_menu_keyboard_sent(target.chat.id, 3)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    user_id = message.from_user.id

    if await db.is_currently_blocked(user_id):
        user = await db.get_user(user_id)
        lang = user["language"] if user else "uz"
        await message.answer(t(lang, "blocked"))
        return

    referrer_id = None
    if command.args and command.args.startswith("ref_"):
        ref_code = command.args.replace("ref_", "")
        ref_user = await db.get_user_by_referral_code(ref_code)
        if ref_user and ref_user["user_id"] != user_id:
            referrer_id = ref_user["user_id"]

    user = await db.get_user(user_id)
    if user is None:
        await db.create_user_if_not_exists(
            user_id, message.from_user.username or "", message.from_user.full_name, referrer_id
        )
        await state.set_state(Registration.choosing_language)
        await message.answer(t("uz", "choose_language"), reply_markup=language_kb())
        return

    if not user["language"] or user["registered"] == 0:
        if not user["language"]:
            await state.set_state(Registration.choosing_language)
            await message.answer(t("uz", "choose_language"), reply_markup=language_kb())
            return
        lang = user["language"]
        await state.set_state(Registration.waiting_contact)
        await message.answer(t(lang, "share_contact"), reply_markup=contact_kb(lang))
        return

    lang = user["language"]
    if not await check_subscriptions(message.bot, user_id):
        channels = await db.get_mandatory_channels()
        await message.answer(t(lang, "subscribe_required"), reply_markup=subscribe_kb(channels, lang))
        return

    await state.clear()
    # Reply Keyboard yangi versiyada bir marta yangilanadi.
    # Eski foydalanuvchilarda version=2 bo‘lsa, /start orqali keyboard 3-versiyaga yangilanadi.
    # Keyingi /start bosishlarda yangi menyu xabari yuborilmaydi.
    if int(user.get("main_menu_keyboard_version") or 0) < 3:
        await show_main_menu(message, lang)
    return


MAIN_MENU_BUTTON_TEXTS = {
    t("uz", "btn_number"), t("uz", "btn_services"), t("uz", "btn_my_orders"),
    t("uz", "btn_balance"), t("uz", "btn_referral"), t("uz", "btn_topup"),
    t("uz", "btn_guide"), t("uz", "btn_support"),
    t("ru", "btn_number"), t("ru", "btn_services"), t("ru", "btn_my_orders"),
    t("ru", "btn_balance"), t("ru", "btn_referral"), t("ru", "btn_topup"),
    t("ru", "btn_guide"), t("ru", "btn_support"),
}


@router.message(F.text.in_(MAIN_MENU_BUTTON_TEXTS))
async def main_menu_text_buttons(message: Message, state: FSMContext):
    """Doimiy Reply Keyboard tugmalarini tegishli bo'limlarga ulaydi."""
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("language") or user.get("registered") == 0:
        return

    lang = user["language"]
    text = message.text

    if text == t(lang, "btn_services"):
        await state.clear()
        from keyboards.services import services_root_kb
        await message.answer(t(lang, "choose_network"), reply_markup=services_root_kb(lang))
        return

    if text == t(lang, "btn_number"):
        await state.clear()
        from keyboards.numbers import countries_kb
        from handlers.numbers import get_cached_countries
        countries = await get_cached_countries()
        if not countries:
            await message.answer("Hozircha davlatlar mavjud emas.")
            return
        await message.answer(t(lang, "choose_country"), reply_markup=countries_kb(lang, countries))
        return

    if text == t(lang, "btn_balance"):
        balance = f"{user['balance']:,}".replace(",", " ")
        await message.answer(
            t(lang, "balance_info", user_id=user["user_id"], balance=balance),
            reply_markup=back_kb(lang, "back_main_menu"),
        )
        return

    if text == t(lang, "btn_my_orders"):
        await state.clear()
        orders = await db.get_user_orders(message.from_user.id, limit=15)
        if not orders:
            await message.answer(t(lang, "no_orders"), reply_markup=back_kb(lang, "back_main_menu"))
            return
        status_text = {
            "pending": "Kutilmoqda", "processing": "Jarayonda",
            "completed": "Bajarildi", "cancelled": "Bekor qilingan",
        }
        lines = [t(lang, "orders_list_title"), ""]
        for o in orders:
            lines.append(
                f"#{o['order_id']} — {o['title']} — {o['amount']} — "
                f"{o['price']:,} so'm — {status_text.get(o['status'], o['status'])}".replace(",", " ")
            )
        await message.answer("\n".join(lines), reply_markup=back_kb(lang, "back_main_menu"))
        return

    if text == t(lang, "btn_referral"):
        await state.clear()
        from config import REFERRAL_SIGNUP_BONUS, REFERRAL_FIRST_PAYMENT_BONUS
        bot_info = await message.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start=ref_{user['referral_code']}"
        count = await db.count_referrals(user["user_id"])
        await message.answer(
            t(lang, "referral_info", link=link, count=count,
              signup_bonus=REFERRAL_SIGNUP_BONUS, first_payment_bonus=REFERRAL_FIRST_PAYMENT_BONUS),
            reply_markup=back_kb(lang, "back_main_menu"),
        )
        return

    if text == t(lang, "btn_topup"):
        await state.clear()
        from keyboards.topup import topup_methods_kb
        from states import TopUp
        await state.set_state(TopUp.choosing_method)
        await message.answer(t(lang, "choose_topup_method"), reply_markup=topup_methods_kb(lang))
        return

    if text == t(lang, "btn_guide"):
        await state.clear()
        await message.answer(t(lang, "guide_text"), reply_markup=back_kb(lang, "back_main_menu"))
        return

    if text == t(lang, "btn_support"):
        await state.clear()
        from config import ADMIN_USERNAME
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "contact_admin_btn"), url=f"https://t.me/{ADMIN_USERNAME}")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="back_main_menu")],
        ])
        await message.answer(t(lang, "support_text"), reply_markup=kb)
        return


@router.callback_query(F.data.startswith("lang_"))
async def cb_choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await db.set_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(t(lang, "language_set"))
    await state.set_state(Registration.waiting_contact)
    await callback.message.answer(t(lang, "share_contact"), reply_markup=contact_kb(lang))
    await callback.answer()


@router.message(Registration.waiting_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.contact.user_id != user_id:
        user = await db.get_user(user_id)
        lang = user["language"] if user else "uz"
        await message.answer(t(lang, "contact_wrong"))
        return

    await db.set_user_phone_and_register(user_id, message.contact.phone_number)
    user = await db.get_user(user_id)
    lang = user["language"]

    await message.answer(t(lang, "registered"))
    await state.clear()

    if not await check_subscriptions(message.bot, user_id):
        channels = await db.get_mandatory_channels()
        await message.answer(t(lang, "subscribe_required"), reply_markup=subscribe_kb(channels, lang))
        return

    await show_main_menu(message, lang)


@router.message(Registration.waiting_contact)
async def process_contact_wrong(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "uz"
    await message.answer(t(lang, "contact_wrong"))


@router.callback_query(F.data == "check_subs")
async def cb_check_subs(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"
    if await check_subscriptions(callback.bot, callback.from_user.id):
        await callback.message.delete()
        await show_main_menu(callback, lang)
    else:
        await callback.answer(t(lang, "subscribe_not_done"), show_alert=True)


@router.callback_query(F.data == "back_main_menu")
async def cb_back_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"
    await show_main_menu(callback, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data == "menu_balance")
async def cb_balance(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    text = t(lang, "balance_info", user_id=user["user_id"], balance=f"{user['balance']:,}".replace(",", " "))
    from keyboards.common import back_kb
    await callback.message.edit_text(text, reply_markup=back_kb(lang, "back_main_menu"))
    await callback.answer()


@router.callback_query(F.data == "menu_guide")
async def cb_guide(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    from keyboards.common import back_kb
    await callback.message.edit_text(t(lang, "guide_text"), reply_markup=back_kb(lang, "back_main_menu"))
    await callback.answer()


@router.callback_query(F.data == "menu_support")
async def cb_support(callback: CallbackQuery):
    from config import ADMIN_USERNAME
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    user = await db.get_user(callback.from_user.id)
    lang = user["language"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "contact_admin_btn"), url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="back_main_menu")],
    ])
    await callback.message.edit_text(t(lang, "support_text"), reply_markup=kb)
    await callback.answer()
