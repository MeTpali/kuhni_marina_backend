from fastapi import APIRouter

from core.schemas.guest_sessions import GuestSessionAckResponse

router = APIRouter(
    prefix="/session",
    tags=["session"],
)


@router.get(
    "",
    response_model=GuestSessionAckResponse,
    summary="Текущая гостевая сессия",
    description=(
        "Вызывайте при первом входе в приложение. Идентификатор сессии задаётся в HttpOnly-cookie "
        "`sessionid` (на каждом ответе API он обновляется middleware). Тело ответа не содержит id."
    ),
)
async def get_current_session():
    return GuestSessionAckResponse()
