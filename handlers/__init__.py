from .menu import menu_router
from .cart import cart_router
from .catalog import catalog_router
from .delivery_status import delivery_router
from .other import other_router
from aiogram import Router
from .search import search_router


router: Router = Router()
router.include_routers(menu_router, cart_router, catalog_router, search_router, delivery_router, other_router)
