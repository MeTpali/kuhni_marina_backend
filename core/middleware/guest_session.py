"""
Гостевая сессия: cookie sessionid (только UUID), без тела ответа с данными сессии.
"""
from uuid import UUID

from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings
from core.guest_session_policy import is_guest_session_stale
from repositories.guest_sessions import GuestSessionRepository

SKIP_PATH_PREFIXES: tuple[str, ...] = (
    "/admin",
    "/static",
    "/api/v1/docs",
    "/api/v1/redoc",
    "/api/v1/openapi.json",
)


def _should_skip_guest_session(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in SKIP_PATH_PREFIXES)


def _attach_session_cookie(response: Response, session_id: UUID) -> None:
    max_age = settings.GUEST_SESSION_TTL_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=settings.GUEST_SESSION_COOKIE_NAME,
        value=str(session_id),
        max_age=max_age,
        httponly=True,
        secure=settings.GUEST_SESSION_COOKIE_SECURE,
        samesite=settings.GUEST_SESSION_COOKIE_SAMESITE,
        path="/",
    )


class GuestSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _should_skip_guest_session(request.url.path):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        from db.session import async_session

        async with async_session() as db:
            await db.execute(text("SET search_path TO kuhni_marina, public"))
            repo = GuestSessionRepository(db)

            cookie_raw = request.cookies.get(settings.GUEST_SESSION_COOKIE_NAME)
            session_id: UUID | None = None
            ttl_days = settings.GUEST_SESSION_TTL_DAYS

            if cookie_raw:
                try:
                    parsed = UUID(cookie_raw)
                except ValueError:
                    parsed = None
                if parsed is not None:
                    row = await repo.get_by_id(parsed)
                    if row is not None and not is_guest_session_stale(
                        row.last_seen_at, ttl_days=ttl_days
                    ):
                        updated = await repo.touch(parsed)
                        if updated is not None:
                            session_id = updated.id

            if session_id is None:
                created = await repo.create()
                session_id = created.id

            request.state.guest_session_id = session_id

        response = await call_next(request)
        _attach_session_cookie(response, session_id)
        return response
