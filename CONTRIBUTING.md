# Contributing

Contributions are welcome when they make the course materials more accurate, clearer, easier to teach, or easier to reuse.

Follow the [code of conduct](CODE_OF_CONDUCT.md) in all project spaces.

## What Helps Most

- A correction of a wrong fact, a broken link, or a citation that does not support its claim.
- A better source for a claim, with a link to a lawful copy.
- An accessibility problem on a page, a slide deck, or a handout.
- A report from a teacher who reused the course, with the changes that worked.

## Rules for Course Content

- Cite each claim next to the claim. Add the source to `references.bib` and verify it against the publisher or the DOI first.
- Mark a documented harm as documented, and a hypothetical example as hypothetical.
- Do not change a confirmed course fact without a public source. The official University of Basel course listing overrides this repository.
- Do not add copyrighted readings, scans, or third-party slides. Link to a lawful copy instead.

## Privacy

This repository is public. It holds generic teaching resources only.

- Do not commit participant names, contact details, attendance records, evaluation answers, submissions, certificates, or signatures.
- Do not put this information into an issue, a pull request, or a commit message.
- Use synthetic examples. Use a real example only with the informed permission of the person.

## License of Contributions

A contribution takes the license of the file that it changes.

| Content                                     | License                                 |
| ------------------------------------------- | --------------------------------------- |
| Original course text, figures, and handouts | [CC BY 4.0](LICENSE-CCBY.md)            |
| Material adapted from Liberating Structures | [CC BY-SA 4.0](LICENSE-CCBYSA.md)       |
| Code, configuration, and build scripts      | [AGPL 3.0](LICENSE-AGPL.md)             |
| Third-party material                        | The terms of the owner, stated per file |

## Local and Agent Setup

Use [GitHub Codespaces](https://github.com/features/codespaces) or follow the local setup in [README.md](README.md). A coding agent must read [AGENTS.md](AGENTS.md) before it changes a file.

## Pull Request Process

1. Open an issue first for a large change, a new tool, or a change to the teaching sequence.
2. Keep each pull request to one topic.
3. Update the affected documentation in the same pull request.
4. Run `npm run preview` while you edit.
5. Run `npm run format` and `npm run check` before you request a review.
6. Run `uv run pytest` to check the edition data and the privacy guards.
7. Commit with a Conventional Commit subject, for example `git commit -m "docs: correct a reading link"`.
8. Wait for a maintainer review before you merge.
