# Worklog

## 2026-06-13 - Initial CLI Scope

### Cause

Agent-assisted OSS maintenance needs durable local evidence without requiring
API keys, hosted services, or private machine context.

### Reproduction

Before this package, a maintainer had to create instruction files, work logs,
verification notes, and human-approval rules manually for each repository.

### Changes

Implemented the local-first `agent-maintainer` CLI with three commands:

- `init` for repository maintainer templates
- `check` for workflow evidence validation
- `evidence` for shareable verification notes

### Verification

- `python -m unittest discover -s tests`
- `python -m agent_maintainer_kit check .`

### Prevention

- The default workflow requires no API keys or hosted services.
- Generated evidence files are ignored by default because they can include machine-specific paths.
- Local agent history is kept outside the public worklog when it contains private task context.

## 2026-06-13 - Pre-Publish Security Review

### Cause

Before publishing the repository publicly, the candidate files needed one more
check for secrets, personal identifiers, private local paths, and generated
cache artifacts.

### Reproduction

The repository is intended to be published from this package directory only.
Parent workspaces can contain unrelated personal files and should not be used as
the Git repository root.

### Changes

No source changes were required. Generated Python bytecode caches were removed
after validation because they can contain machine-specific paths.

### Verification

- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests`
- `PYTHONDONTWRITEBYTECODE=1 python -m agent_maintainer_kit check .`
- Exact-pattern scan for private keys, common API tokens, email addresses,
  Korean phone numbers, resident-number-like strings, and Windows user paths
  found no hits in publishable candidate files.

### Prevention

- Publish only this package directory, not the parent workspace.
- Keep `evidence/`, Python caches, and local agent history out of the public repo.
