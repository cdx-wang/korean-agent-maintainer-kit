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

## Cursor Cloud specific instructions

- Pure-Python CLI with zero runtime dependencies (`pyproject.toml` `dependencies = []`), targeting Python 3.10+. The VM has Python 3.12.
- The startup update script installs the package editable (`python3 -m pip install -e . --break-system-packages`), so `src/` edits are picked up immediately without reinstalling. Reinstall only when packaging metadata in `pyproject.toml` changes.
- The `agent-maintainer` console script lands in `~/.local/bin` (added to PATH in `~/.bashrc`). If PATH is not loaded in a given shell, use the equivalent module form `python3 -m agent_maintainer_kit ...`.
- Standard lint/test/build/run commands are already documented in `README.md`, `verification.md`, `CONTRIBUTING.md`, and `.github/workflows/ci.yml`. There is no separate linter configured; the repo's own `check` command is the validation gate.
- CI equivalent: `python -m unittest discover -s tests` then `python -m agent_maintainer_kit check . --no-fs-smoke`. The `--no-fs-smoke` flag skips the temporary Korean-filename round-trip test; drop it locally to also exercise UTF-8/Korean filesystem behavior.
