# -*- coding: utf-8 -*-
from fastapi import APIRouter
from .auth_router import auth_router
from .users_router import users_router
from .rankings_router import rankings_router
from .postbox_router import postbox_router
from .config_router import config_router
from .payment_router import payment_router
from .friends_router import friends_router
from .mmp_push_app_router import mmp_push_app_router
from .guild_router import guild_router
from .currency_router import currency_router
from .test import test_router
from .notice_router import notice_router
from .control_router import control_router
from .game_router import game_router
from .refresh_router import refresh_router
from .shop_router import shop_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(postbox_router)
router.include_router(rankings_router)
router.include_router(config_router)
router.include_router(payment_router)
router.include_router(friends_router)
router.include_router(mmp_push_app_router)
router.include_router(guild_router)
router.include_router(test_router)
router.include_router(currency_router)
router.include_router(notice_router)
router.include_router(control_router)
router.include_router(game_router)
router.include_router(refresh_router)
router.include_router(shop_router)