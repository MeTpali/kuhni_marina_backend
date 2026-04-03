"""
Удаление устаревших гостевых сессий (last_seen_at старше GUEST_SESSION_TTL_DAYS).
Избранное удаляется каскадом.

Запуск локально (из корня backend, с .env):
    python -m jobs.cleanup_guest_sessions

Проверка без удаления:
    python -m jobs.cleanup_guest_sessions --dry-run

Cron на сервере (пример, ежедневно в 03:15):
    15 3 * * * cd /path/to/backend && /path/to/venv/bin/python -m jobs.cleanup_guest_sessions >> /var/log/guest_session_cleanup.log 2>&1

Docker Compose (профиль cron, тот же образ и .env, что у API):
    docker compose --profile cron run --rm guest-session-cleanup
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from sqlalchemy import text

from core.config import settings, setup_logging
from core.guest_session_policy import stale_last_seen_cutoff_utc
from core.models.db_helper import db_helper
from repositories.guest_sessions import GuestSessionRepository

logger = logging.getLogger(__name__)


async def run_cleanup(*, dry_run: bool) -> int:
    setup_logging()
    ttl = settings.GUEST_SESSION_TTL_DAYS
    batch = settings.GUEST_SESSION_CLEANUP_BATCH_SIZE
    cutoff = stale_last_seen_cutoff_utc(ttl_days=ttl)

    logger.info(
        "Guest session cleanup: ttl_days=%s batch_size=%s cutoff_utc=%s dry_run=%s",
        ttl,
        batch,
        cutoff.isoformat(),
        dry_run,
    )

    try:
        async with db_helper.session_factory() as session:
            await session.execute(text("SET search_path TO kuhni_marina, public"))
            repo = GuestSessionRepository(session)

            if dry_run:
                n = await repo.count_stale_before(cutoff)
                logger.info("Dry run: %s stale guest session(s) would be deleted", n)
                return 0

            total = 0
            while True:
                deleted = await repo.delete_stale_batch(cutoff, batch)
                total += deleted
                if deleted:
                    logger.info("Deleted batch: %s row(s), running total=%s", deleted, total)
                if deleted < batch:
                    break

            logger.info("Guest session cleanup finished: removed %s row(s)", total)
            return 0
    finally:
        await db_helper.engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Удаление устаревших guest_sessions по TTL.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только посчитать устаревшие сессии, без DELETE",
    )
    args = parser.parse_args()
    try:
        code = asyncio.run(run_cleanup(dry_run=args.dry_run))
    except Exception:
        setup_logging()
        logging.getLogger(__name__).exception("Guest session cleanup failed")
        code = 1
    sys.exit(code)


if __name__ == "__main__":
    main()
