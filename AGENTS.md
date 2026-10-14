# Agents Tooling Specification — Quarto

This repository holds the open educational resources for the workshop _Stochastic Parrots and Beyond: Normative Dimensions of Generative AI_. A Quarto website with Reveal.js slide decks and Typst handouts publishes them through GitHub Pages.

The file follows the shared [Agents Tooling Specification](https://gist.github.com/maehr/6c48ef14f37c9f745fa1fbaa315d106b), Quarto stack. Sections 1, 3, 5, and 6 are the shared text. Sections 2, 4, and 7 are narrowed to this repository. Sections 8 to 13 hold the rules of this course. No document executes code, and the repository has no R. Python runs only the tests. The repository keeps the template file names `LICENSE-AGPL.md`, `LICENSE-CCBY.md`, and `LICENSE-CCBYSA.md`, and the Contributor Covenant 2.1 from the template.

## 1. Orchestration

Context is the scarce resource. Manage it.

**Model tier.** A frontier model holds the plan, the decisions, and the shared context. A small model does a bounded subtask. Pick the tier before you spawn the agent.

**Delegate on evidence.** A subagent starts cold and derives the context again. Delegate work that reads far more than it reports: broad search, log triage, or fan-out over many files. Do a small local edit inline.

**Contracts, not conversations.** Give a subagent one task, the context it cannot infer, the output shape, and the stop condition. A subagent returns a conclusion, never a file dump. Verify a report before you act on it.

**Parallel only when independent.** Run agents at the same time only when no result feeds another. Use three at most.

**Context ladder.** At 25% of the window, name the source of the pressure. At 50%, reduce it: write state to disk, delegate the reading, or narrow the re-reads. At 75%, stop and reduce before further work.

**State on disk.** Write plans, findings, and decisions to files. The transcript dies at the next compaction.

**Read narrow.** Read the slice, not the file. After you write a file, verify the diff or the section you changed. Do not read the whole file again.

## 2. Tooling

`package.json` holds the contract. Call a script. Never call the tool that the script wraps.

**Quarto.** [Quarto](https://quarto.org/docs/guide/) CLI, pinned in CI to the version you develop against · [quarto-cli-mcp](https://github.com/maehr/quarto-cli-mcp) renders and inspects from an agent session. It builds a temporary project and rejects an outside path, so it writes nothing into this repository.

**PDF.** [Typst](https://quarto.org/docs/output-formats/typst.html) builds the printable handouts. This repository needs no TeX.

**Engine.** No document executes code. [uv](https://docs.astral.sh/uv/) installs the Python test tools only: pytest, ruff, and ty. Commit `uv.lock`.

**Documents.** [Prettier](https://prettier.io/) formats Markdown, YAML, and JSON, and formats `.qmd` with `--parser markdown` · [lychee](https://lychee.cli.rs/) checks links · [prek](https://prek.j178.dev/) runs the hooks · [commitlint](https://commitlint.js.org/) checks each commit message · [git-cliff](https://git-cliff.org/docs/) writes the changelog.

**Reference.** [open-research-data-template](https://github.com/maehr/open-research-data-template) carries the advanced workflow: a placeholder policy, a release that archives the site, a Zenodo DOI, and GitHub Pages. Take the workflow from it. Its `AGENTS.md` predates this specification, so do not take the structure. [All Data Are Local](https://github.com/maehr/all-data-are-local) is the model for the course structure and the visual design.

## 3. Standards

* [SemVer 2.0.0](https://semver.org/) for versions.
* [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages.
* [Contributor Covenant 3.0](https://www.contributor-covenant.org/version/3/0/code_of_conduct/) as `CODE_OF_CONDUCT.md`.
* [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.en.html) as `LICENSE`. SPDX identifier `AGPL-3.0-only`.

## 4. Code

**Preview while you edit.** `npm run preview` writes `_site/` and `.quarto/`. That is expected. Commit neither.

**Run no production render and no publish in an agent session** unless the maintainer asks. That covers `quarto publish`, the deploy workflow, and any release artifact. To check that a document still builds, use `quarto-cli-mcp`. It renders in a temporary project.

* Use `.qmd` for a Quarto document. Use `.md` for text that Quarto does not process.
* Give every document valid YAML front matter.
* Add no executable chunk without a decision from the maintainer.
* Cite only from `references.bib`. Never invent a citation or its metadata.
* Keep `_site/`, `.quarto/`, and `_freeze/` untracked. The project sets no `freeze`.
* Put a new file in the directory that matches its role: `assets/`, `contents/`, `data/`, `documentation/`, `scripts/`, `test/`.

Define one script that runs the whole gate. Call it, and let `prek` call it too:

```bash
npm run check
```

Add a new tool to that script. A direct `lychee` or `prettier` call drifts from CI. The gate runs no preview and no render. A preview never exits, and a production render belongs in CI.

## 5. GitHub Workflow

Use a fork and a pull request. Never push to upstream.

```bash
gh repo fork OWNER/REPO --clone
git switch -c feat/thing
gh pr create --repo OWNER/REPO
```

Allow maintainer edits. Resync with `gh repo sync`. Put one logical change in one PR. Title the PR with a Conventional Commit.

**Stacked PRs.** Each PR targets the branch below it. The bottom PR targets the trunk. Merge from the bottom up. GitHub retargets the rest. Take the requirements from the trunk only. Use the `gh stack` extension. Keep a stack in one repository, never across forks.

**Trunk protection.** Both layers are idempotent, so a second run converges.

```bash
gh repo edit --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false \
  --delete-branch-on-merge --allow-update-branch \
  --enable-secret-scanning --enable-secret-scanning-push-protection
gh api -X PUT repos/OWNER/REPO/branches/main/protection --input protection.json
```

The `PUT` replaces the whole configuration. Take the body shape from the [API reference](https://docs.github.com/en/rest/branches/branch-protection), not from a stale snippet.

For a repository with more than one maintainer, enforce a PR before a merge, at least one approval, dismissal of a stale approval on push, code-owner approval, last-push approval, conversation resolution, strict status checks, linear history, `enforce_admins: true`, no force-push, and no deletion. A solo repository differs. See the bullets below.

* Without `enforce_admins`, the rule is advisory for whoever can bypass it.
* A solo repository needs three settings together: 0 required approvals, no required code-owner review, and no required last-push approval. You cannot approve your own pull request, so either of the last two deadlocks the merge even at 0 approvals.
* The free plan covers branch protection on a public repository. Branch protection on a private repository needs Pro.
* Plan limits differ per feature. Secret scanning, push protection, CodeQL, and dependency review are free on a public repository. On a private repository each one needs a paid GitHub security plan. Check the plan before you enable one in a workflow or in `gh repo edit`.
* Rulesets are the successor at organization scale. `gh ruleset` only reads, and creation uses `POST`, so a second run duplicates the ruleset. Prefer the `PUT` for one repository.

## 6. CI/CD Security

Follow [secure use of Actions](https://docs.github.com/en/actions/reference/security/secure-use).

* Set `permissions: contents: read` at the top level. Widen it per job only where a job needs more.
* Default the repository token to read: `gh api -X PUT repos/OWNER/REPO/actions/permissions/workflow -f default_workflow_permissions=read`.
* Pin an action to a full commit SHA. Verify the SHA against the upstream repository, not a fork. Let Dependabot bump it.
* Never check out fork code under `pull_request_target`. Prefer `workflow_run`, and treat its artifacts as untrusted.
* Never interpolate `github.event.*` into `run:`. Pass the value through `env:` and quote `"$VAR"`.
* Use OIDC and a short-lived cloud role. Do not store a long-lived secret. Keep a secret a scalar, never a JSON blob. Rotate it.
* Gate a deploy on an Environment with required reviewers. Prefer an environment secret over a repository secret.
* Do not use a self-hosted runner on a public repository.
* Cover `.github/workflows/**` in `CODEOWNERS`.
* Require the section 4 gate, CodeQL, and `dependency-review-action`. Run the same gate locally, so CI gives no surprise. On a private repository, confirm the plan covers CodeQL and dependency review first.

## 7. Publishing

The workflow `.github/workflows/quarto-publish.yml` deploys the site from `main` to GitHub Pages. Never publish by hand. Never replace the workflow with a manual step.

* Render in CI. A local render hides a missing dependency.
* Pin the Quarto version in the workflow. An unpinned `quarto-actions/setup` changes the output with no commit.
* Give the deploy job the narrowest permission that works. Gate it on the `github-pages` Environment.
* Keep the site URL in `_quarto.yml`. An absolute link breaks a preview deployment.
* In the repository settings, Pages must use the source **GitHub Actions**.

## 8. Course Content

The course pages are teaching material for a real course. Accuracy matters more than style.

* Mark every fact with its status. CONFIRMED: a published course fact. PROPOSED: a decision that the instructors must approve. TBC: unknown.
* The official University of Basel course listing overrides this repository.
* Do not invent a date, a reading, a page number, a case, an outcome, or an assessment rule.
* Cite each claim next to the claim. Verify the source against the DOI or the publisher before you add it to `references.bib`.
* Label each example as a documented case or as a hypothetical example. A product name is not evidence.
* Leave a blank line between a list and a closing `:::`. Otherwise Prettier indents the fence, and the div stays open.
* Keep the section order of a lesson page: question, core concepts, evidence and limits, case, activity, output, reading, slides. `test/test_consistency.py` checks it.
* Never show, link, or describe in detail abusive images from audited datasets. Describe findings, and cite the audit.
* Ask the instructors before you change a timetable, a reading, or an assessment rule.

## 9. Edition Data

`data/editions.yml` is the single source for the facts of each edition. `_quarto.yml` loads it through `metadata-files`. The shortcode in `_extensions/edition/` renders it at build time.

* Write an edition fact only in `data/editions.yml`. Show it with the shortcode, for example `{{< edition hs2026 date >}}`.
* Use `null` for each unknown fact. The shortcode renders "To be confirmed".
* Never copy a value from one edition to another. Each value needs its own public source.
* Put no edition fact in a slide deck. The decks serve every edition.
* Show the evaluation link only on its own edition page.
* Switch `featured_edition` and `status: delivered` on purpose. Never delete or rename an edition page.

## 10. Privacy

The repository holds generic teaching resources only.

* Never commit participant names, contact details, attendance records, applications, evaluation answers, submissions, certificates, or signatures.
* Keep this data out of issues, pull requests, commit messages, assets, and archives too.
* Use synthetic examples. Label them as fictional.
* `test/test_privacy.py` and `.gitignore` catch common cases. Add a public role address to the allowlist only, never a personal one.

## 11. Liberating Structures and Licenses

* Material adapted from Liberating Structures carries CC BY-SA 4.0. Set `license: 'CC BY-SA'` in its front matter and keep the attribution text.
* Never relicense an adapted Liberating Structures asset as CC BY.
* Use no Liberating Structures icons, unless they are the original icons.
* Original course content carries CC BY 4.0. Code carries AGPL 3.0.

## 12. Handouts and Diagrams

* Edit the handout source in `contents/handouts/`. The source is also the accessible web version.
* Run `npm run handouts:build` after a change to a handout or to a diagram that it embeds. Commit the generated files in `assets/handouts/` in the same commit. The `check-handouts` CI job fails when a generated file is older than its sources.
* This build writes committed files, so it is allowed in an agent session.
* Open each generated PDF and check the layout. A table that does not fit moves to the next page without an error.
* The SVG files are the editable sources of the diagrams. Keep their `<title>` and `<desc>` current. Use the greyscale palette from `_brand.yml`.

## 13. Writing Style

* Write procedures, instructions, and documentation in Simplified Technical English: one instruction per sentence, active voice, short sentences.
* Use American English on the site. Keep the original spelling in titles and quotations.
