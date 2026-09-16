# -*- coding: utf-8 -*-
import re
from database import db
from utils import number_api

try:
    import phonenumbers
    from phonenumbers import geocoder
except ImportError:
    phonenumbers = None
    geocoder = None

ALIASES = {
    'usa':'United States','us':'United States','america':'United States',
    'uk':'United Kingdom','england':'United Kingdom','britain':'United Kingdom',
    'russia':'Russia','kazakhstan':'Kazakhstan','uzbekistan':'Uzbekistan',
}

def normalize_name(name: str) -> str:
    name = re.sub(r'[^\w]+', ' ', name or '', flags=re.UNICODE).strip().casefold()
    return ALIASES.get(name, name)

def normalize_phone(raw: str) -> str:
    digits=re.sub(r'\D','',raw or '')
    if raw.strip().startswith('+'):
        return '+'+digits
    if digits.startswith('00'):
        return '+'+digits[2:]
    return '+'+digits

def detect_country(phone: str):
    if not phonenumbers:
        return None
    try:
        parsed=phonenumbers.parse(phone, None)
        if not phonenumbers.is_possible_number(parsed):
            return None
        region=phonenumbers.region_code_for_number(parsed)
        if not region:
            return None
        # Region code is resolved by the numbering plan, including area-code distinctions for shared calling codes.
        return phonenumbers.region_code_for_number(parsed)
    except Exception:
        return None

def country_display(region: str, phone: str = ""):
    if not region: return None
    names={
      'UZ':'Uzbekistan','US':'USA','CA':'Canada','KZ':'Kazakhstan','RU':'Russia','GB':'United Kingdom',
      'DE':'Germany','FR':'France','TR':'Turkey','UA':'Ukraine','AE':'United Arab Emirates','IN':'India',
      'PK':'Pakistan','BD':'Bangladesh','ID':'Indonesia','BR':'Brazil','MX':'Mexico','AU':'Australia',
    }
    if region in names: return names[region]
    try:
        label = geocoder.description_for_region(region, 'en')
        return label or region
    except Exception:
        return region

async def add_manual_number_from_command(text: str) -> str:
    parts=(text or '').split()
    if len(parts)<2:
        return '❌ Foydalanish: /add_number +998901234567 [DAVLAT]'
    phone=normalize_phone(parts[1])
    if not re.fullmatch(r'\+\d{7,15}', phone):
        return '❌ Nomer noto‘g‘ri. Masalan: /add_number +998901234567'
    region=detect_country(phone)
    explicit=' '.join(parts[2:]).strip() if len(parts)>2 else ''
    if explicit:
        name=explicit.strip()
        normalized=normalize_name(name)
        if region:
            detected_name=country_display(region, phone)
            # Explicit country is authoritative only when it matches the numbering-plan result.
            if detected_name and normalize_name(detected_name)!=normalized:
                # USA/United States alias normalization covers common spelling differences.
                return f'❌ Nomer prefiks/raqam kodi bo‘yicha {detected_name} ga tegishli, {name} bo‘limiga qo‘shib bo‘lmaydi.'
    else:
        if not region:
            return '❌ Davlatni aniq aniqlab bo‘lmadi. Davlat bo‘limini yaratish uchun /add_number +raqam DAVLAT ko‘rinishida yuboring.'
        name=country_display(region, phone); normalized=normalize_name(name)
    country=await db.get_manual_country_by_name(normalized)
    if not country:
        base,_=await number_api.get_country_price_by_name(name)
        if not base or base<=0:
            return f'❌ {name} uchun Number API narxi topilmadi. Avval shu davlat API ro‘yxatida narxi mavjud bo‘lishi kerak.'
        country=await db.create_manual_country(name,normalized,int(round(base)))
    try:
        nid=await db.add_manual_number(country['id'],phone)
    except Exception as e:
        if 'UNIQUE' in str(e).upper(): return '❌ Bu nomer bazada allaqachon mavjud.'
        return '❌ Nomer qo‘shishda xatolik yuz berdi.'
    margin=float(await db.get_setting('number_margin_percent',20)); price=number_api.apply_margin(country['base_price'],margin)
    return f"✅ Manual nomer qo‘shildi.\n🌍 Davlat: {country['name']}\n📞 Nomer: {phone}\n💰 Mijoz narxi: {int(price):,} so'm".replace(',',' ')
