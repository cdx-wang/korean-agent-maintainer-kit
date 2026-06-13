# Maintenance Evidence: Initial CLI Smoke

- Date: 2026-06-13
- Target: `<repo-root>`
- Check status: pass
- Checked text files: 14
- Worklog: `<repo-root>/작업일지.md`

## Commands

- `python -m unittest discover -s tests`
- `python -m agent_maintainer_kit check .`
- `python -m agent_maintainer_kit evidence . --task "Initial CLI smoke" --dry-run`

## Verification Coverage

- Happy path: initialized repository passes `check`.
- Edge case 1: missing required documentation is reported as an error.
- Edge case 2: invalid UTF-8 text files are reported as errors.
- Edge case 3: Korean filename smoke test can create, read, and remove a temp file.
- Edge case 4: `init` preserves existing files unless `--force` is used.

## Errors

- None.

## Warnings

- None.

## Human-Touch And Cost Notes

- No OpenAI API call is required for this evidence file.
- Stop for human approval before auth, billing, publishing, destructive actions, or secret changes.
- The default workflow is designed to run at 0 required cost.
