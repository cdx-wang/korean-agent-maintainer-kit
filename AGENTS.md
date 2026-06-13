# Agent Instructions

This repository is an OSS candidate for maintainer workflow evidence tooling.

## Working Rules

- Keep the current release local-first and dry-run. Do not add mandatory API calls.
- Do not commit secrets, account identifiers, tokens, or private local paths.
- Keep Windows, OneDrive, PowerShell, UTF-8, and Korean filename behavior testable.
- Update `작업일지.md` for substantive work.
- Run `python -m unittest discover -s tests` and CLI smoke checks before handoff.

## Human-Touch Gate

Stop for explicit maintainer approval before:

- GitHub publishing or release tagging
- package publishing
- billing or paid services
- auth, token, OAuth, or security setting changes
- destructive git operations

## Completion Evidence

For code changes, record:

- cause or task intent
- reproduction or baseline
- implementation summary
- happy path
- at least three edge checks
- repeat-mistake prevention
