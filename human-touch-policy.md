# Human-Touch Policy

Agents must stop and ask before actions involving:

- login, account switching, OAuth scopes, or token changes
- billing, paid services, subscriptions, or quota-consuming integrations
- publishing packages, GitHub releases, comments, posts, or messages
- force push, history rewrite, recursive deletion, or irreversible file changes
- scanning or testing repositories and systems without clear authorization

Approval requests should state the action, expected cost if any, rollback path,
and what happens if approval is not granted.
