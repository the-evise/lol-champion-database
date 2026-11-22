# Research status and development path

The present database supports roster browsing, narrative keyword exploration, coarse gameplay clustering, and position-based candidate filtering. It is not yet a final evidence base for a validated personality quiz or an advanced playstyle recommender.

## Current evidence boundary

All 173 short biographies have original summaries. All 173 full biographies are available at linked sources, but have not been read and annotated in full for this editorial pass. The 200 unique linked stories are a catalog, not 200 completed story analyses. Every record makes these distinctions machine-readable.

Themes and motivations are interpretations. They must never be shown as Riot-authored labels, clinical diagnoses, or scientifically validated personality measurements. Similarity to a villain's narrative theme need not imply endorsement of their behavior.

## Next annotation passes

| Pass | Proposed fields | Evidence requirement |
|---|---|---|
| Full biography | Major life events, formative experiences, choices, competing goals | Original paraphrases with exact source URLs and paragraph anchors/locators |
| Linked stories | Story-specific behavior, changes over time, contradictions | Read each story once; associate evidence with every featured character |
| Relationships | Family, allies, rivals, mentors; reciprocal and one-sided views | Explicit narrative evidence; curated related links alone are insufficient |
| Character dimensions | Autonomy, belonging, duty, novelty, recognition, compassion, risk, conflict response | Multiple behavioral examples; confidence and counterevidence, not just keywords |
| Gameplay mechanics | Engage, disengage, poke, peel, sustain, burst, DPS, targeting, combos, resource demands | Verified current abilities, including transformations and edge cases |
| Playstyle demands | Spacing, tempo, execution, map attention, farming, team dependence, tolerance for mistakes | Explicit analytical rubric and human review; no class-only assumptions |
| Position suitability | Main/off-role labels, patch, population, sample size | Current role-specific evidence; client roles are only an initial pool |
| Quiz model | Question dimensions, weights, uncertainty, explanations | Separate design and evaluation; do not derive morality from gameplay class |

Record supporting and contradicting evidence. Never infer a personality solely from weapon choice, gender, species, class, or role.

For gameplay, let players express preferences and constraints separately. A player may enjoy mobility while wanting low execution difficulty. Later selection of three champions in each role should apply role eligibility first, then preference matching, and should explain tradeoffs instead of silently returning the three strongest in a patch.

## Source changes

A later source can revise a champion without updating every older story. Preserve a previous snapshot in git, identify which input changed, and explicitly decide whether the interpretation still holds. The current pipeline marks changed short-biography summaries as needing review. It records full-biography hashes too, so a later deep-reading pass can introduce its own review pins.

The Jarvan dossier carries a source-staleness question because its retrieved profile describes a prince/heir. This is retained as source evidence rather than silently promoted to a claim about the latest narrative status. Amumu and Rammus retain uncertainty about their origins.
