# Open Tasks

The course site is built. The tasks below need a decision by the instructors, an external service, or a check by a person.

## Owner Labels

| Label      | Meaning                                                                       |
| ---------- | ----------------------------------------------------------------------------- |
| `[Agent]`  | A coding agent can do this directly in the repository.                        |
| `[Shared]` | An agent can prepare the work, but a maintainer approves the external action. |
| `[Manual]` | Complete this in GitHub, Zenodo, or another external service.                 |

## Approve the Proposed Content

- [ ] `[Manual]` Approve the proposed timetable in `contents/_timetable.qmd`. Then set `detailed_program_status: approved` in `data/editions.yml`.
- [ ] `[Manual]` Approve the four documented cases: BLOOM, LAION-5B, Sama and OpenAI, and the Llama 2 license.
- [ ] `[Manual]` Approve the eight-hour preparation plan in `contents/assignments.qmd`.
- [ ] `[Manual]` Confirm the follow-up task, the rubric, the submission channel, and the deadline with GRACE. Then set `assessment_deadline` and remove the "proposed" labels.
- [ ] `[Manual]` Read the lens pages and the decks for accuracy and tone. Laura Wagner and Moritz Mähr both sign off.

## HS 2026 Operations

These tasks hold no participant data. Keep all participant data outside this repository.

- [ ] `[Manual]` By 21 October 2026: send the registered participants the course message with a link to the HS 2026 page. Copy grace@unibas.ch.
- [ ] `[Manual]` Before 4 November 2026: arrange the welcome with GRACE. Print the handouts and one large Panarchy chart.
- [ ] `[Manual]` On 4 November 2026: record attendance privately, and keep the last ten minutes for the evaluation.
- [ ] `[Manual]` After the course day: return the attendance table to GRACE. After the deadline, return the completion table. Arrange the certificates.
- [ ] `[Agent]` After 4 November 2026: set `hs2026.status: delivered` and decide on `featured_edition`.

## FS 2027

- [ ] `[Manual]` Request the confirmed schedule, venue, course link, rules, evaluation link, and deadline from GRACE.
- [ ] `[Agent]` Enter only confirmed facts in `data/editions.yml`. Keep `null` for the rest.

## Materials

- [ ] `[Shared]` Check the six decks for legibility and accessibility. Then offer PDF versions.
- [ ] `[Agent]` Run veraPDF on the handouts (`quarto install verapdf`) to validate PDF/UA-1.
- [ ] `[Shared]` Decide whether to self-host the IBM Plex fonts instead of loading them from Google Fonts.

## GitHub and Zenodo

- [x] `[Manual]` Enable GitHub Pages with the source **GitHub Actions**.
- [x] `[Shared]` Enable Dependabot alerts and security updates, secret scanning, and push protection.
- [ ] `[Shared]` Protect the `main` branch. For one maintainer: require a pull request and passing checks, 0 approvals.
- [ ] `[Shared]` Enable CodeQL default setup for GitHub Actions.
- [ ] `[Manual]` Enable the Zenodo-GitHub integration. Add the DOI badge and a `doi` key to `CITATION.cff` after the first release. Do not invent a DOI.
- [ ] `[Agent]` Remove the exclusion for `https://maehr.github.io/stochastic-parrots-and-beyond` from `.lycheerc.toml` after the first deployment.

## Validation

Run these commands before you push:

| Command                  | Purpose                                    |
| ------------------------ | ------------------------------------------ |
| `npm run check`          | Formatting, lint, types, and tests         |
| `npm run lychee-check`   | Links                                      |
| `npm run handouts:build` | Rebuild the handouts after a source change |
| `npm run site:build`     | Full build with the Reveal.js decks        |
