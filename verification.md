# Verification Contract

## Standard Commands

```powershell
python -m unittest discover -s tests
python -m agent_maintainer_kit check .
python -m agent_maintainer_kit evidence . --task "CLI smoke" --command "python -m unittest discover -s tests" --dry-run
```

## Required Coverage

- Happy path: initialized repository passes `check`.
- Edge case 1: missing required files fail `check`.
- Edge case 2: invalid UTF-8 text files fail `check`.
- Edge case 3: Korean filename smoke test can create/read/remove a temp file.
- Edge case 4: `init` does not overwrite existing files unless `--force` is used.
