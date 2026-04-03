"""
Единая политика «протухания» гостевой сессии по last_seen_at и TTL в днях.
Используется middleware и фоновой очисткой.
"""
from datetime import datetime, timedelta, timezone


def stale_last_seen_cutoff_utc(*, ttl_days: int) -> datetime:
    """
    Граница времени: сессии с last_seen_at строго раньше этой отметки считаются устаревшими
    (совпадает с логикой GuestSessionMiddleware).
    """
    return datetime.now(timezone.utc) - timedelta(days=ttl_days)


def is_guest_session_stale(last_seen_at: datetime, *, ttl_days: int) -> bool:
    if last_seen_at.tzinfo is None:
        last_seen_at = last_seen_at.replace(tzinfo=timezone.utc)
    cutoff = stale_last_seen_cutoff_utc(ttl_days=ttl_days)
    return last_seen_at < cutoff
