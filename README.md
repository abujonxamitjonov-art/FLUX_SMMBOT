# LOCK SMM Bot

Telegram SMM bot — Render + GitHub orqali ishga tushiriladi.

## 1. GitHub'ga joylash

```bash
git init
git add .
git commit -m "Birinchi versiya"
git branch -M main
git remote add origin <SIZNING_GITHUB_REPO_URL>
git push -u origin main
```

## 2. Render'da deploy qilish

1. https://render.com da **New +** → **Background Worker** tanlang (bu bot uzluksiz ishlashi kerak bo'lgani uchun Web Service emas, Worker kerak).
2. GitHub repo'ingizni ulang.
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python main.py`
5. **Environment Variables** bo'limiga qo'shing:
   - `BOT_TOKEN` — BotFather'dan olingan token

Boshqa barcha ma'lumotlar (API kalitlar, narxlar, karta raqamlari, admin ID, kanal) `config.py` faylida allaqachon yozilgan.

## 3. Buyurtmalar kanali

Botni `@FLUX_buyurtmalar` kanaliga **admin** qilib qo'shing (xabar yuborish huquqi bilan).

## 4. Majburiy obuna kanallari

Botga admin sifatida `/start` bosgandan so'ng, quyidagi buyruq bilan kanal/guruh qo'shing:

```
/add_channel
```

so'ng kanal username'ini yuboring (masalan `@kanalim`). Bot o'sha kanalda **admin** bo'lishi shart (a'zolikni tekshirish uchun).

## 5. Admin buyruqlari

`/admin` — barcha buyruqlar ro'yxati botda ko'rinadi (chap pastdagi menyu tugmasi orqali ham).

## 6. Muhim eslatmalar

- **Ma'lumotlar bazasi**: SQLite fayl sifatida saqlanadi (`bot_database.db`). Render'ning **bepul** tarifida disk doimiy emas — deploy qayta ishga tushganda ma'lumotlar o'chib ketishi mumkin. Agar bu muhim bo'lsa:
  - Render'da **persistent disk** ulang (pullik tarif), yoki
  - Tashqi PostgreSQL bazasidan foydalanish uchun kodni moslashtirish kerak bo'ladi (so'rasangiz buni ham qilib beraman).
- **Xizmatlar (Telegram/Instagram/TikTok/YouTube)** SMM panelidan avtomatik olinadi va nomiga qarab turkumlarga (Obunachilar/Layk/Ko'rish va h.k.) ajratiladi. Agar biror xizmat noto'g'ri turkumga tushsa, `utils/service_classifier.py` faylidagi kalit so'zlarni sozlash kerak bo'ladi.
- **Margin (foyda foizi)**: `/set_smm_margin` va `/set_number_margin` buyruqlari orqali istalgan vaqt o'zgartirilishi mumkin.
- **Bot polling rejimida ishlaydi** (webhook emas) — bu Render Background Worker uchun eng oddiy va barqaror usul.

## 7. Loyiha tuzilishi

```
smmbot/
├── main.py                  # Ishga tushirish nuqtasi
├── config.py                 # Barcha sozlamalar, narxlar, kalitlar
├── texts.py                  # UZ/RU matnlar
├── states.py                  # FSM holatlari
├── database/
│   └── db.py                  # SQLite bilan ishlash
├── handlers/
│   ├── user.py                 # start, til, kontakt, majburiy obuna, menyu
│   ├── services.py              # Telegram/Instagram/TikTok/YouTube + PUBG UC
│   ├── premium_stars_gifts.py    # Stars/Premium/Gift tanlash
│   ├── manual_orders.py           # Admin qo'lda bajaradigan buyurtmalar oqimi
│   ├── numbers.py                  # Nomer olish
│   ├── topup.py                     # Hisob to'ldirish
│   ├── orders.py                     # Buyurtmalarim
│   ├── referral.py                    # Referal bonus
│   └── admin.py                         # Admin panel
├── keyboards/                              # Barcha inline klaviaturalar
└── utils/
    ├── smm_api.py                          # SMM panel API wrapper
    ├── number_api.py                        # Nomer olish API wrapper
    ├── service_classifier.py                 # Xizmatlarni turkumlash
    └── order_channel.py                       # Buyurtmalar kanaliga post qilish
```
