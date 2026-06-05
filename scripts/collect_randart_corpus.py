"""Collect a research corpus of real DCSS randarts into crawl_service/docs/ko/research/randart-corpus/.

This script intentionally uses the crawl_service parser/evaluator stack but does
not write MongoDB. It fetches recent public morgue files, extracts random
artifact documents, and writes a reproducible JSON corpus plus a compact report.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crawl_service.morgue.fetcher import (  # noqa: E402
    DEFAULT_USER_AGENT,
    build_morgue_raw_texts,
    fetch_morgue_files,
    fetch_morgue_users,
    select_recent_morgue_files,
)
from crawl_service.processor import artifact_documents_from_raw_text  # noqa: E402
from crawl_service.worker import DEFAULT_MORGUE_BASE_URL  # noqa: E402


DEFAULT_CORPUS_DIR = ROOT / "crawl_service" / "docs" / "research" / "randart-corpus"
DEFAULT_JSON_OUTPUT = DEFAULT_CORPUS_DIR / "corpus.json"
DEFAULT_REPORT_OUTPUT = DEFAULT_CORPUS_DIR / "report.md"
INDEX_DATE_FORMAT = "%Y-%b-%d %H:%M"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch real DCSS morgue randarts and save a docs corpus."
    )
    parser.add_argument("--base-url", default=DEFAULT_MORGUE_BASE_URL)
    parser.add_argument("--target-artifacts", type=int, default=150)
    parser.add_argument("--max-users", type=int, default=40)
    parser.add_argument("--files-per-user", type=int, default=8)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    args = parser.parse_args()

    started_at = datetime.now().astimezone()
    users = _recent_users(
        fetch_morgue_users(
            args.base_url,
            timeout=args.timeout,
            user_agent=DEFAULT_USER_AGENT,
        )
    )

    documents_by_id: dict[str, dict[str, Any]] = {}
    source_files: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for user in users[: args.max_users]:
        if len(documents_by_id) >= args.target_artifacts:
            break
        try:
            files = select_recent_morgue_files(
                fetch_morgue_files(
                    _user_morgue_url(args.base_url, user.nickname),
                    timeout=args.timeout,
                    user_agent=DEFAULT_USER_AGENT,
                ),
                args.files_per_user,
            )
            raw_texts = build_morgue_raw_texts(
                files,
                timeout=args.timeout,
                user_agent=DEFAULT_USER_AGENT,
                delay=args.delay,
            )
        except Exception as exc:  # network archives can have transient misses
            failures.append({"player": user.nickname, "error": str(exc)})
            continue

        for raw_text in raw_texts:
            try:
                documents = artifact_documents_from_raw_text(raw_text)
            except Exception as exc:
                failures.append(
                    {
                        "player": user.nickname,
                        "file": raw_text.name,
                        "error": str(exc),
                    }
                )
                continue

            source_files.append(
                {
                    "player": user.nickname,
                    "file": raw_text.name,
                    "url": raw_text.url,
                    "extension": raw_text.extension,
                    "artifact_count": len(documents),
                }
            )
            for document in documents:
                documents_by_id.setdefault(document.id, document.to_dict())
                if len(documents_by_id) >= args.target_artifacts:
                    break
            if len(documents_by_id) >= args.target_artifacts:
                break
        time.sleep(args.delay)

    documents = sorted(
        documents_by_id.values(),
        key=lambda document: (
            document["evaluation"]["total"],
            document["evaluation"]["offense"],
            document["name"].casefold(),
        ),
        reverse=True,
    )
    finished_at = datetime.now().astimezone()
    corpus = {
        "metadata": {
            "purpose": "Research corpus for evaluating real DCSS random artifact scoring.",
            "base_url": args.base_url,
            "collected_at": finished_at.isoformat(),
            "started_at": started_at.isoformat(),
            "target_artifacts": args.target_artifacts,
            "max_users": args.max_users,
            "files_per_user": args.files_per_user,
            "source_file_count": len(source_files),
            "artifact_count": len(documents),
            "failure_count": len(failures),
            "parser": "crawl_service.processor.artifact_documents_from_raw_text",
        },
        "source_files": source_files,
        "failures": failures,
        "artifacts": documents,
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(corpus, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(
        _report(corpus),
        encoding="utf-8",
    )
    print(
        f"Wrote {len(documents)} artifacts from {len(source_files)} source files "
        f"to {args.json_output} and {args.report_output}"
    )


def _recent_users(users: list[Any]) -> list[Any]:
    return sorted(users, key=lambda user: _index_datetime(user.modified_at), reverse=True)


def _user_morgue_url(base_url: str, nickname: str) -> str:
    return f"{base_url.rstrip('/')}/{urllib.parse.quote(nickname)}/"


def _index_datetime(value: str) -> datetime:
    try:
        return datetime.strptime(value, INDEX_DATE_FORMAT)
    except ValueError:
        return datetime.min


def _report(corpus: dict[str, Any]) -> str:
    artifacts = corpus["artifacts"]
    metadata = corpus["metadata"]
    by_grade = Counter(artifact["evaluation"]["grade"] for artifact in artifacts)
    by_class = Counter(artifact["item_class"] for artifact in artifacts)
    by_base = Counter(artifact["base_item"] for artifact in artifacts)
    by_attribute = Counter(
        attribute
        for artifact in artifacts
        for attribute in artifact["random_attributes"]
    )
    scores = [artifact["evaluation"]["total"] for artifact in artifacts]
    grade_lines = _counter_table(by_grade)
    class_lines = _counter_table(by_class)
    base_lines = _counter_table(by_base, limit=15)
    attr_lines = _counter_table(by_attribute, limit=25)
    top_lines = "\n".join(
        _artifact_line(artifact, index)
        for index, artifact in enumerate(artifacts[:20], start=1)
    )

    return f"""# DCSS Randart Corpus Report

실제 DCSS public morgue archive에서 수집한 randart 평가 연구용 표본입니다.

## Collection

| Field | Value |
| --- | --- |
| Collected at | `{metadata["collected_at"]}` |
| Source base | `{metadata["base_url"]}` |
| Source files | {metadata["source_file_count"]} |
| Artifacts | {metadata["artifact_count"]} |
| Failures | {metadata["failure_count"]} |
| Parser | `{metadata["parser"]}` |

## Score Summary

| Metric | Value |
| --- | ---: |
| Max | {_safe_max(scores)} |
| Min | {_safe_min(scores)} |
| Average | {_safe_average(scores):.1f} |

## Grades

{grade_lines}

## Item Classes

{class_lines}

## Common Base Items

{base_lines}

## Common Random Attributes

{attr_lines}

## Top Scored Artifacts

{top_lines}

## Notes

- 이 corpus는 MongoDB에 저장하지 않은 문서형 스냅샷입니다.
- 점수는 현재 `crawl_service.domain.evaluation.evaluator` 기준입니다.
- `base_attributes`는 제외하고 `random_attributes` 중심으로 평가한 결과입니다.
- 원문 블록과 source URL은 `crawl_service/docs/ko/research/randart-corpus/corpus.json`의 각 artifact에 포함되어 있습니다.
"""


def _counter_table(counter: Counter[str], limit: int | None = None) -> str:
    rows = counter.most_common(limit)
    if not rows:
        return "_No data._"
    lines = ["| Value | Count |", "| --- | ---: |"]
    lines.extend(f"| `{value}` | {count} |" for value, count in rows)
    return "\n".join(lines)


def _artifact_line(artifact: dict[str, Any], index: int) -> str:
    score = artifact["evaluation"]["total"]
    grade = artifact["evaluation"]["grade"]
    attrs = artifact["random_attribute_text"] or "-"
    source = artifact["source"]
    return (
        f"{index}. **{score} {grade}** `{artifact['name']}` "
        f"({artifact['item_class']}, {artifact['base_item']}) - {attrs} "
        f"[{source['player']} / {source['file']}:{source['line']}]({source['url']})"
    )


def _safe_max(values: list[int]) -> int:
    return max(values) if values else 0


def _safe_min(values: list[int]) -> int:
    return min(values) if values else 0


def _safe_average(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
