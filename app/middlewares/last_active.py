# from datetime import datetime, timezone
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from app.configs.dependencies import get_current_user, get_db


# class LastActiveMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         response = await call_next(request)
#         try:
#             db = await get_db()
#             user = await get_current_user(request, db)
#             if user:
#                 user.last_active_at = datetime.now(timezone.utc)
#                 await db.commit()
#         except Exception:
#             pass
#         return response
