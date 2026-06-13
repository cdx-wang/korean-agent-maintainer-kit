# korean-agent-maintainer-kit

Local-first maintainer workflow guardrails for agent-assisted open-source work.

This project helps maintainers keep repeatable evidence when coding agents make
changes: repo-local instructions, work logs, verification checklists, human-touch
gates, and UTF-8 checks for Windows/Korean workflows.

It does not require an OpenAI API key. The default workflow is dry-run and
local-first so a maintainer can evaluate it at 0 required cost.

## Why This Exists

Agent-assisted maintenance often fails in quiet ways:

- code changes land without a durable worklog
- tests are mentioned in chat but not captured as evidence
- Windows paths, OneDrive folders, and Korean filenames expose encoding bugs
- agents continue through auth, billing, publishing, or destructive actions without
  a clear human approval gate

This kit turns those concerns into files and checks that can be reused across
repositories.

## Install For Local Development

```powershell
python -m pip install -e .
```

## Quickstart

Initialize a repository:

```powershell
agent-maintainer init path\to\repo
```

Check a repository:

```powershell
agent-maintainer check path\to\repo
```

Generate an evidence file:

```powershell
agent-maintainer evidence path\to\repo --task "Add release checklist" --command "agent-maintainer check ."
```

## Commands

### `init`

Creates:

- `AGENTS.md`
- `WORKLOG.md`
- `verification.md`
- `human-touch-policy.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

Use a Korean worklog filename when needed:

```powershell
agent-maintainer init . --worklog-name 작업일지.md
```

### `check`

Checks:

- required maintainer files
- `WORKLOG.md` or `작업일지.md`
- UTF-8 readability for common text files
- possible mojibake or replacement characters
- temporary Korean filename round-trip in the target directory

### `evidence`

Creates `evidence/YYYY-MM-DD-task.md` with:

- task title
- target path
- commands recorded by the maintainer
- check result
- happy path and edge case observations
- human-touch and cost notes

## Cost Boundary

Required cost for the default workflow is 0.

Possible future costs only appear if a maintainer chooses to add API calls,
hosted services, paid CI usage, domains, or third-party integrations.

## Release Scope

The current CLI scope is complete for:

- repository bootstrap files with `init`
- maintainer evidence validation with `check`
- shareable verification markdown with `evidence`

Future expansion candidates include issue triage templates, PR review templates,
reporter adapters, human-touch gate helpers, and expanded dogfooding examples.

## Development Checks

```powershell
python -m unittest discover -s tests
python -m agent_maintainer_kit check .
```
