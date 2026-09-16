# -*- coding: utf-8 -*-
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from states import AdminBroadcast, AdminMargin, AdminMandatoryChannel
from config import ADMIN_ID

router = Router()


def admin_only(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


ADMIN_HELP = (
    "👑 <b>Admin buyruqlari</b>\n\n"
    "/stats — Statistika\n"
    "/broadcast — Barcha foydalanuvchilarga xabar yuborish\n"
    "/add_channel — Majburiy obuna kanali/guruh qo'shish\n"
    "/list_channels — Majburiy kanallar ro'yxati\n"
    "/remove_channel — Majburiy kanalni o'chirish\n"
    "/set_smm_margin — SMM xizmatlar foydasini o'zgartirish (%)\n"
    "/set_number_margin — Nomer olish foydasini o'zgartirish (%)\n"
    "/user &lt;id&gt; — Foydalanuvchi haqida ma'lumot\n"
)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not admin_only(message):
        return
    await message.answer(ADMIN_HELP, parse_mode="HTML")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not admin_only(message):
        return
    total = await db.count_users()
    registered = await db.count_registered_users()
    smm_margin = await db.get_setting("smm_margin_percent")
    number_margin = await db.get_setting("number_margin_percent")
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: {total}\n"
        f"✅ Ro'yxatdan o'tganlar: {registered}\n"
        f"💹 SMM margin: {smm_margin}%\n"
        f"💹 Nomer olish margin: {number_margin}%",
        parse_mode="HTML",
    )


@router.message(Command("user"))
async def cmd_user_info(message: Message):
    if not admin_only(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /user <telegram_id>")
        return
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Noto'g'ri ID")
        return
    user = await db.get_user(user_id)
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi")
        return
    orders = await db.get_user_orders(user_id, limit=5)
    orders_text = "\n".join(f"  #{o['order_id']} — {o['title']} — {o['status']}" for o in orders) or "  yo'q"
    blocked_label = "ha" if user["is_blocked"] else "yo'q"
    await message.answer(
        f"👤 <b>Foydalanuvchi ma'lumoti</b>\n\n"
        f"🆔 ID: {user['user_id']}\n"
        f"📛 Ism: {user['full_name']}\n"
        f"📞 Telefon: {user['phone']}\n"
        f"🌐 Til: {user['language']}\n"
        f"💰 Balans: {user['balance']:,} so'm\n"
        f"⛔️ Bloklangan: {blocked_label}\n\n"
        f"📦 So'nggi buyurtmalar:\n{orders_text}".replace(",", " "),
        parse_mode="HTML",
    )


# -------------------- BROADCAST --------------------

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.set_state(AdminBroadcast.waiting_message)
    await message.answer("✉️ Barcha foydalanuvchilarga yuborish uchun xabaringizni yuboring:")


@router.message(AdminBroadcast.waiting_message)
async def process_broadcast(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.clear()
    user_ids = await db.get_all_user_ids()
    sent, failed = 0, 0
    status_msg = await message.answer(f"⏳ Yuborilmoqda... (0/{len(user_ids)})")
    for i, uid in enumerate(user_ids):
        try:
            await message.copy_to(uid)
            sent += 1
        except Exception:
            failed += 1
        if i % 30 == 0:
            try:
                await status_msg.edit_text(f"⏳ Yuborilmoqda... ({i}/{len(user_ids)})")
            except Exception:
                pass
    await status_msg.edit_text(f"✅ Yakunlandi.\n✅ Yuborildi: {sent}\n❌ Xatolik: {failed}")


# -------------------- MAJBURIY OBUNA --------------------

@router.message(Command("add_channel"))
async def cmd_add_channel(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.set_state(AdminMandatoryChannel.waiting_channel_id)
    await message.answer(
        "📢 Kanal/guruh username yoki ID'sini yuboring (masalan @kanal yoki -1001234567890).\n"
        "Bot o'sha kanalda admin bo'lishi shart."
    )


@router.message(AdminMandatoryChannel.waiting_channel_id)
async def process_add_channel(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    chat_id = message.text.strip()
    await state.clear()
    try:
        chat = await message.bot.get_chat(chat_id)
        title = chat.title or chat_id
        ctype = "group" if chat.type in ("group", "supergroup") else "channel"
    except Exception:
        title = chat_id
        ctype = "channel"
    await db.add_mandatory_channel(chat_id, title, ctype)
    await message.answer(f"✅ Qo'shildi: {title} ({chat_id})")


@router.message(Command("list_channels"))
async def cmd_list_channels(message: Message):
    if not admin_only(message):
        return
    channels = await db.get_mandatory_channels()
    if not channels:
        await message.answer("📭 Majburiy kanallar yo'q.")
        return
    lines = [f"• {c['title']} ({c['chat_id']}) — {c['type']}" for c in channels]
    await message.answer("📢 Majburiy kanallar:\n\n" + "\n".join(lines))


@router.message(Command("remove_channel"))
async def cmd_remove_channel(message: Message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Foydalanish: /remove_channel <chat_id>")
        return
    await db.remove_mandatory_channel(parts[1].strip())
    await message.answer("✅ O'chirildi.")


# -------------------- MARGIN --------------------

@router.message(Command("set_smm_margin"))
async def cmd_set_smm_margin(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.set_state(AdminMargin.waiting_smm_margin)
    current = await db.get_setting("smm_margin_percent")
    await message.answer(f"💹 Joriy SMM margin: {current}%\n\nYangi foizni kiriting:")


@router.message(AdminMargin.waiting_smm_margin)
async def process_smm_margin(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri qiymat. Raqam kiriting:")
        return
    await db.set_setting("smm_margin_percent", str(value))
    await state.clear()
    await message.answer(f"✅ SMM margin {value}% qilib o'rnatildi.")


@router.message(Command("set_number_margin"))
async def cmd_set_number_margin(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.set_state(AdminMargin.waiting_number_margin)
    current = await db.get_setting("number_margin_percent")
    await message.answer(f"💹 Joriy Nomer olish margin: {current}%\n\nYangi foizni kiriting:")


@router.message(AdminMargin.waiting_number_margin)
async def process_number_margin(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri qiymat. Raqam kiriting:")
        return
    await db.set_setting("number_margin_percent", str(value))
    await state.clear()
    await message.answer(f"✅ Nomer olish margin {value}% qilib o'rnatildi.")
