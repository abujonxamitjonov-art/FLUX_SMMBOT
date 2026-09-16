# -*- coding: utf-8 -*-
import json
import time
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import db
from texts import t
from keyboards.numbers import countries_kb, manual_numbers_kb, get_sms_kb
from utils import number_api

router=Router(); _countries_cache={'data':None,'ts':0,'margin':None}

async def _manual_country_price(name):
    base,_=await number_api.get_country_price_by_name(name)
    return int(round(base or 0))

async def get_cached_countries():
    margin=float(await db.get_setting('number_margin_percent',20))
    if _countries_cache['data'] is None or time.time()-_countries_cache['ts']>300 or _countries_cache['margin']!=margin:
        api_countries=await number_api.get_countries()
        result=[]
        manual_countries=await db.get_manual_countries()
        for c in api_countries:
            try: base=float(c.get('price',0) or 0)
            except: continue
            same=next((mc for mc in manual_countries if str(mc['name']).casefold()==str(c.get('name','')).casefold()),None)
            result.append({'name':c.get('name',''), 'code':str(c.get('code','')), 'price':number_api.apply_margin(base,margin), 'key':'api:'+str(c.get('code','')), 'source':'mixed' if same else 'api', 'manual_country_id': same['id'] if same else None})
        for mc in manual_countries:
            if not any(str(c['name']).casefold()==str(mc['name']).casefold() for c in result) and mc['base_price']>0:
                result.append({'name':mc['name'],'code':str(mc['id']),'price':number_api.apply_margin(mc['base_price'],margin),'key':'manual:'+str(mc['id']),'source':'manual','manual_country_id':mc['id']})
        _countries_cache.update(data=result,ts=time.time(),margin=margin)
    return _countries_cache['data']

@router.callback_query(F.data=='menu_number')
async def cb_menu_number(callback:CallbackQuery):
    user=await db.get_user(callback.from_user.id); lang=user['language']; countries=await get_cached_countries()
    if not countries: await callback.answer('⏳ Hozircha davlatlar mavjud emas.',show_alert=True); return
    await callback.message.edit_text(t(lang,'choose_country'),reply_markup=countries_kb(lang,countries,0)); await callback.answer()

@router.callback_query(F.data.startswith('num_page_'))
async def cb_num_page(callback:CallbackQuery):
    page=int(callback.data.replace('num_page_','')); user=await db.get_user(callback.from_user.id); countries=await get_cached_countries()
    await callback.message.edit_text(t(user['language'],'choose_country'),reply_markup=countries_kb(user['language'],countries,page)); await callback.answer()

@router.callback_query(F.data.startswith('num_api_buy_'))
async def cb_api_buy(callback:CallbackQuery):
    code=callback.data.replace('num_api_buy_',''); user=await db.get_user(callback.from_user.id); lang=user['language']; countries=await get_cached_countries(); c=next((x for x in countries if x['source'] in ('api','mixed') and x['code']==code),None)
    if not c: await callback.answer('❌ Topilmadi',show_alert=True); return
    price=int(round(c['price']))
    if user['balance']<price: await callback.message.edit_text(t(lang,'not_enough_balance')); await callback.answer(); return
    result=await number_api.buy_number(code)
    if 'error' in result or 'phone' not in result: await callback.answer(f"❌ {result.get('error','Xatolik')}",show_alert=True); return
    await db.update_balance(user['user_id'],-price)
    oid=await db.create_order(user['user_id'],'number',f"Nomer olish - {c['name']}",result['phone'],price,status='completed',external_id=result['hash'],extra=json.dumps({'phone':result['phone'],'source':'api','country_code':code}))
    from utils.order_channel import post_new_order
    name=f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
    await post_new_order(callback.bot,oid,name,f"Nomer - {c['name']}",price)
    await callback.message.edit_text(t(lang,'number_given',phone=result['phone']),reply_markup=get_sms_kb(lang,oid,False)); await callback.answer()

@router.callback_query(F.data.startswith('num_country_'))
async def cb_pick_country(callback:CallbackQuery):
    key=callback.data.replace('num_country_',''); user=await db.get_user(callback.from_user.id); lang=user['language']; countries=await get_cached_countries(); c=next((x for x in countries if x['key']==key),None)
    if not c: await callback.answer('❌ Topilmadi',show_alert=True); return
    if c['source'] in ('manual','mixed'):
        country_id=int(c['manual_country_id'] or c['code'])
        nums=await db.get_available_manual_numbers(country_id)
        if nums:
            await callback.message.edit_text(f"🌍 {c['name']}\n💰 Narx: {int(c['price']):,} so'm",reply_markup=manual_numbers_kb(lang,nums,country_id,0,country_id and (20),c['code'] if c['source']=='mixed' else None))
            await callback.answer(); return
        if c['source']=='manual': await callback.answer('⏳ Bu davlatda hozircha nomer yo‘q.',show_alert=True); return
    price=int(round(c['price']))
    if user['balance']<price: await callback.message.edit_text(t(lang,'not_enough_balance')); await callback.answer(); return
    result=await number_api.buy_number(c['code'])
    if 'error' in result or 'phone' not in result: await callback.answer(f"❌ {result.get('error','Xatolik')}",show_alert=True); return
    await db.update_balance(user['user_id'],-price)
    oid=await db.create_order(user['user_id'],'number',f"Nomer olish - {c['name']}",result['phone'],price,status='completed',external_id=result['hash'],extra=json.dumps({'phone':result['phone'],'source':'api','country_code':c['code']}))
    from utils.order_channel import post_new_order
    name=f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
    await post_new_order(callback.bot,oid,name,f"Nomer - {c['name']}",price)
    await callback.message.edit_text(t(lang,'number_given',phone=result['phone']),reply_markup=get_sms_kb(lang,oid,False)); await callback.answer()

@router.callback_query(F.data.startswith('num_manual_page_'))
async def cb_manual_page(callback:CallbackQuery):
    _, _, country_id, page = callback.data.split('_')
    country_id=int(country_id); page=int(page)
    country=await db.get_manual_country(country_id); user=await db.get_user(callback.from_user.id)
    nums=await db.get_available_manual_numbers(country_id)
    if not country or not nums: await callback.answer('❌ Nomerlar topilmadi.',show_alert=True); return
    margin=float(await db.get_setting('number_margin_percent',20)); price=number_api.apply_margin(country['base_price'],margin)
    await callback.message.edit_text(f"🌍 {country['name']}\n💰 Narx: {int(price):,} so'm".replace(',',' '),reply_markup=manual_numbers_kb(user['language'],nums,country_id,page))
    await callback.answer()

@router.callback_query(F.data.startswith('num_manual_'))
async def cb_pick_manual(callback:CallbackQuery):
    nid=int(callback.data.replace('num_manual_','')); n=await db.get_manual_number(nid); user=await db.get_user(callback.from_user.id); lang=user['language']
    if not n or n['status']!='available': await callback.answer('❌ Bu nomer allaqachon sotilgan.',show_alert=True); return
    margin=float(await db.get_setting('number_margin_percent',20)); price=number_api.apply_margin(n['base_price'],margin)
    if user['balance']<price: await callback.message.edit_text(t(lang,'not_enough_balance')); await callback.answer(); return
    if not await db.reserve_manual_number(nid,user['user_id']): await callback.answer('❌ Bu nomer allaqachon olindi.',show_alert=True); return
    extra={'phone':n['phone'],'source':'manual','manual_number_id':nid,'country_id':n['country_id'],'code_sent':False,'code_sent_at':0,'entered':False,'logged_out':False}
    oid=await db.create_order(user['user_id'],'number',f"Nomer olish - {n['country_name']}",n['phone'],price,status='manual_waiting_code',extra=json.dumps(extra))
    await db.update_balance(user['user_id'],-price)
    from utils.order_channel import post_new_order
    name=f"{callback.from_user.full_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.full_name
    await post_new_order(callback.bot,oid,name,f"Manual nomer - {n['country_name']}",price)
    await callback.message.edit_text(t(lang,'number_given',phone=n['phone']),reply_markup=get_sms_kb(lang,oid,True)); await callback.answer()

@router.callback_query(F.data.startswith('num_getsms_'))
async def cb_get_sms(callback:CallbackQuery):
    oid=int(callback.data.replace('num_getsms_','')); order=await db.get_order(oid); user=await db.get_user(callback.from_user.id); lang=user['language']
    if not order or order['user_id']!=callback.from_user.id: await callback.answer('❌ Xatolik',show_alert=True); return
    extra=json.loads(order['extra'] or '{}')
    if extra.get('source')=='manual':
        if extra.get('code_sent') and time.time()-extra.get('code_sent_at',0)<=120: await callback.answer('⏳ Kod allaqachon yuborilgan.',show_alert=True); return
        if extra.get('code_sent'): await callback.answer('⌛ Kodning 2 daqiqalik muddati tugagan.',show_alert=True); return
        await callback.bot.send_message(__import__('config').ADMIN_ID,f"📩 Manual nomer uchun SMS kod so‘raldi.\n\n🧾 Buyurtma: #{oid}\n👤 Mijoz ID: {callback.from_user.id}\n📞 Nomer: {extra.get('phone')}\n\nKodini shu botga yuboring.")
        from states import AdminManualNumber
        from aiogram.fsm.context import FSMContext
        # Dispatcher state context is not directly available here; admin code handler uses per-user pending order setting.
        await db.set_setting(f'manual_pending_admin_{__import__("config").ADMIN_ID}',str(oid))
        await callback.answer('✅ Kod so‘rovi adminga yuborildi.')
        return
    result=await number_api.get_sms(order['external_id'])
    if 'error' in result or not result.get('sms'): await callback.answer(t(lang,'sms_not_yet'),show_alert=True); return
    await callback.answer(); await callback.message.answer(t(lang,'sms_received',code=result['sms']))

@router.callback_query(F.data.startswith('num_entered_'))
async def cb_entered(callback:CallbackQuery):
    oid=int(callback.data.replace('num_entered_','')); order=await db.get_order(oid)
    if not order or order['user_id']!=callback.from_user.id: await callback.answer('❌ Xatolik',show_alert=True); return
    extra=json.loads(order['extra'] or '{}')
    if extra.get('source')!='manual' or not extra.get('code_sent'): await callback.answer('⏳ Avval kodni oling.',show_alert=True); return
    if time.time()-extra.get('code_sent_at',0)>120: await callback.answer('⌛ Kodning 2 daqiqalik muddati tugagan.',show_alert=True); return
    extra['entered']=True
    await db.update_order_extra(oid,json.dumps(extra))
    from config import ADMIN_ID
    await callback.bot.send_message(ADMIN_ID,f"👤 Mijoz akkauntga kirdi.\n🧾 Buyurtma: #{oid}\n👤 ID: {callback.from_user.id}\n📞 Nomer: {extra.get('phone')}\n\nAkkauntdan chiqib bo‘lgach, Chiqdim tugmasini bosing.",reply_markup=__import__('aiogram').types.InlineKeyboardMarkup(inline_keyboard=[[__import__('aiogram').types.InlineKeyboardButton(text='Chiqdim',callback_data=f'num_exited_{oid}')]]))
    await callback.answer('✅ Adminga xabar yuborildi.')

@router.callback_query(F.data.startswith('num_exited_'))
async def cb_exited(callback:CallbackQuery):
    from config import ADMIN_ID
    if callback.from_user.id!=ADMIN_ID: await callback.answer('❌ Faqat admin.',show_alert=True); return
    oid=int(callback.data.replace('num_exited_','')); order=await db.get_order(oid)
    if not order: await callback.answer('❌ Buyurtma topilmadi.',show_alert=True); return
    extra=json.loads(order['extra'] or '{}')
    if extra.get('source')!='manual' or not extra.get('entered'):
        await callback.answer('❌ Avval mijoz Kirdim tugmasini bosishi kerak.',show_alert=True); return
    extra['logged_out']=True
    await db.update_order_extra(oid,json.dumps(extra)); await db.update_order_status(oid,'completed')
    await callback.bot.send_message(order['user_id'],'✅ Akkauntdan chiqildi. Endi akkaunt to‘liq sizning huquqingizda.')
    await callback.message.edit_text(f'✅ #{oid} — akkauntdan chiqildi, mijozga topshirildi.')
    await callback.answer()
