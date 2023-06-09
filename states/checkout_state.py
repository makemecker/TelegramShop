from aiogram.fsm.state import StatesGroup, State


class CheckoutState(StatesGroup):
    check_cart = State()
    name = State()
    pickup_delivery = State()
    address = State()
    phone = State()
    confirm = State()
