"""One-shot morgue archive worker."""

from __future__ import annotations

import os
import re
import time
from datetime import UTC, date, datetime

from crawl_service.fetcher import (
    fetch_morgue_file_text,
    fetch_morgue_files,
    fetch_morgue_users,
)
from crawl_service.fetcher import MorgueFile, MorgueUser
from crawl_service.repository import (
    CrawlErrorRecord,
    MongoCrawlRepository,
    RawMorgueFileRecord,
    create_mongo_crawl_repository,
)


DEFAULT_MORGUE_BASE_URL = "https://archive.nemelex.cards/morgue"
DEFAULT_CRAWL_START_DATE = date(2026, 1, 1)
DEFAULT_REQUEST_DELAY_SECONDS = 1.0
MORGUE_FILE_STAMP_RE = re.compile(
    r"^\.?morgue-(?P<player>.+?)-(?P<date>\d{8})-\d{6}\.(?P<ext>txt|lst)$"
)


class CrawlWorker:
    """Ingests changed morgue files into raw storage."""

    def __init__(
        self,
        repository: MongoCrawlRepository,
        base_url: str = DEFAULT_MORGUE_BASE_URL,
    ) -> None:
        self.repository = repository
        self.base_url = base_url

    def run_once(self) -> None:
        time.sleep(DEFAULT_REQUEST_DELAY_SECONDS)
        users = fetch_morgue_users(self.base_url)

        for user in users:
            error_recorded = False
            try:
                time.sleep(DEFAULT_REQUEST_DELAY_SECONDS)
                files = fetch_morgue_files(user.url)
                candidate_files = [
                    file
                    for file in files
                    if _morgue_file_date_is_on_or_after(
                        file.name,
                        DEFAULT_CRAWL_START_DATE,
                    )
                ]
                source_files = [file.name for file in candidate_files]
                raw_file_records = (
                    self.repository.list_raw_morgue_file_records_for_files(source_files)
                    if source_files
                    else {}
                )
                files_to_fetch = [
                    file
                    for file in candidate_files
                    if file.name not in raw_file_records
                ]

                for file in files_to_fetch:
                    time.sleep(DEFAULT_REQUEST_DELAY_SECONDS)
                    try:
                        text = fetch_morgue_file_text(file.url)
                    except Exception as exc:
                        self.repository.save_crawl_error_record(
                            _crawl_error_record(
                                user,
                                stage="fetch_file",
                                error=exc,
                                file=file,
                            )
                        )
                        error_recorded = True
                        raise

                    self.repository.save_raw_morgue_file(
                        RawMorgueFileRecord(
                            player=user.nickname,
                            name=file.name,
                            url=file.url,
                            extension=file.extension,
                            text=text,
                            fetched_at=_utc_now(),
                        )
                    )
            except Exception as exc:
                if not error_recorded:
                    self.repository.save_crawl_error_record(
                        _crawl_error_record(
                            user,
                            stage="fetch_user_directory",
                            error=exc,
                        )
                    )
                continue


def main() -> None:
    repository = create_mongo_crawl_repository()
    try:
        CrawlWorker(
            repository,
            base_url=os.environ.get("MORGUE_BASE_URL", DEFAULT_MORGUE_BASE_URL),
        ).run_once()
    finally:
        repository.close()


def _crawl_error_record(
    user: MorgueUser,
    stage: str,
    error: Exception,
    file: MorgueFile | None = None,
) -> CrawlErrorRecord:
    return CrawlErrorRecord(
        player=user.nickname,
        name=file.name if file else None,
        url=file.url if file else None,
        extension=file.extension if file else None,
        stage=stage,
        message=str(error),
        error_type=type(error).__name__,
        user_url=user.url,
        occurred_at=_utc_now(),
    )


def _morgue_file_date_is_on_or_after(name: str, start_date: date) -> bool:
    match = MORGUE_FILE_STAMP_RE.match(name)
    if not match:
        return False
    file_date = datetime.strptime(match.group("date"), "%Y%m%d").date()
    return file_date >= start_date


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


if __name__ == "__main__":
    main()
