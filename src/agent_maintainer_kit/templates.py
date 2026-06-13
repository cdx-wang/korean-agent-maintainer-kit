from __future__ import annotations

from textwrap import dedent


def bootstrap_templates(worklog_name: str = "WORKLOG.md") -> dict[str, str]:
    return {
        "AGENTS.md": dedent(
            f"""\
            # Agent Instructions

            This repository allows agent-assisted maintenance, but every non-trivial
            change must leave durable evidence.

            ## Required Flow
            - Start by reading this file, `{worklog_name}`, and `verification.md`.
            - Prefer local-first and dry-run behavior before networked or paid actions.
            - Do not expose secrets, access tokens, private account details, or billing data.
            - Stop for human approval before auth changes, publishing, billing, destructive
              actions, or actions that affect third-party accounts.
            - After code changes, run the relevant checks and record the result.

            ## Completion Contract
            For substantive work, update `{worklog_name}` with:
            - cause or task intent
            - reproduction or baseline observation
            - change summary
            - verification commands and results
            - repeat-mistake prevention notes

            ## Verification Baseline
            Use `agent-maintainer check .` before handing work off.
            Use `agent-maintainer evidence . --task "<task>"` when a shareable evidence
            artifact is useful for review, release, or funding applications.
            """
        ),
        worklog_name: dedent(
            """\
            # Worklog

            ## YYYY-MM-DD - Task Title

            ### Cause or Task Intent
            - 

            ### Reproduction or Baseline
            - 

            ### Change Summary
            - 

            ### Verification
            - Happy path:
            - Edge case 1:
            - Edge case 2:
            - Edge case 3:

            ### Repeat-Mistake Prevention
            - 
            """
        ),
        "verification.md": dedent(
            """\
            # Verification Contract

            Use this file to keep repeatable checks close to the repository.

            ## Standard Commands
            - `agent-maintainer check .`

            ## Expected Evidence
            - The worklog exists and is updated for substantive work.
            - UTF-8 text files can be read without decode errors.
            - Korean filenames and Windows paths are handled safely where relevant.
            - At least one happy path and three edge cases are recorded for risky changes.
            """
        ),
        "human-touch-policy.md": dedent(
            """\
            # Human-Touch Policy

            Agents must stop and ask for human approval before:

            - logging in or switching accounts
            - changing billing, subscriptions, or paid resources
            - publishing releases, packages, posts, comments, or messages
            - deleting, force-pushing, or rewriting durable history
            - changing secrets, tokens, OAuth scopes, or security settings
            - scanning or testing systems the maintainer does not control

            The approval request should include the action, expected cost if any, rollback
            path, and what happens if no approval is granted.
            """
        ),
        "CONTRIBUTING.md": dedent(
            """\
            # Contributing

            Thanks for improving this project.

            ## Before Opening a PR
            - Keep changes local-first unless network access is part of the feature.
            - Add or update verification evidence for behavior changes.
            - Avoid including secrets, private paths, or account identifiers.
            - Run `agent-maintainer check .`.

            ## PR Review Checklist
            - What maintainer workload does this reduce?
            - How can the behavior be reproduced?
            - Which happy path and edge cases were checked?
            - Does the change require human approval, auth, billing, or publishing?
            """
        ),
        "SECURITY.md": dedent(
            """\
            # Security Policy

            Please report security issues privately to the project maintainer.

            Do not include secrets, tokens, private account data, or exploit details in
            public issues. This project is local-first and should not require API keys for
            its default checks.

            Maintainers should confirm repository ownership and authorization before using
            any automated security, scanning, or review workflow.
            """
        ),
    }
