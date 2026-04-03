from core.schemas.base import BaseSchema


class GuestSessionAckResponse(BaseSchema):
    """Подтверждение, что гостевая сессия активна (идентификатор только в cookie sessionid)."""

    ok: bool = True
