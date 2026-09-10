# Forge projection synchronization

Git repository content is canonical for project state. Forge issues are collaboration surfaces, not independent authorities.

The Founding Sprint index issue is a generated external projection. `scripts/sync_founding_sprint_issue.py` derives its title and body from:

- `content/public/founding_sprint.json`;
- `content/public/quests.json`;
- `content/public/project.json`.

The GitHub workflow `.github/workflows/sync-founding-sprint.yml` reconciles that projection after relevant changes reach `main`. It finds the issue by a machine sentinel embedded in the generated body, not by a hardcoded issue number. If no generated index exists it creates one; if one exists it updates it; if more than one sentinel-bearing index exists it fails closed.

This is intentionally one-way:

`canonical repository state -> generated forge projection`

Editing the generated issue is not a supported way to change the sprint. The next reconciliation replaces manual drift.

Individual quest issues are optional work surfaces and are not canonical copies of the quest catalog. The canonical quest definition remains `content/public/quests.json`; accepted result state remains repository data reviewed through the public contribution protocol.
