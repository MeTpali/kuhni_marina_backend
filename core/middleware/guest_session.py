"""
Гостевая сессия: идентификатор — UUID.

Приоритет на запросе: 1) cookie `sessionid` (имя из настроек);
2) заголовок X-Guest-Session-Id, если по cookie сессию восстановить нельзя.

В ответе: Set-Cookie и дублирование UUID в X-Guest-Session-Id
(для Flutter Web нужен expose_headers в CORS).
"""
from uuid import UUID

from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings
from core.guest_session_policy import is_guest_session_stale
from repositories.guest_sessions import GuestSessionRepository

# Запрос и ответ: один заголовок с UUID гостевой сессии.
GUEST_SESSION_EXPOSE_HEADER = "X-Guest-Session-Id"

SKIP_PATH_PREFIXES: tuple[str, ...] = (
    "/admin",
    "/static",
    "/api/v1/docs",
    "/api/v1/redoc",
    "/api/v1/openapi.json",
)


def _should_skip_guest_session(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in SKIP_PATH_PREFIXES)


async def _try_resume_session(
    repo: GuestSessionRepository,
    raw: str | None,
    *,
    ttl_days: int,
) -> UUID | None:
    """Восстановить активную сессию по строке UUID (cookie или заголовок)."""
    if not raw or not str(raw).strip():
        return None
    try:
        parsed = UUID(str(raw).strip())
    except ValueError:
        return None
    row = await repo.get_by_id(parsed)
    if row is None or is_guest_session_stale(row.last_seen_at, ttl_days=ttl_days):
        return None
    updated = await repo.touch(parsed)
    return updated.id if updated is not None else None


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

            ttl_days = settings.GUEST_SESSION_TTL_DAYS
            cookie_raw = request.cookies.get(settings.GUEST_SESSION_COOKIE_NAME)
            session_id = await _try_resume_session(repo, cookie_raw, ttl_days=ttl_days)

            if session_id is None:
                header_raw = request.headers.get(GUEST_SESSION_EXPOSE_HEADER)
                if header_raw is None:
                    header_raw = request.headers.get("x-guest-session-id")
                session_id = await _try_resume_session(repo, header_raw, ttl_days=ttl_days)

            if session_id is None:
                created = await repo.create()
                session_id = created.id

            request.state.guest_session_id = session_id

        response = await call_next(request)
        _attach_session_cookie(response, session_id)
        response.headers[GUEST_SESSION_EXPOSE_HEADER] = str(session_id)
        return response
