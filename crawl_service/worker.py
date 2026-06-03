"""Long-running morgue archive worker."""

from __future__ import annotations

import os
import re
import signal
import time
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Callable

from crawl_service.morgue.fetcher import (
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    fetch_morgue_file_text,
    fetch_morgue_files,
    fetch_morgue_users,
)
from crawl_service.morgue.types import MorgueFile, MorgueUser
from crawl_service.observability import (
    CrawlProcessSummary,
    CrawlServicePassSummary,
    configure_logging,
    crawl_pass_message,
    get_logger,
)
from crawl_service.processor import process_pending_raw_morgue_files
from crawl_service.repository import (
    CrawlArtifactRepository,
    CrawlFileRecord,
    CrawlUserRecord,
    FETCH_STATUS_FETCHED,
    RawMorgueFileRecord,
    repository_from_env,
)


DEFAULT_MORGUE_BASE_URL = "https://archive.nemelex.cards/morgue"
DEFAULT_CRAWL_START_DATE = date(2026, 1, 1)
DEFAULT_REQUEST_DELAY_SECONDS = 1.0
DEFAULT_LOOP_INTERVAL_SECONDS = 10_800.0
DEFAULT_PROCESS_LIMIT = 100
USER_SKIP_MODE_CONSERVATIVE = "conservative"
USER_SKIP_MODE_MODIFIED_AT = "modified_at"
MORGUE_FILE_STAMP_RE = re.compile(
    r"^\.?morgue-(?P<player>.+?)-(?P<date>\d{8})-\d{6}\.(?P<ext>txt|lst)$"
)
MORGUE_INDEX_DATE_FORMAT = "%Y-%b-%d %H:%M"


@dataclass(frozen=True)
class CrawlWorkerConfig:
    """Runtime configuration for the archive-wide crawl worker."""

    base_url: str = DEFAULT_MORGUE_BASE_URL
    start_date: date = DEFAULT_CRAWL_START_DATE
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS
    loop_interval_seconds: float = DEFAULT_LOOP_INTERVAL_SECONDS
    timeout: float = DEFAULT_TIMEOUT
    user_agent: str = DEFAULT_USER_AGENT
    user_skip_mode: str = USER_SKIP_MODE_CONSERVATIVE
    process_limit: int = DEFAULT_PROCESS_LIMIT


@dataclass(frozen=True)
class CrawlWorkerRunSummary:
    """One full root-list scan summary."""

    users_seen: int = 0
    users_skipped_by_date: int = 0
    users_skipped_unchanged: int = 0
    users_scanned: int = 0
    users_failed: int = 0
    files_processed: int = 0
    files_skipped_existing_raw: int = 0
    artifacts_imported: int = 0


@dataclass(frozen=True)
class _UserScanSummary:
    """One player directory scan summary."""

    files_processed: int = 0
    files_skipped_existing_raw: int = 0
    artifacts_imported: int = 0


class RequestThrottle:
    """Ensures a minimum delay before each outbound HTTP request."""

    def __init__(
        self,
        delay_seconds: float,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.delay_seconds = max(delay_seconds, 0.0)
        self.sleep = sleep

    def wait(self) -> None:
        if self.delay_seconds > 0:
            self.sleep(self.delay_seconds)


class CrawlWorker:
    """Continuously ingests changed morgue files into raw storage."""

    def __init__(
        self,
        repository: CrawlArtifactRepository,
        config: CrawlWorkerConfig | None = None,
        throttle: RequestThrottle | None = None,
        sleep: Callable[[float], None] = time.sleep,
        list_users: Callable[..., list[MorgueUser]] = fetch_morgue_users,
        list_files: Callable[..., list[MorgueFile]] = fetch_morgue_files,
        fetch_file_text: Callable[..., str] = fetch_morgue_file_text,
        process_pending: Callable[..., int] = process_pending_raw_morgue_files,
    ) -> None:
        self.repository = repository
        self.config = config or CrawlWorkerConfig()
        self.throttle = throttle or RequestThrottle(
            self.config.request_delay_seconds,
            sleep=sleep,
        )
        self.sleep = sleep
        self.list_users = list_users
        self.list_files = list_files
        self.fetch_file_text = fetch_file_text
        self.process_pending = process_pending
        self.logger = get_logger(__name__)
        self._stop_requested = False

    def request_stop(self, *_args) -> None:
        self._stop_requested = True

    def run_forever(self) -> None:
        while not self._stop_requested:
            summary = self.run_pass()
            self.logger.info(crawl_pass_message(summary))
            if summary.process.error:
                self.logger.warning("Processing pass failed: %s", summary.process.error)
            self._sleep_until_next_pass()

    def run_pass(self) -> CrawlServicePassSummary:
        started_at = time.monotonic()
        crawl_summary = self.run_once()
        process_summary = self._process_pending_raw_files()
        return CrawlServicePassSummary(
            crawl=crawl_summary,
            process=process_summary,
            duration_seconds=time.monotonic() - started_at,
        )

    def run_once(self) -> CrawlWorkerRunSummary:
        self.throttle.wait()
        users = self.list_users(
            self.config.base_url,
            timeout=self.config.timeout,
            user_agent=self.config.user_agent,
        )

        users_skipped_by_date = 0
        users_skipped_unchanged = 0
        users_scanned = 0
        users_failed = 0
        files_processed = 0
        files_skipped_existing_raw = 0
        artifacts_imported = 0

        for user in users:
            if self._stop_requested:
                break
            if not _index_date_is_on_or_after(user.modified_at, self.config.start_date):
                users_skipped_by_date += 1
                continue
            if self._user_is_unchanged(user):
                users_skipped_unchanged += 1
                continue

            try:
                summary = self._scan_user(user)
            except Exception as exc:
                users_failed += 1
                self._save_user_record(user, status="failed", error=str(exc))
                continue

            users_scanned += 1
            files_processed += summary.files_processed
            files_skipped_existing_raw += summary.files_skipped_existing_raw
            artifacts_imported += summary.artifacts_imported
            self._save_user_record(
                user,
                status="completed",
                processed_files=summary.files_processed,
                artifact_count=summary.artifacts_imported,
            )

        return CrawlWorkerRunSummary(
            users_seen=len(users),
            users_skipped_by_date=users_skipped_by_date,
            users_skipped_unchanged=users_skipped_unchanged,
            users_scanned=users_scanned,
            users_failed=users_failed,
            files_processed=files_processed,
            files_skipped_existing_raw=files_skipped_existing_raw,
            artifacts_imported=artifacts_imported,
        )

    def _scan_user(self, user: MorgueUser) -> _UserScanSummary:
        self.throttle.wait()
        files = self.list_files(
            user.url,
            timeout=self.config.timeout,
            user_agent=self.config.user_agent,
        )
        selected_files = [
            file
            for file in files
            if _morgue_file_date_is_on_or_after(file.name, self.config.start_date)
        ]

        files_processed = 0
        files_skipped_existing_raw = 0
        artifacts_imported = 0
        for file in selected_files:
            if self._stop_requested:
                break
            if _is_completed_file(self.repository, user.nickname, file.name):
                files_skipped_existing_raw += 1
                continue

            self.throttle.wait()
            try:
                self._ingest_file(user, file)
                self.repository.save_crawl_file_record(
                    CrawlFileRecord(
                        player=user.nickname,
                        name=file.name,
                        url=file.url,
                        status="completed",
                        artifact_count=0,
                        processed_at=_utc_now(),
                        error=None,
                    )
                )
            except Exception as exc:
                self.repository.save_crawl_file_record(
                    CrawlFileRecord(
                        player=user.nickname,
                        name=file.name,
                        url=file.url,
                        status="failed",
                        artifact_count=0,
                        processed_at=_utc_now(),
                        error=str(exc),
                    )
                )
                raise
            files_processed += 1

        return _UserScanSummary(
            files_processed=files_processed,
            files_skipped_existing_raw=files_skipped_existing_raw,
            artifacts_imported=artifacts_imported,
        )

    def _process_pending_raw_files(self) -> CrawlProcessSummary:
        if self.config.process_limit <= 0:
            return CrawlProcessSummary()
        try:
            artifacts_imported = self.process_pending(
                self.repository,
                limit=self.config.process_limit,
            )
        except Exception as exc:
            return CrawlProcessSummary(failed=True, error=str(exc))
        return CrawlProcessSummary(artifacts_imported=artifacts_imported)

    def _ingest_file(self, user: MorgueUser, file: MorgueFile) -> RawMorgueFileRecord:
        try:
            text = self.fetch_file_text(
                file.url,
                timeout=self.config.timeout,
                user_agent=self.config.user_agent,
            )
        except Exception as exc:
            self.repository.save_raw_morgue_file(
                RawMorgueFileRecord.fetch_failed(
                    player=user.nickname,
                    name=file.name,
                    url=file.url,
                    extension=file.extension,
                    error=str(exc),
                )
            )
            raise
        raw_file = RawMorgueFileRecord.fetched(
            player=user.nickname,
            name=file.name,
            url=file.url,
            extension=file.extension,
            text=text,
            fetched_at=_utc_now(),
        )
        self.repository.save_raw_morgue_file(raw_file)
        return raw_file

    def _user_is_unchanged(self, user: MorgueUser) -> bool:
        if self.config.user_skip_mode != USER_SKIP_MODE_MODIFIED_AT:
            return False
        record = self.repository.get_crawl_user_record(user.nickname)
        return (
            record is not None
            and record.status == "completed"
            and record.observed_at == user.modified_at
        )

    def _save_user_record(
        self,
        user: MorgueUser,
        status: str,
        processed_files: int = 0,
        artifact_count: int = 0,
        error: str | None = None,
    ) -> None:
        self.repository.save_crawl_user_record(
            CrawlUserRecord(
                player=user.nickname,
                url=user.url,
                observed_at=user.modified_at,
                status=status,
                scanned_at=_utc_now(),
                processed_files=processed_files,
                artifact_count=artifact_count,
                error=error,
            )
        )

    def _sleep_until_next_pass(self) -> None:
        remaining = self.config.loop_interval_seconds
        while remaining > 0 and not self._stop_requested:
            chunk = min(remaining, 1.0)
            self.sleep(chunk)
            remaining -= chunk


def config_from_env() -> CrawlWorkerConfig:
    """Build worker config from environment variables."""

    return CrawlWorkerConfig(
        base_url=os.environ.get("MORGUE_BASE_URL", DEFAULT_MORGUE_BASE_URL),
        start_date=_date_from_env("CRAWL_START_DATE", DEFAULT_CRAWL_START_DATE),
        request_delay_seconds=_float_from_env(
            "MORGUE_REQUEST_DELAY_SECONDS",
            DEFAULT_REQUEST_DELAY_SECONDS,
        ),
        loop_interval_seconds=_float_from_env(
            "CRAWL_LOOP_INTERVAL_SECONDS",
            DEFAULT_LOOP_INTERVAL_SECONDS,
        ),
        timeout=_float_from_env("MORGUE_REQUEST_TIMEOUT_SECONDS", DEFAULT_TIMEOUT),
        user_agent=os.environ.get("MORGUE_USER_AGENT", DEFAULT_USER_AGENT),
        user_skip_mode=_user_skip_mode_from_env(),
        process_limit=_int_from_env("CRAWL_PROCESS_LIMIT", DEFAULT_PROCESS_LIMIT),
    )


def main() -> None:
    configure_logging()
    worker = CrawlWorker(repository_from_env(), config=config_from_env())
    signal.signal(signal.SIGINT, worker.request_stop)
    signal.signal(signal.SIGTERM, worker.request_stop)
    worker.run_forever()


def _is_completed_file(
    repository: CrawlArtifactRepository,
    nickname: str,
    source_file: str,
) -> bool:
    raw_file = repository.get_raw_morgue_file(nickname, source_file)
    if raw_file is not None:
        return raw_file.fetch_status == FETCH_STATUS_FETCHED
    return False


def _index_date_is_on_or_after(value: str, start_date: date) -> bool:
    try:
        return datetime.strptime(value, MORGUE_INDEX_DATE_FORMAT).date() >= start_date
    except ValueError:
        return False


def _morgue_file_date_is_on_or_after(name: str, start_date: date) -> bool:
    match = MORGUE_FILE_STAMP_RE.match(name)
    if not match:
        return False
    file_date = datetime.strptime(match.group("date"), "%Y%m%d").date()
    return file_date >= start_date


def _date_from_env(name: str, default: date) -> date:
    configured = os.environ.get(name)
    if not configured:
        return default
    return date.fromisoformat(configured)


def _float_from_env(name: str, default: float) -> float:
    configured = os.environ.get(name)
    if not configured:
        return default
    return max(float(configured), 0.0)


def _int_from_env(name: str, default: int) -> int:
    configured = os.environ.get(name)
    if not configured:
        return default
    return max(int(configured), 0)


def _user_skip_mode_from_env() -> str:
    configured = os.environ.get("CRAWL_USER_SKIP_MODE", USER_SKIP_MODE_CONSERVATIVE)
    if configured == USER_SKIP_MODE_MODIFIED_AT:
        return USER_SKIP_MODE_MODIFIED_AT
    return USER_SKIP_MODE_CONSERVATIVE


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


if __name__ == "__main__":
    main()
