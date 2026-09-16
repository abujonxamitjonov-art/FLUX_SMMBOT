# -*- coding: utf-8 -*-
"""Ma'lumotlar bazasi bilan ishlash - aiosqlite orqali."""
import aiosqlite
import time
import secrets
from config import DB_PATH, DEFAULT_SMM_MARGIN_PERCENT, DEFAULT_NUMBER_MARGIN_PERCENT

_db: aiosqlite.Connection | None = None


async def init_db():
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    await _db.execute("PRAGMA journal_mode=WAL;")
    await _db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            language TEXT DEFAULT 'uz',
            balance INTEGER DEFAULT 0,
            main_menu_keyboard_version INTEGER DEFAULT 0,
            registered INTEGER DEFAULT 0,
            referrer_id INTEGER,
            referral_code TEXT UNIQUE,
            ref_first_payment_done INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            blocked_until INTEGER DEFAULT 0,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_type TEXT,          -- 'smm', 'number', 'premium', 'stars', 'gift', 'pubg'
            title TEXT,
            amount TEXT,
            price INTEGER,
            status TEXT DEFAULT 'pending',   -- pending / processing / completed / cancelled
            external_id TEXT,          -- SMM panel order id yoki number hash
            extra TEXT,                -- qo'shimcha JSON matn (username, telefon va h.k.)
            channel_message_id INTEGER,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS topups (
            topup_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            method TEXT,               -- 'humo' / 'visa' / 'mastercard'
            status TEXT DEFAULT 'waiting_receipt',  -- waiting_receipt / pending_review / approved / rejected / expired
            receipt_file_id TEXT,
            admin_message_id INTEGER,
            created_at INTEGER,
            expires_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS mandatory_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            title TEXT,
            type TEXT   -- 'channel' / 'group' / 'request_channel'
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            user_id INTEGER PRIMARY KEY,
            api_key TEXT UNIQUE
        );
        """
    )
    await _db.commit()

    # Eski bazalarda yangi ustunni xavfsiz qo'shamiz.
    try:
        await _db.execute("ALTER TABLE users ADD COLUMN main_menu_keyboard_version INTEGER DEFAULT 0")
        await _db.commit()
    except Exception:
        # Ustun allaqachon mavjud bo'lsa, SQLite xatolik qaytaradi.
        pass

    # Standart sozlamalar
    await _ensure_setting("smm_margin_percent", str(DEFAULT_SMM_MARGIN_PERCENT))
    await _ensure_setting("number_margin_percent", str(DEFAULT_NUMBER_MARGIN_PERCENT))


async def _ensure_setting(key: str, default_value: str):
    cur = await _db.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = await cur.fetchone()
    if row is None:
        await _db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, default_value))
        await _db.commit()


def get_db() -> aiosqlite.Connection:
    return _db


# ---------------- USERS ----------------

async def get_user(user_id: int):
    cur = await _db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = await cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


async def mark_main_menu_keyboard_sent(user_id: int, version: int = 3):
    await _db.execute(
        "UPDATE users SET main_menu_keyboard_version=? WHERE user_id=?",
        (version, user_id),
    )
    await _db.commit()


async def create_user_if_not_exists(user_id: int, username: str, full_name: str, referrer_id: int | None = None):
    existing = await get_user(user_id)
    if existing:
        return existing
    ref_code = secrets.token_hex(4)
    await _db.execute(
        """INSERT INTO users (user_id, username, full_name, referrer_id, referral_code, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, username, full_name, referrer_id, ref_code, int(time.time())),
    )
    await _db.commit()
    return await get_user(user_id)


async def set_user_language(user_id: int, lang: str):
    await _db.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    await _db.commit()


async def set_user_phone_and_register(user_id: int, phone: str):
    await _db.execute("UPDATE users SET phone=?, registered=1 WHERE user_id=?", (phone, user_id))
    await _db.commit()


async def get_user_language(user_id: int) -> str:
    user = await get_user(user_id)
    if user and user.get("language"):
        return user["language"]
    return "uz"


async def update_balance(user_id: int, delta: int):
    await _db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (delta, user_id))
    await _db.commit()


async def set_block(user_id: int, until_ts: int):
    await _db.execute("UPDATE users SET is_blocked=1, blocked_until=? WHERE user_id=?", (until_ts, user_id))
    await _db.commit()


async def unblock_user(user_id: int):
    await _db.execute("UPDATE users SET is_blocked=0, blocked_until=0 WHERE user_id=?", (user_id,))
    await _db.commit()


async def is_currently_blocked(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user or not user["is_blocked"]:
        return False
    if user["blocked_until"] and user["blocked_until"] <= int(time.time()):
        await unblock_user(user_id)
        return False
    return True


async def get_all_user_ids():
    cur = await _db.execute("SELECT user_id FROM users WHERE registered=1")
    rows = await cur.fetchall()
    return [r[0] for r in rows]


async def count_users():
    cur = await _db.execute("SELECT COUNT(*) FROM users")
    row = await cur.fetchone()
    return row[0]


async def count_registered_users():
    cur = await _db.execute("SELECT COUNT(*) FROM users WHERE registered=1")
    row = await cur.fetchone()
    return row[0]


async def get_user_by_referral_code(code: str):
    cur = await _db.execute("SELECT * FROM users WHERE referral_code=?", (code,))
    row = await cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


async def mark_ref_first_payment_done(user_id: int):
    await _db.execute("UPDATE users SET ref_first_payment_done=1 WHERE user_id=?", (user_id,))
    await _db.commit()


async def count_referrals(user_id: int) -> int:
    cur = await _db.execute("SELECT COUNT(*) FROM users WHERE referrer_id=? AND registered=1", (user_id,))
    row = await cur.fetchone()
    return row[0]


# ---------------- ORDERS ----------------

async def create_order(user_id: int, order_type: str, title: str, amount: str, price: int,
                        status: str = "pending", external_id: str | None = None, extra: str | None = None) -> int:
    cur = await _db.execute(
        """INSERT INTO orders (user_id, order_type, title, amount, price, status, external_id, extra, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, order_type, title, amount, price, status, external_id, extra, int(time.time())),
    )
    await _db.commit()
    return cur.lastrowid


async def set_order_channel_message(order_id: int, message_id: int):
    await _db.execute("UPDATE orders SET channel_message_id=? WHERE order_id=?", (message_id, order_id))
    await _db.commit()


async def update_order_status(order_id: int, status: str):
    await _db.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    await _db.commit()


async def get_order(order_id: int):
    cur = await _db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,))
    row = await cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


async def get_user_orders(user_id: int, limit: int = 20):
    cur = await _db.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY order_id DESC LIMIT ?", (user_id, limit)
    )
    rows = await cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


# ---------------- TOPUPS ----------------

async def create_topup(user_id: int, amount: int, method: str, expires_at: int) -> int:
    cur = await _db.execute(
        """INSERT INTO topups (user_id, amount, method, expires_at, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, amount, method, expires_at, int(time.time())),
    )
    await _db.commit()
    return cur.lastrowid


async def get_topup(topup_id: int):
    cur = await _db.execute("SELECT * FROM topups WHERE topup_id=?", (topup_id,))
    row = await cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


async def set_topup_receipt(topup_id: int, file_id: str):
    await _db.execute(
        "UPDATE topups SET receipt_file_id=?, status='pending_review' WHERE topup_id=?",
        (file_id, topup_id),
    )
    await _db.commit()


async def set_topup_admin_message(topup_id: int, message_id: int):
    await _db.execute("UPDATE topups SET admin_message_id=? WHERE topup_id=?", (message_id, topup_id))
    await _db.commit()


async def set_topup_status(topup_id: int, status: str):
    await _db.execute("UPDATE topups SET status=? WHERE topup_id=?", (status, topup_id))
    await _db.commit()


# ---------------- SETTINGS ----------------

async def get_setting(key: str, default=None):
    cur = await _db.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = await cur.fetchone()
    if row is None:
        return default
    return row[0]


async def set_setting(key: str, value: str):
    await _db.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    await _db.commit()


# ---------------- MANDATORY CHANNELS ----------------

async def add_mandatory_channel(chat_id: str, title: str, chtype: str):
    await _db.execute(
        "INSERT INTO mandatory_channels (chat_id, title, type) VALUES (?, ?, ?)",
        (chat_id, title, chtype),
    )
    await _db.commit()


async def remove_mandatory_channel(chat_id: str):
    await _db.execute("DELETE FROM mandatory_channels WHERE chat_id=?", (chat_id,))
    await _db.commit()


async def get_mandatory_channels():
    cur = await _db.execute("SELECT * FROM mandatory_channels")
    rows = await cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


# ---------------- API KEYS ----------------

async def get_or_create_api_key(user_id: int) -> str:
    cur = await _db.execute("SELECT api_key FROM api_keys WHERE user_id=?", (user_id,))
    row = await cur.fetchone()
    if row:
        return row[0]
    new_key = secrets.token_hex(16)
    await _db.execute("INSERT INTO api_keys (user_id, api_key) VALUES (?, ?)", (user_id, new_key))
    await _db.commit()
    return new_key


async def regenerate_api_key(user_id: int) -> str:
    new_key = secrets.token_hex(16)
    await _db.execute(
        "INSERT INTO api_keys (user_id, api_key) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET api_key=excluded.api_key",
        (user_id, new_key),
    )
    await _db.commit()
    return new_key
