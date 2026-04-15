# CI and release baseline

This document describes the current automation baseline for `mtr2mqtt` and the target direction for the upcoming incremental migration.

## Current state

The repository currently has separate GitHub Actions workflows for:

- lint and test on push
- semantic release
- Docker publishing
- Trivy scanning

Those workflows remain in place during the first migration step. The goal of this PR is only to add a new baseline CI workflow and document the current state, without changing release behavior.

## Packaging baseline

The project currently uses:

- `setup.py`
- `setup.cfg`
- `Pipfile`
- `Pipfile.lock`

Versioning for semantic release is currently tied to `setup.py`, and `setup.cfg` points semantic-release at `setup.py:__version__`.

## Branch and release baseline

The default working branch is currently `master`.

At the time of writing, release automation and Docker automation are still handled by separate legacy workflows. They are not replaced in this step.

## PR1 goal

PR1 adds a new `ci.yml` workflow that runs on pull requests and pushes to `master`.

The new CI workflow is intentionally limited to:

- dependency installation using the current Pipenv-based setup
- pytest execution
- package build smoke test
- Docker build smoke test without pushing

This step does **not**:

- remove any old workflows
- change semantic release
- change PyPI publishing
- change Docker publishing
- migrate packaging to `pyproject.toml`
- introduce coverage gates

## Target direction

The long-term target is:

1. one clean CI workflow for pull requests and branch pushes
2. one dedicated Python release workflow
3. one dedicated Docker publish workflow triggered only after a successful release
4. stronger test coverage, including mocked serial/MQTT tests and Linux PTY-based serial simulation
5. later migration to modern Python packaging

## Why this is incremental

The repository already has working release-related automation. Replacing all of it at once would be higher risk than adding a parallel CI workflow first.

This staged approach keeps the repository usable after each PR and makes rollback simple.