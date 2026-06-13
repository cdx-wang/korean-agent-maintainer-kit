from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from typing import Iterable

from .templates import bootstrap_templates

TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}

REQUIRED_FILES = (
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "verification.md",
    "human-touch-policy.md",
)

WORKLOG_CANDIDATES = ("WORKLOG.md", "작업일지.md")
WORKLOG_SIGNALS = {
    "cause": ("Cause", "Intent", "원인", "목적", "요청"),
    "reproduction": ("Reproduction", "Baseline", "재현", "기준"),
    "verification": ("Verification", "검증", "테스트"),
    "prevention": ("Prevention", "반복", "방지", "실수"),
}

MOJIBAKE_PATTERNS = tuple(
    chr(codepoint)
    for codepoint in (
        0xFFFD,  # replacement character
        0x00EC,
        0x00EB,
        0x00EA,
        0x8ADB,
        0x81FE,
        0x5A9B,
        0x5BC3,
        0x6E72,
        0x6028,
    )
)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


@dataclass
class Issue:
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {"message": self.message, "path": self.path}


@dataclass
class CheckResult:
    target: Path
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    checked_files: int = 0
    worklog: Path | None = None

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "target": str(self.target),
            "checked_files": self.checked_files,
            "worklog": str(self.worklog) if self.worklog else None,
            "errors": [issue.as_dict() for issue in self.errors],
            "warnings": [issue.as_dict() for issue in self.warnings],
        }


def normalize_target(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def iter_text_files(target: Path) -> Iterable[Path]:
    for path in target.rglob("*"):
        relative_parts = path.relative_to(target).parts
        if any(part in SKIP_DIRS for part in relative_parts[:-1]):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def detect_mojibake(text: str) -> bool:
    return any(pattern in text for pattern in MOJIBAKE_PATTERNS)


def find_worklog(target: Path) -> Path | None:
    for name in WORKLOG_CANDIDATES:
        candidate = target / name
        if candidate.is_file():
            return candidate
    return None


def validate_worklog_name(worklog_name: str) -> str:
    name = worklog_name.strip()
    candidate = Path(name)
    if not name:
        raise ValueError("Worklog filename cannot be empty.")
    windows_candidate = PureWindowsPath(name)
    if (
        "/" in name
        or "\\" in name
        or candidate.is_absolute()
        or candidate.drive
        or candidate.root
        or windows_candidate.is_absolute()
        or windows_candidate.drive
        or candidate.name != name
    ):
        raise ValueError("Worklog filename must be a single file name, not a path.")
    if name in {".", ".."}:
        raise ValueError("Worklog filename cannot be '.' or '..'.")
    if any(ord(char) < 32 for char in name):
        raise ValueError("Worklog filename cannot contain control characters.")
    if candidate.suffix.lower() != ".md":
        raise ValueError("Worklog filename must use the .md extension.")
    return name


def resolve_output_dir(target: Path, output_dir: str) -> Path:
    value = output_dir.strip()
    candidate = Path(value)
    if not value:
        raise ValueError("Output directory cannot be empty.")
    windows_candidate = PureWindowsPath(value)
    if (
        candidate.is_absolute()
        or candidate.drive
        or candidate.root
        or windows_candidate.is_absolute()
        or windows_candidate.drive
    ):
        raise ValueError("Output directory must be relative to the target repository.")

    resolved = (target / candidate).resolve()
    if not is_relative_to(resolved, target):
        raise ValueError("Output directory must stay inside the target repository.")
    return resolved


def run_fs_smoke(target: Path, result: CheckResult) -> None:
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix="agent-maintainer-한글-",
            suffix=".tmp",
            dir=target,
            delete=False,
        ) as handle:
            smoke_path = Path(handle.name)
            handle.write("utf-8 smoke: 한글 filename and content\n")
        smoke_text = smoke_path.read_text(encoding="utf-8")
        if "한글" not in smoke_text:
            result.errors.append(Issue("UTF-8 smoke file content did not round-trip."))
    except OSError as exc:
        result.errors.append(Issue(f"Could not create Korean filename smoke file: {exc}"))
    finally:
        if "smoke_path" in locals():
            try:
                smoke_path.unlink(missing_ok=True)
            except OSError as exc:
                result.warnings.append(Issue(f"Could not remove smoke file: {exc}", str(smoke_path)))


def check_worklog_signals(worklog: Path, result: CheckResult) -> None:
    try:
        text = worklog.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        result.errors.append(Issue(f"Worklog is not valid UTF-8: {exc}", str(worklog)))
        return

    for label, signals in WORKLOG_SIGNALS.items():
        if not any(signal in text for signal in signals):
            result.warnings.append(
                Issue(f"Worklog does not show a clear {label} section.", str(worklog))
            )


def run_checks(target: Path, fs_smoke: bool = True) -> CheckResult:
    result = CheckResult(target=target)
    if not target.exists():
        result.errors.append(Issue("Target path does not exist.", str(target)))
        return result
    if not target.is_dir():
        result.errors.append(Issue("Target path is not a directory.", str(target)))
        return result

    for name in REQUIRED_FILES:
        required_path = target / name
        if not required_path.exists():
            result.errors.append(Issue(f"Required file is missing: {name}", str(required_path)))
        elif not required_path.is_file():
            result.errors.append(Issue(f"Required path is not a file: {name}", str(required_path)))

    worklog = find_worklog(target)
    result.worklog = worklog
    for name in WORKLOG_CANDIDATES:
        candidate = target / name
        if candidate.exists() and not candidate.is_file():
            result.errors.append(Issue(f"Worklog path is not a file: {name}", str(candidate)))
    if worklog is None:
        result.errors.append(
            Issue(
                "No worklog found. Expected one of: " + ", ".join(WORKLOG_CANDIDATES),
                str(target),
            )
        )
    else:
        check_worklog_signals(worklog, result)

    for path in iter_text_files(target):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            result.errors.append(Issue(f"Text file is not valid UTF-8: {exc}", str(path)))
            continue
        result.checked_files += 1
        if detect_mojibake(text):
            result.warnings.append(Issue("Possible mojibake or replacement characters detected.", str(path)))

    if fs_smoke:
        run_fs_smoke(target, result)

    return result


def format_check_text(result: CheckResult) -> str:
    lines = [
        f"target: {result.target}",
        f"status: {'ok' if result.ok else 'failed'}",
        f"checked_files: {result.checked_files}",
    ]
    if result.worklog:
        lines.append(f"worklog: {result.worklog}")
    if result.errors:
        lines.append("errors:")
        lines.extend(format_issue("  -", issue) for issue in result.errors)
    if result.warnings:
        lines.append("warnings:")
        lines.extend(format_issue("  -", issue) for issue in result.warnings)
    return "\n".join(lines)


def format_issue(prefix: str, issue: Issue) -> str:
    if issue.path:
        return f"{prefix} {issue.message} ({issue.path})"
    return f"{prefix} {issue.message}"


def safe_slug(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9가-힣._-]+", "-", lowered)
    lowered = lowered.strip("-._")
    return lowered[:60] or "maintenance-evidence"


def render_evidence(
    target: Path,
    task: str,
    commands: list[str],
    edges: list[str],
    result: CheckResult,
) -> str:
    today = dt.date.today().isoformat()
    status = "pass" if result.ok else "needs attention"
    command_lines = "\n".join(f"- `{command}`" for command in commands) or "- Not recorded."
    edge_lines = "\n".join(f"- {edge}" for edge in edges) or "\n".join(
        [
            "- Happy path: `agent-maintainer check .` can inspect the repository.",
            "- Edge case 1: missing required documentation is reported as an error.",
            "- Edge case 2: UTF-8 decode failures are reported as errors.",
            "- Edge case 3: Korean filename smoke test can be created and removed.",
        ]
    )
    error_lines = "\n".join(format_issue("-", issue) for issue in result.errors) or "- None."
    warning_lines = "\n".join(format_issue("-", issue) for issue in result.warnings) or "- None."
    worklog_line = f"`{result.worklog}`" if result.worklog else "None found."

    return (
        f"# Maintenance Evidence: {task}\n\n"
        f"- Date: {today}\n"
        f"- Target: `{target}`\n"
        f"- Check status: {status}\n"
        f"- Checked text files: {result.checked_files}\n"
        f"- Worklog: {worklog_line}\n\n"
        "## Commands\n"
        f"{command_lines}\n\n"
        "## Verification Coverage\n"
        f"{edge_lines}\n\n"
        "## Errors\n"
        f"{error_lines}\n\n"
        "## Warnings\n"
        f"{warning_lines}\n\n"
        "## Human-Touch And Cost Notes\n"
        "- No OpenAI API call is required for this evidence file.\n"
        "- Stop for human approval before auth, billing, publishing, destructive actions, or secret changes.\n"
        "- Record any paid dependency before enabling it; the default workflow is designed to run at 0 required cost.\n"
    )


def write_bootstrap_files(target: Path, worklog_name: str, force: bool) -> list[Path]:
    worklog_name = validate_worklog_name(worklog_name)
    if target.exists() and not target.is_dir():
        raise ValueError("Target path exists but is not a directory.")
    target.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for relative, content in bootstrap_templates(worklog_name).items():
        path = target / relative
        if path.exists() and not force:
            continue
        path.write_text(content, encoding="utf-8", newline="\n")
        created.append(path)
    return created


def cmd_init(args: argparse.Namespace) -> int:
    target = normalize_target(args.target)
    try:
        created = write_bootstrap_files(target, args.worklog_name, args.force)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if created:
        print("created:")
        for path in created:
            print(f"  - {path}")
    else:
        print("nothing created; files already exist. Use --force to overwrite templates.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    target = normalize_target(args.target)
    result = run_checks(target, fs_smoke=not args.no_fs_smoke)
    if args.format == "json":
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_check_text(result))
    return 0 if result.ok else 1


def cmd_evidence(args: argparse.Namespace) -> int:
    target = normalize_target(args.target)
    result = run_checks(target, fs_smoke=not args.no_fs_smoke)
    content = render_evidence(target, args.task, args.command, args.edge, result)
    if not target.exists() or not target.is_dir():
        print(format_check_text(result), file=sys.stderr)
        return 1
    if args.dry_run:
        print(content)
        return 0 if result.ok else 1

    try:
        output_dir = resolve_output_dir(target, args.output_dir)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = safe_slug(args.task)
    output_path = output_dir / f"{dt.date.today().isoformat()}-{slug}.md"
    if output_path.exists():
        stamp = dt.datetime.now().strftime("%H%M%S")
        output_path = output_dir / f"{dt.date.today().isoformat()}-{slug}-{stamp}.md"
    output_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"evidence: {output_path}")
    return 0 if result.ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-maintainer",
        description="Local-first maintainer workflow guardrails for agent-assisted OSS work.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create maintainer workflow templates.")
    init_parser.add_argument("target", nargs="?", default=".", help="Repository path to initialize.")
    init_parser.add_argument("--worklog-name", default="WORKLOG.md", help="Worklog filename to create.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing template files.")
    init_parser.set_defaults(func=cmd_init)

    check_parser = subparsers.add_parser("check", help="Check maintainer workflow evidence.")
    check_parser.add_argument("target", nargs="?", default=".", help="Repository path to check.")
    check_parser.add_argument("--no-fs-smoke", action="store_true", help="Skip temporary Korean filename smoke test.")
    check_parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    check_parser.set_defaults(func=cmd_check)

    evidence_parser = subparsers.add_parser("evidence", help="Generate a shareable maintenance evidence file.")
    evidence_parser.add_argument("target", nargs="?", default=".", help="Repository path to inspect.")
    evidence_parser.add_argument("--task", required=True, help="Task title for the evidence file.")
    evidence_parser.add_argument("--command", action="append", default=[], help="Verification command to record.")
    evidence_parser.add_argument("--edge", action="append", default=[], help="Happy path or edge case observation.")
    evidence_parser.add_argument("--output-dir", default="evidence", help="Directory for generated evidence.")
    evidence_parser.add_argument("--dry-run", action="store_true", help="Print evidence without writing a file.")
    evidence_parser.add_argument("--no-fs-smoke", action="store_true", help="Skip temporary Korean filename smoke test.")
    evidence_parser.set_defaults(func=cmd_evidence)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
