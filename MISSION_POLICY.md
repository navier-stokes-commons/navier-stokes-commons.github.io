# Mission and Quest Policy

## Mission

A mission is a durable research program or question. It must contain an ID, open status, exact question, public starting points, acceptance criteria, contributor classes, source links when applicable, and governance status.

A mission may be scientifically difficult or open-ended. Its acceptance criteria define what would count as resolving the mission, not what every contributor must do.

## Quest

A quest is the unit a collaborator should be able to start. It belongs to exactly one mission and must be bounded enough for an independent reviewer to determine whether its acceptance conditions were met.

Every quest requires:

- stable ID;
- parent mission ID;
- status and provenance of creation;
- difficulty/time rung;
- precise task;
- concrete deliverables;
- individually checkable acceptance conditions;
- required review class and competence;
- source IDs when claims depend on sources;
- dependencies, if any;
- claim IDs affected, if any;
- non-exclusive participation rule.

## Non-exclusivity

Starting or "claiming" a quest announces an attempt. It never prevents parallel attempts. Independent duplication is often desirable for verification work.

## Six-rung ladder

The canonical ladder is `content/public/task_ladder.json`, from L0 source or interface checks through L5 open research. Maintainers should preserve a healthy launch distribution, especially L0-L2 entry points and L3-L4 substantive build/research tasks.

## Founding Sprint

The Founding Sprint is a selected cross-section of quests intended to produce early independent evidence while testing the system itself. Its completion is evidence of institutional substance. It is not a prerequisite for publishing the open workspace that allows contributors to undertake it.

## Creating new work

Use:

```bash
python3 scripts/catalog.py validate
python3 scripts/catalog.py next-quest-id
python3 scripts/catalog.py next-mission-id
```

Then use the templates in `templates/` and follow `docs/QUEST_AUTHORING.md` or `docs/MISSION_AUTHORING.md`. Community proposals should normally arrive through the side-quest or mission proposal issue flow before becoming canonical.
