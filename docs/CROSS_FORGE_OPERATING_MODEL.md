# Cross-forge operating model

## Authority

GitHub `timperelman/navier-stokes-commons-public` remains the canonical source repository because current public project metadata names it as `repository_url`.

GitLab `champia-labs-group/navier-stokes-commons-public` is an exact public mirror and fully valid contribution intake surface.

Forge issues/MRs are collaboration records, not scientific authority. Accepted scientific state lives in reviewed canonical repository data.

## Source mirroring

Every accepted canonical `main` revision must be mirrored fast-forward-only to GitLab `main`.

Algorithm:

1. observe canonical `HEAD = X`;
2. fetch GitLab main `Y`;
3. require `Y` is an ancestor of `X` or equal to it;
4. if not, stop with `GITLAB_DIVERGED_RECONCILIATION_REQUIRED`;
5. push `X -> gitlab/main` without force;
6. verify remote main equals `X`;
7. allow GitLab CI/Pages to deploy the exact mirrored source;
8. terminal release requires both public hosts to expose the same source release identity.

A dedicated write-capable GitLab deploy key/project bot should be used for mirroring; never embed a personal credential in source or prompts.

## Unified intake

Public GitHub and GitLab issues/MRs are periodically read and normalized into a derived intake snapshot.

The intake queue records origin forge and native IDs. It does not silently copy or rewrite native discussions, and it never converts submission into scientific acceptance.

The same derived queue is published on both Pages hosts so the operator does not have to manually monitor two independent inboxes.

## Code originating on GitLab

For a GitLab MR intended to change canonical code/data:

1. fetch exact MR head/base and patch;
2. replay in a clean canonical checkout under an ephemeral scratch directory;
3. run source/provenance/security checks;
4. create a canonical GitHub branch/PR retaining GitLab author/MR provenance;
5. merge only after normal review and gates;
6. mirror the resulting canonical main revision back to GitLab.

This avoids two writable source authorities while allowing either community to originate work.
