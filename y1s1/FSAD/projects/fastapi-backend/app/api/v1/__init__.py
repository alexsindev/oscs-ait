from fastapi import APIRouter

from .routes_courses import router as courses_router
from .routes_users import router as users_router
from .routes_auth import router as auth_router
from .routes_posts import router as posts_router
from .routes_enrollments import router as enrollments_router
from .routes_feedbacks import router as feedbacks_router
from .routes_public import router as public_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(users_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(posts_router)
api_v1_router.include_router(enrollments_router)
api_v1_router.include_router(feedbacks_router)
api_v1_router.include_router(public_router)
