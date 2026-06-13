# Windows/Korean Workflow Example

This example shows the intended use pattern without exposing private local paths.

Scenario:

- A maintainer uses an agent in a Windows + OneDrive workspace.
- The repository requires durable work logs, verification commands, and human-touch
  gates for auth, billing, publishing, and destructive actions.
- The maintainer runs `agent-maintainer check .` before handoff.
- The maintainer creates a sanitized evidence file for review or funding
  applications.

Relevant current commands:

```powershell
agent-maintainer init . --worklog-name 작업일지.md
agent-maintainer check .
agent-maintainer evidence . --task "Initial CLI smoke" --dry-run
```
