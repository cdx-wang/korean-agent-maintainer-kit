from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_maintainer_kit.cli import main, run_checks


class CliTests(unittest.TestCase):
    def run_cli(self, args: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_init_creates_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, _ = self.run_cli(["init", tmp, "--worklog-name", "작업일지.md"])
            self.assertEqual(code, 0)
            target = Path(tmp)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / "작업일지.md").exists())
            self.assertTrue((target / "verification.md").exists())
            self.assertTrue((target / "human-touch-policy.md").exists())

    def test_init_does_not_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.run_cli(["init", tmp])
            agents = target / "AGENTS.md"
            agents.write_text("custom\n", encoding="utf-8")
            self.run_cli(["init", tmp])
            self.assertEqual(agents.read_text(encoding="utf-8"), "custom\n")
            self.run_cli(["init", tmp, "--force"])
            self.assertIn("Agent Instructions", agents.read_text(encoding="utf-8"))

    def test_check_passes_after_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(["init", tmp])
            result = run_checks(Path(tmp))
            self.assertTrue(result.ok, result.as_dict())

    def test_check_fails_when_required_files_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_checks(Path(tmp), fs_smoke=False)
            self.assertFalse(result.ok)
            self.assertGreaterEqual(len(result.errors), 1)

    def test_check_fails_invalid_utf8_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(["init", tmp])
            bad = Path(tmp) / "bad.md"
            bad.write_bytes(b"\xff\xfe\xfa")
            result = run_checks(Path(tmp), fs_smoke=False)
            self.assertFalse(result.ok)
            self.assertTrue(any("UTF-8" in issue.message for issue in result.errors))

    def test_evidence_dry_run_prints_markdown_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(["init", tmp])
            code, stdout, _ = self.run_cli(["evidence", tmp, "--task", "Smoke Test", "--dry-run"])
            self.assertEqual(code, 0)
            self.assertIn("# Maintenance Evidence: Smoke Test", stdout)
            self.assertFalse((Path(tmp) / "evidence").exists())

    def test_evidence_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(["init", tmp])
            code, _, _ = self.run_cli(["evidence", tmp, "--task", "Smoke Test"])
            self.assertEqual(code, 0)
            evidence_files = list((Path(tmp) / "evidence").glob("*.md"))
            self.assertEqual(len(evidence_files), 1)
            self.assertIn("Smoke Test", evidence_files[0].read_text(encoding="utf-8"))

    def test_init_rejects_worklog_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            outside = root / "outside.md"
            code, _, stderr = self.run_cli(["init", str(repo), "--worklog-name", "../outside.md"])
            self.assertEqual(code, 1)
            self.assertIn("single file name", stderr)
            self.assertFalse(outside.exists())
            self.assertFalse(repo.exists())

    def test_init_rejects_existing_file_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "repo-file"
            target.write_text("not a directory\n", encoding="utf-8")
            code, _, stderr = self.run_cli(["init", str(target)])
            self.assertEqual(code, 1)
            self.assertIn("not a directory", stderr)

    def test_check_does_not_skip_when_parent_directory_is_named_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "build" / "repo"
            self.run_cli(["init", str(target)])
            result = run_checks(target, fs_smoke=False)
            self.assertTrue(result.ok, result.as_dict())
            self.assertGreaterEqual(result.checked_files, 6)

    def test_check_fails_when_required_path_is_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.run_cli(["init", tmp])
            (target / "AGENTS.md").unlink()
            (target / "AGENTS.md").mkdir()
            result = run_checks(target, fs_smoke=False)
            self.assertFalse(result.ok)
            self.assertTrue(any("not a file" in issue.message for issue in result.errors))

    def test_check_fails_when_worklog_path_is_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.run_cli(["init", tmp])
            (target / "WORKLOG.md").unlink()
            (target / "WORKLOG.md").mkdir()
            result = run_checks(target, fs_smoke=False)
            self.assertFalse(result.ok)
            self.assertTrue(any("Worklog path is not a file" in issue.message for issue in result.errors))

    def test_evidence_rejects_output_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "repo"
            outside = root / "outside"
            self.run_cli(["init", str(target)])
            code, _, stderr = self.run_cli(
                ["evidence", str(target), "--task", "Escape", "--output-dir", "../outside"]
            )
            self.assertEqual(code, 1)
            self.assertIn("inside the target", stderr)
            self.assertFalse(outside.exists())

    def test_evidence_missing_target_does_not_create_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "missing"
            code, _, stderr = self.run_cli(["evidence", str(target), "--task", "Missing"])
            self.assertEqual(code, 1)
            self.assertIn("Target path does not exist", stderr)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
