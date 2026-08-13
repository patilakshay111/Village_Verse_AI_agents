from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.civilization import router as civilization_router
from app.api.conversations import router as conversations_router
from app.api.families import router as families_router
from app.api.locations import router as locations_router
from app.api.simulation import router as simulation_router
from app.api.stories import router as stories_router
from app.api.villagers import router as villagers_router

api_router = APIRouter()
api_router.include_router(villagers_router)
api_router.include_router(families_router)
api_router.include_router(stories_router)
api_router.include_router(conversations_router)
api_router.include_router(locations_router)
api_router.include_router(simulation_router)
api_router.include_router(civilization_router)
api_router.include_router(admin_router)
