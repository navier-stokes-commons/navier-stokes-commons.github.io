# Locale scientific-review receipts

Locale status is evidence-derived. A full-translation locale becomes `scientific-reviewed` only when the current exact locale-content digest has both a passing native-language review and a passing subject-domain review, by two distinct publicly identifiable reviewers, with public review-artifact URLs and no failing receipt for that digest.

Any edit to the locale, mission translation, taxonomy translation, or source translation changes the digest and automatically returns that locale to `full-translation-review-pending` until the new content is reviewed. Old receipts therefore cannot silently certify changed text.

Receipt format: `schemas/locale-review.schema.json`.
