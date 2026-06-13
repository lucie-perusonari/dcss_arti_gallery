---
name: git-workflow
description: Enforce repository git hygiene for DCSS artifact gallery work. Use for any git-related request or command in this repository, including git status, diff, log, show, branch creation/rename/switching, fetch, pull, merge, rebase, staging, committing, amending, tagging, pushing, force-pushing, reverting, resetting, cleaning, stash work, PR summaries, release notes from git history, or advice about git commands.
---

# Git Workflow

## Overview

Use this skill before any git-facing action in this repository. If a user asks to inspect, explain, modify, commit, push, pull, sync, or advise on git state, apply this skill first. The goal is to keep branches, commits, and status reporting predictable while protecting user work already present in the worktree.

## Trigger Discipline

- Treat any explicit `git ...` command, branch/commit/push/pull/status/diff/log/stash/reset/revert wording, or PR/release-history request as a git workflow task.
- Before running mutating git commands, check status and identify unrelated or user-owned work.
- For read-only git commands such as `git log`, `git show`, `git diff`, or `git status`, still use this skill so reporting stays consistent.
- If another skill is also relevant, use this skill in addition to that skill; git hygiene does not replace domain-specific routing.

## Required Checks

Before staging, committing, switching branches, rebasing, merging, or deleting branches:

1. Run `git status --short --branch`.
2. Identify which changes were made by Codex in the current task and which changes may belong to the user.
3. Do not stage, commit, revert, move, or delete user-owned changes unless the user explicitly asked for that exact action.
4. Avoid destructive commands such as `git reset --hard`, `git checkout -- <path>`, `git clean`, forced branch deletion, or force push unless the user explicitly requested them.

## Branch Naming

Use this branch name format for new task branches:

```text
<type>/<english-slug>
```

Rules:

- `<type>` is an English commit/work type.
- `<english-slug>` is a short lowercase English phrase that describes the work.
- Prefer lowercase English type names.
- Use hyphens between words in the English slug.
- Keep the branch name concise, ASCII, and shell-safe.
- Follow common git branch naming conventions: lowercase words, no spaces, no trailing slash, and no punctuation unless it is conventional in branch names.

Allowed common types:

- `feature`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `review`

Examples:

```text
feature/artifact-filter
fix/scoring-calculation
docs/service-readme
chore/git-workflow-skill
```

If the user specifies a type, keep it if it is an English work type. If the user provides only a Korean description, choose the narrowest fitting English type and translate the branch slug into concise English.

## Commit Messages

Use this commit subject format:

```text
<type>: <Korean message>
```

Rules:

- `<type>` is English and describes the commit category.
- `<Korean message>` is Korean and describes the actual change.
- Keep the subject concise.
- Do not use vague messages like `update`, `fix`, `changes`, or `작업`.
- Do not include generated-by footers unless the user asks for them.
- When a body is useful, write it in Korean and keep code identifiers, commands, file names, and API fields in their original form.

Examples:

```text
feature: 아티팩트 필터 추가
fix: 점수 계산 오류 수정
docs: 서비스 README 구조 정리
chore: git workflow skill 추가
```

## Staging and Commit Workflow

When the user asks Codex to commit:

1. Inspect `git status --short --branch`.
2. Inspect relevant diffs for files that will be staged.
3. Split commits by logical unit when the work contains separable changes, such as docs updates, parser behavior, API contract changes, UI changes, tests, or tooling.
4. Do not bundle unrelated changes into one commit for convenience.
5. Stage only the files that belong to the current logical commit.
6. Commit with a compliant message.
7. Repeat staging and committing for each logical unit.
8. Report each commit hash and exact subject.

If unrelated user changes are present, mention that they were left untouched.

If the user explicitly asks for a single commit, follow that request while still excluding unrelated user-owned changes.

## Reporting

When reporting git state to the user:

- Mention the current branch.
- Separate staged, unstaged, and untracked changes when relevant.
- Call out unrelated or user-owned changes instead of silently including them in proposed commits.
- Prefer Korean for explanations in this repository, while preserving command output identifiers as written.
