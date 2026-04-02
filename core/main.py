from ninja import NinjaAPI
from ninja_simple_jwt.auth.views.api import mobile_auth_router, web_auth_router
from app.users.urls import user_router
from app.microtiks.urls import microtik_router
from app.admin_microtiks.urls import owner_microtik
from app.clients.urls import client_router

api = NinjaAPI()

api.add_router("/auth/mobile/", mobile_auth_router, tags=["Auth"])
api.add_router("/auth/web/", web_auth_router, tags=["Auth"])
api.add_router("/users/", user_router)
api.add_router("/microtik/", microtik_router)
api.add_router("/client/", client_router)
api.add_router("/owner-microtik/", owner_microtik)
