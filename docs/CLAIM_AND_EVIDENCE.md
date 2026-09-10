# Claims and Evidence

`content/public/claims.json` is the seed claim ledger. Claims should be atomic enough that evidence can support, dispute, or supersede them without changing unrelated statements.

A claim record should identify its status, supporting source or contribution IDs, derivation if any, limitations, and predecessor or successor links when revised.

Do not upgrade `derived-unreviewed` to `independently-reviewed` because the derivation is plausible or because an automated test passes. The review record must exist and target the exact claim.
