# -*- coding: utf-8 -*-
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    choosing_language = State()
    waiting_contact = State()


class ServiceOrder(StatesGroup):
    choosing_network = State()
    choosing_type = State()
    choosing_service = State()
    entering_link = State()
    entering_quantity = State()
    confirming = State()


class NumberOrder(StatesGroup):
    choosing_country = State()
    confirming = State()


class UsernameOrder(StatesGroup):
    """Stars / Gift / Premium (3,6,12 oy) uchun umumiy holat."""
    entering_username = State()
    confirming = State()


class TopUp(StatesGroup):
    choosing_method = State()
    entering_amount = State()
    waiting_receipt = State()


class AdminBroadcast(StatesGroup):
    waiting_message = State()


class AdminMargin(StatesGroup):
    waiting_smm_margin = State()
    waiting_number_margin = State()


class AdminMandatoryChannel(StatesGroup):
    waiting_channel_id = State()


class AdminManualNumber(StatesGroup):
    waiting_code = State()
