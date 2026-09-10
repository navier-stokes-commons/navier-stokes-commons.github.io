# Maintainer Quickstart

## Add or change public work

1. Edit canonical data under `content/public/`, never generated HTML.
2. Validate catalogs with `python3 scripts/catalog.py validate`.
3. Build with `python3 scripts/build_site.py`.
4. Run `python3 scripts/run_all_checks.py`.
5. Run `python3 scripts/release_gate.py --class open-beta` before a public release.
6. Commit source and generated output according to the repository's deployment policy.

## Accept a result

1. Confirm the submission targets a valid quest or mission.
2. Confirm the exact artifact and version are immutable or sufficiently pinned.
3. Check every acceptance condition.
4. Obtain the review class and independence required by the quest.
5. Record accepted contribution and review objects in canonical public data.
6. Rebuild, run all gates, and merge.

## Correct an accepted record

Do not silently overwrite scientific history. Add a superseding or dispute record, link predecessor/successor IDs, rebuild, and preserve the earlier record in version control.
