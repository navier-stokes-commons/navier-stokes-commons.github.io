# Public content policy

The deployable repository is intentionally clean-room public material.

## Allowed

- claims directly supported by listed public sources;
- ordinary logical or methodological cautions that do not disclose private history;
- newly formulated open research questions;
- explicit acceptance criteria for those questions;
- reviewed and accepted public contribution manifests;
- public contribution, accessibility, localization, security, and licensing instructions.

## Not allowed

- private or unpublished research history;
- private project names, orchestration records, prompts, or internal research procedures;
- local filesystem paths, host-specific private configuration, credentials, or secrets;
- unpublished personal claims presented as public fact;
- hidden model reasoning;
- copied third-party material beyond what its license or quotation rules permit.

## Release gate

The build validates source references and runs a privacy-leak scan over both source files and generated public pages. The repository stores no private identifier list or fingerprints. Project-specific blocked-identifier hashes, when used for a release audit, are supplied ephemerally through `PUBLIC_RELEASE_PRIVATE_DENY_HASHES` and are not committed or packaged.
