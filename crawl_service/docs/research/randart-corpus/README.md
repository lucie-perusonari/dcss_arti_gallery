# DCSS Randart 코퍼스

실제 DCSS public morgue archive에서 수집한 랜덤 아티팩트(randart) 평가 연구용 자료입니다.
이 폴더의 문서와 JSON은 연구/재현용 산출물이며, 규격 문서는 `../../reference/`의 Reference 항목을 우선합니다.

## 파일

- `corpus.json`: 수집된 artifact 문서, source file metadata, raw text block, parser/evaluator 결과.
- `report.md`: corpus 점수 분포, 등급 분포, 주요 속성, 상위 점수 artifact 요약.
- `luxury_classification.md`: corpus를 커뮤니티식 `명품`/`돌품명품` 관점으로 재분류한 메모.
- `community_luxury_examples.md`: Reddit과 공개 morgue에서 확인한 `돌품명품`급 randart 참고 사례.
- `reddit_randart_language.md`: 영어권 DCSS 커뮤니티에서 좋은 randart를 표현하는 방식과 사례 메모.

## 재생성

```sh
python3 scripts/collect_randart_corpus.py
```

기본 실행은 `crawl_service/docs/research/randart-corpus/corpus.json`과
`crawl_service/docs/research/randart-corpus/report.md`를 갱신합니다.
MongoDB에는 쓰지 않고 `crawl_service.processor.artifact_documents_from_raw_text`를 사용해 문서형 스냅샷만 생성합니다.
