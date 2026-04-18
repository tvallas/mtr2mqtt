# AGENTS.md

This repository welcomes agent assistance, but changes should follow the same working practices as a careful human contributor.

## Scope

- These instructions apply to the whole repository.
- Prefer small, focused changes over broad refactors unless the task explicitly asks for a larger rewrite.
- Preserve existing behavior unless the change is intentionally fixing a bug or changing a documented feature.

## Branching

- Always create a new branch before starting a new feature, fix, refactor, or documentation task.
- Do not work directly on `master`.
- Use a branch name that reflects the change, for example:
  - `fix/serial-recovery`
  - `feat/home-assistant-...`
  - `docs/update-readme`
  - `chore/dependency-updates`

## Commits

- Always use Conventional Commits.
- Commit messages must be compatible with semantic-release.
- Create commits in logical groups.
- Each commit should represent one coherent change or one tightly related set of changes.
- Prefer clear commit types such as:
  - `fix(...)` for bug fixes
  - `feat(...)` for user-facing functionality
  - `docs(...)` for documentation-only changes
  - `test(...)` for test-only changes
  - `chore(...)` for maintenance work
  - `refactor(...)` for code restructuring without behavior changes
- Keep commit messages concise and specific.
- Commit messages should explain why the change was made when that is not already obvious from the diff.
- Do not use vague commit messages like `updates`, `misc fixes`, or `work in progress`.
- Never mention AI, agents, or automated authorship in commit messages.

## Testing And Verification

- Tests must always be run before committing when code or behavior changes.
- Functionality must be verified before committing, not just the tests.
- At minimum, run the most relevant validation for the change:
  - `uv run pytest`
  - `make test`
  - targeted manual verification for the affected CLI behavior, serial handling, MQTT behavior, or Home Assistant discovery flow
- If a change affects runtime behavior, verify the real behavior as directly as possible, not only through unit tests.
- If something cannot be tested locally, say so clearly in the final summary and in the PR description.

## Documentation

- Update documentation whenever behavior, configuration, CLI flags, environment variables, metadata format, or operational expectations change.
- Documentation updates commonly belong in:
  - `README.md`
  - sample metadata or usage examples
  - release/process docs under `docs/`
- Do not leave docs behind after changing the code.

## Implementation Guidelines

- Add or update tests alongside code changes whenever practical.
- Prefer focused fixes over unrelated cleanup.
- Keep logging and error handling helpful for operators, especially because this project interacts with serial devices and MQTT brokers.
- Be careful with reconnect, retry, and hardware error paths. Stability is more important than cleverness.
- Avoid changing packaging or release configuration unless the task requires it.

## Pull Requests

- Push the branch to the remote repository after the work is ready.
- Summarize what changed, why it changed, and how it was validated.
- Pull request descriptions should explain the reason for the change, not only list the code changes.
- Mention any manual verification performed.
- Call out any limitations, follow-up work, or areas that could not be tested.
- Never add advertising or attribution that the work was done by an AI agent.

## Final Check Before Commit

- Confirm the work is on a dedicated branch.
- Confirm tests were run.
- Confirm the changed functionality was verified.
- Confirm relevant documentation was updated.
- Confirm the commit message follows Conventional Commits and semantic-release expectations.

## Final Check Before Opening A Pull Request

- Confirm the commits are logically grouped.
- Confirm the branch has been pushed to the remote.
- Confirm the pull request description clearly explains both what changed and why it changed.
- Confirm validation steps are included.
- Confirm there is no AI attribution, marketing, or automated authorship language in the branch, commits, or pull request text.
