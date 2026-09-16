# -*- coding: utf-8 -*-
"""Barcha matnlar UZ va RU tillarida."""

TEXTS = {
    "uz": {
        "choose_language": "🌐 Tilni tanlang:",
        "language_set": "✅ Til o'zbekcha qilib o'rnatildi.",
        "share_contact": (
            "📱 Ro'yxatdan o'tish uchun raqamingizni yuboring.\n\n"
            "⚠️ Pastdagi tugma orqali yuboring, qo'lda yozib bo'lmaydi."
        ),
        "share_contact_btn": "📱 Raqamni yuborish",
        "contact_wrong": "❗️ Iltimos, faqat pastdagi tugma orqali raqamingizni yuboring.",
        "registered": "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!",
        "subscribe_required": "⚠️ Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:",
        "subscribe_check_btn": "✅ Tekshirish",
        "subscribe_not_done": "❗️ Siz hali barcha kanallarga a'zo bo'lmadingiz.",
        "main_menu": "🏠 Asosiy menyu. Kerakli bo'limni tanlang:",
        "blocked": "⛔️ Siz vaqtinchalik bloklangansiz. Iltimos keyinroq urinib ko'ring.",
        # Asosiy menyu
        "btn_number": "Nomer olish",
        "btn_services": "Xizmatlar",
        "btn_my_orders": "Buyurtmalarim",
        "btn_balance": "Hisobim",
        "btn_referral": "Referal bonus",
        "btn_topup": "Hisob to'ldirish",
        "btn_guide": "Qo'llanma",
        "btn_support": "Qo'llab-quvvatlash",
        "btn_back": "🔙 Orqaga",
        "btn_cancel": "❌ Bekor qilish",
        "btn_confirm": "✅ Tasdiqlash",
        "btn_yes": "✅ Ha",
        "btn_no": "❌ Yo'q",
        # Xizmatlar
        "choose_network": "📡 Kerakli tarmoqni tanlang:",
        "choose_service_type": "🗂 Kerakli xizmat turini tanlang:",
        "choose_service": "🛒 Kerakli xizmatni tanlang:",
        "enter_link": "🔗 Havolani (link) yuboring:",
        "enter_quantity": "🔢 Kerakli miqdorni kiriting (min: {min}, max: {max}):",
        "order_summary": (
            "🧾 Buyurtma ma'lumotlari:\n\n"
            "🛍 Xizmat: {service}\n"
            "🔗 Havola: {link}\n"
            "🔢 Miqdor: {quantity}\n"
            "💰 Narx: {price} so'm\n\n"
            "Tasdiqlaysizmi?"
        ),
        "not_enough_balance": "❌ Hisobingizda yetarli mablag' yo'q. Iltimos hisobingizni to'ldiring.",
        "order_success": "✅ Buyurtmangiz muvaffaqiyatli qabul qilindi!\n📦 Buyurtma raqami: #{order_id}",
        "order_failed": "❌ Buyurtma yaratishda xatolik: {error}",
        # Nomer olish
        "choose_country": "🌍 Davlatni tanlang:",
        "number_price_confirm": "📱 {country} — narxi: {price} so'm.\n\nSotib olishni tasdiqlaysizmi?",
        "number_given": "📞 Raqamingiz: `{phone}`\n\nSMS kodni olish uchun pastdagi tugmani bosing.",
        "get_sms_btn": "📩 SMS kodni olish",
        "sms_not_yet": "⏳ SMS hali kelmadi, biroz kutib qayta urinib ko'ring.",
        "sms_received": "✅ SMS kod: `{code}`",
        # Stars/Premium/Gift
        "choose_stars_amount": "⭐ Kerakli Stars miqdorini tanlang:",
        "choose_premium_duration": "⭐ Premium muddatini tanlang:",
        "choose_gift_group": "🎁 Gift toifasini tanlang:",
        "choose_gift": "🎁 Kerakli hadyani tanlang:",
        "enter_username": "👤 Yuborish kerak bo'lgan akkaunt username'ini yuboring (masalan: @username):",
        "confirm_order_username": (
            "🧾 Buyurtma ma'lumotlari:\n\n"
            "🛍 Xizmat: {service}\n"
            "👤 Username: {username}\n"
            "💰 Narx: {price} so'm\n\n"
            "Ma'lumotlar to'g'rimi?"
        ),
        "order_accepted_wait": "✅ Buyurtmangiz qabul qilindi. 5-15 daqiqa ichida yuboriladi.",
        "premium_1m_contact": (
            "☎️ 1 oylik Premium uchun quyidagi tugma orqali Admin bilan bog'laning.\n"
            "1 oylik obunani Admin tomonidan olasiz."
        ),
        "contact_admin_btn": "☎️ Admin bilan bog'lanish",
        "order_completed_premium": (
            "🎉 Sizga Premium olib berildi!\n\n"
            "⭐ Premium turi: {duration}\n"
            "🆔 Sizning IDingiz: {user_id}\n\n"
            "Xarid uchun tashakkur! 🙏"
        ),
        "order_completed_generic": "🎉 Buyurtmangiz bajarildi! Xarid uchun tashakkur 🙏",
        # Hisobim
        "balance_info": "💰 Hisobingiz:\n\n🆔 ID: {user_id}\n💵 Balans: {balance} so'm",
        # Hisob to'ldirish
        "choose_topup_method": "💳 To'lov usulini tanlang:",
        "btn_card_uzcard": "💳 Karta orqali to'lov",
        "btn_card_foreign": "🌍 Chet davlatdan to'lov",
        "enter_topup_amount": "💵 Hisobingizni qancha summaga to'ldirmoqchisiz? (minimal: {min} so'm)",
        "amount_too_low": "❗️ Minimal summa {min} so'm. Qaytadan kiriting:",
        "card_details_uz": (
            "💳 Humo karta orqali to'lov\n\n"
            "💳 Karta raqami: `{card}`\n"
            "👤 Karta egasi: {owner}\n"
            "💵 To'lov summasi: {amount} so'm\n\n"
            "⚠️ Belgilangan summadan kam yoki ko'p tashlamang!\n"
            "⏰ To'lovni {minutes} daqiqa ichida amalga oshirib, chekni shu yerga yuboring.\n"
            "🚫 Soxta chek yuborsangiz {block_hours} soatga bloklanasiz."
        ),
        "card_details_foreign": (
            "🌍 Chet davlatdan to'lov\n\n"
            "💳 Visa: `{visa}`\n"
            "💳 Mastercard: `{mastercard}`\n"
            "👤 Karta egasi: {owner}\n"
            "💵 To'lov summasi: {amount} so'm\n\n"
            "⚠️ Belgilangan summadan kam yoki ko'p tashlamang!\n"
            "⏰ To'lovni {minutes} daqiqa ichida amalga oshirib, chekni shu yerga yuboring.\n"
            "🚫 Soxta chek yuborsangiz {block_hours} soatga bloklanasiz."
        ),
        "send_receipt": "🧾 Endi to'lov chekini (screenshot) yuboring:",
        "receipt_received": "✅ Chekingiz qabul qilindi va admin ko'rib chiqishga yuborildi. Iltimos kuting.",
        "topup_expired": "⌛️ Vaqt tugadi. Siz belgilangan {minutes} daqiqa ichida to'lov qilmadingiz.",
        "topup_approved": "✅ To'lovingiz tasdiqlandi! Hisobingizga {amount} so'm qo'shildi.",
        "topup_rejected": (
            "❌ Siz yuborgan chek admin tomonidan soxta deb topildi.\n"
            "🚫 Siz {hours} soatga bloklandingiz."
        ),
        "unblocked_msg": "✅ Blok muddatingiz tugadi. Botdan yana foydalanishingiz mumkin.",
        # Referal
        "referral_info": (
            "🔗 Sizning referal havolangiz:\n`{link}`\n\n"
            "👥 Taklif qilingan do'stlar: {count} ta\n\n"
            "💰 Har bir ro'yxatdan o'tgan do'st uchun: {signup_bonus} so'm\n"
            "💰 Do'stingiz birinchi to'lovni qilganda: +{first_payment_bonus} so'm"
        ),
        # Qo'llanma
        "guide_text": (
            "📖 Botdan foydalanish qo'llanmasi:\n\n"
            "1️⃣ Kerakli bo'limni tanlang (Xizmatlar, Nomer olish va h.k.)\n"
            "2️⃣ Hisobingizni to'ldiring (Hisob to'ldirish bo'limi orqali)\n"
            "3️⃣ Kerakli xizmatni tanlab, buyurtma bering\n"
            "4️⃣ Buyurtmangiz holatini \"Buyurtmalarim\" bo'limida kuzatib boring\n\n"
            "❓ Savol bo'lsa, Qo'llab-quvvatlash bo'limiga murojaat qiling."
        ),
        "btn_get_api_key": "🔑 API kalit olish",
        "btn_show_api_key": "👁 API kalitni ko'rish",
        "btn_regenerate_key": "🔄 Kalitni o'zgartirish",
        "api_key_hidden": "🔑 API kalitingiz: `{masked}`\n\nTo'liq ko'rish uchun pastdagi tugmani bosing.",
        "api_key_full": "🔑 API kalitingiz:\n`{key}`\n\n(Nusxalash uchun ustiga bosing)",
        "api_key_regenerated": "✅ Yangi API kalit yaratildi:\n`{key}`",
        # Qo'llab-quvvatlash
        "support_text": "☎️ Savollaringiz bo'lsa, quyidagi tugma orqali admin bilan bog'laning:",
        # Buyurtmalarim
        "no_orders": "📭 Sizda hali buyurtmalar mavjud emas.",
        "orders_list_title": "📦 Sizning buyurtmalaringiz:",
        # Umumiy
        "error_generic": "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.",
        "cancelled": "❌ Bekor qilindi.",
        "back_to_menu": "🏠 Asosiy menyuga qaytish",
        "active_reminder": "🤖 Bot aktiv ishlayapti! Xizmatlardan foydalanish uchun /start bosing.",
        "confirm_are_you_sure": "❗️ Ishonchingiz komilmi?",
    },
    "ru": {
        "choose_language": "🌐 Выберите язык:",
        "language_set": "✅ Язык установлен на русский.",
        "share_contact": (
            "📱 Для регистрации отправьте свой номер.\n\n"
            "⚠️ Отправьте через кнопку ниже, вручную ввести нельзя."
        ),
        "share_contact_btn": "📱 Отправить номер",
        "contact_wrong": "❗️ Пожалуйста, отправьте номер только через кнопку ниже.",
        "registered": "✅ Вы успешно зарегистрированы!",
        "subscribe_required": "⚠️ Для использования бота подпишитесь на следующие каналы:",
        "subscribe_check_btn": "✅ Проверить",
        "subscribe_not_done": "❗️ Вы ещё не подписались на все каналы.",
        "main_menu": "🏠 Главное меню. Выберите нужный раздел:",
        "blocked": "⛔️ Вы временно заблокированы. Попробуйте позже.",
        "btn_number": "Получить номер",
        "btn_services": "Услуги",
        "btn_my_orders": "Мои заказы",
        "btn_balance": "Мой баланс",
        "btn_referral": "Реферальный бонус",
        "btn_topup": "Пополнить баланс",
        "btn_guide": "Инструкция",
        "btn_support": "Поддержка",
        "btn_back": "🔙 Назад",
        "btn_cancel": "❌ Отмена",
        "btn_confirm": "✅ Подтвердить",
        "btn_yes": "✅ Да",
        "btn_no": "❌ Нет",
        "choose_network": "📡 Выберите нужную платформу:",
        "choose_service_type": "🗂 Выберите тип услуги:",
        "choose_service": "🛒 Выберите услугу:",
        "enter_link": "🔗 Отправьте ссылку:",
        "enter_quantity": "🔢 Введите нужное количество (мин: {min}, макс: {max}):",
        "order_summary": (
            "🧾 Информация о заказе:\n\n"
            "🛍 Услуга: {service}\n"
            "🔗 Ссылка: {link}\n"
            "🔢 Количество: {quantity}\n"
            "💰 Цена: {price} сум\n\n"
            "Подтверждаете?"
        ),
        "not_enough_balance": "❌ Недостаточно средств на балансе. Пополните баланс.",
        "order_success": "✅ Ваш заказ успешно принят!\n📦 Номер заказа: #{order_id}",
        "order_failed": "❌ Ошибка при создании заказа: {error}",
        "choose_country": "🌍 Выберите страну:",
        "number_price_confirm": "📱 {country} — цена: {price} сум.\n\nПодтверждаете покупку?",
        "number_given": "📞 Ваш номер: `{phone}`\n\nНажмите кнопку ниже, чтобы получить SMS-код.",
        "get_sms_btn": "📩 Получить SMS-код",
        "sms_not_yet": "⏳ SMS ещё не пришло, попробуйте позже.",
        "sms_received": "✅ SMS-код: `{code}`",
        "choose_stars_amount": "⭐ Выберите количество Stars:",
        "choose_premium_duration": "⭐ Выберите срок Premium:",
        "choose_gift_group": "🎁 Выберите категорию подарка:",
        "choose_gift": "🎁 Выберите подарок:",
        "enter_username": "👤 Отправьте username аккаунта, куда отправить (например: @username):",
        "confirm_order_username": (
            "🧾 Информация о заказе:\n\n"
            "🛍 Услуга: {service}\n"
            "👤 Username: {username}\n"
            "💰 Цена: {price} сум\n\n"
            "Всё верно?"
        ),
        "order_accepted_wait": "✅ Ваш заказ принят. Будет выполнен в течение 5-15 минут.",
        "premium_1m_contact": (
            "☎️ Для 1-месячного Premium свяжитесь с администратором через кнопку ниже.\n"
            "1-месячная подписка будет предоставлена администратором."
        ),
        "contact_admin_btn": "☎️ Связаться с администратором",
        "order_completed_premium": (
            "🎉 Вам предоставлен Premium!\n\n"
            "⭐ Тип Premium: {duration}\n"
            "🆔 Ваш ID: {user_id}\n\n"
            "Спасибо за покупку! 🙏"
        ),
        "order_completed_generic": "🎉 Ваш заказ выполнен! Спасибо за покупку 🙏",
        "balance_info": "💰 Ваш баланс:\n\n🆔 ID: {user_id}\n💵 Баланс: {balance} сум",
        "choose_topup_method": "💳 Выберите способ оплаты:",
        "btn_card_uzcard": "💳 Оплата картой",
        "btn_card_foreign": "🌍 Оплата из-за рубежа",
        "enter_topup_amount": "💵 На какую сумму хотите пополнить баланс? (минимум: {min} сум)",
        "amount_too_low": "❗️ Минимальная сумма {min} сум. Введите заново:",
        "card_details_uz": (
            "💳 Оплата через карту Humo\n\n"
            "💳 Номер карты: `{card}`\n"
            "👤 Владелец карты: {owner}\n"
            "💵 Сумма оплаты: {amount} сум\n\n"
            "⚠️ Не отправляйте меньше или больше указанной суммы!\n"
            "⏰ Совершите оплату в течение {minutes} минут и отправьте чек сюда.\n"
            "🚫 За фальшивый чек вы будете заблокированы на {block_hours} часов."
        ),
        "card_details_foreign": (
            "🌍 Оплата из-за рубежа\n\n"
            "💳 Visa: `{visa}`\n"
            "💳 Mastercard: `{mastercard}`\n"
            "👤 Владелец карты: {owner}\n"
            "💵 Сумма оплаты: {amount} сум\n\n"
            "⚠️ Не отправляйте меньше или больше указанной суммы!\n"
            "⏰ Совершите оплату в течение {minutes} минут и отправьте чек сюда.\n"
            "🚫 За фальшивый чек вы будете заблокированы на {block_hours} часов."
        ),
        "send_receipt": "🧾 Теперь отправьте чек об оплате (скриншот):",
        "receipt_received": "✅ Ваш чек принят и отправлен администратору на проверку. Пожалуйста, подождите.",
        "topup_expired": "⌛️ Время истекло. Вы не совершили оплату в течение {minutes} минут.",
        "topup_approved": "✅ Ваш платёж подтверждён! На баланс зачислено {amount} сум.",
        "topup_rejected": (
            "❌ Отправленный вами чек признан администратором поддельным.\n"
            "🚫 Вы заблокированы на {hours} часов."
        ),
        "unblocked_msg": "✅ Срок блокировки истёк. Вы снова можете пользоваться ботом.",
        "referral_info": (
            "🔗 Ваша реферальная ссылка:\n`{link}`\n\n"
            "👥 Приглашённые друзья: {count}\n\n"
            "💰 За каждого зарегистрированного друга: {signup_bonus} сум\n"
            "💰 Когда друг совершит первую оплату: +{first_payment_bonus} сум"
        ),
        "guide_text": (
            "📖 Инструкция по использованию бота:\n\n"
            "1️⃣ Выберите нужный раздел (Услуги, Получить номер и т.д.)\n"
            "2️⃣ Пополните баланс (через раздел Пополнить баланс)\n"
            "3️⃣ Выберите нужную услугу и оформите заказ\n"
            "4️⃣ Следите за статусом заказа в разделе \"Мои заказы\"\n\n"
            "❓ Если есть вопросы, обратитесь в раздел Поддержка."
        ),
        "btn_get_api_key": "🔑 Получить API-ключ",
        "btn_show_api_key": "👁 Показать API-ключ",
        "btn_regenerate_key": "🔄 Изменить ключ",
        "api_key_hidden": "🔑 Ваш API-ключ: `{masked}`\n\nНажмите кнопку ниже для полного просмотра.",
        "api_key_full": "🔑 Ваш API-ключ:\n`{key}`\n\n(Нажмите, чтобы скопировать)",
        "api_key_regenerated": "✅ Создан новый API-ключ:\n`{key}`",
        "support_text": "☎️ Если у вас есть вопросы, свяжитесь с администратором через кнопку ниже:",
        "no_orders": "📭 У вас пока нет заказов.",
        "orders_list_title": "📦 Ваши заказы:",
        "error_generic": "❌ Произошла ошибка. Попробуйте ещё раз.",
        "cancelled": "❌ Отменено.",
        "back_to_menu": "🏠 Вернуться в главное меню",
        "active_reminder": "🤖 Бот активен! Нажмите /start, чтобы пользоваться услугами.",
        "confirm_are_you_sure": "❗️ Вы уверены?",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TEXTS else "uz"
    text = TEXTS[lang].get(key, TEXTS["uz"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
