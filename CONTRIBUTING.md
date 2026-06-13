# Contributing

Thanks for improving this project.

## Local Checks

```powershell
python -m unittest discover -s tests
python -m agent_maintainer_kit check .
```

## Pull Request Expectations

- Explain the maintainer workload being reduced.
- Keep default behavior local-first and free to run.
- Add or update tests for behavior changes.
- Capture verification evidence for non-trivial changes.
- Do not include secrets, private account data, or private machine paths.
