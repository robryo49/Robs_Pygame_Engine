# Repository Guidelines

## Project overview

Robs Pygame Engine is a Python 3.13+ 2D game-engine library built on
`pygame-ce`. The importable package lives in `src/robs_pge`; the `test/`
directory currently contains runnable examples and their assets.

## Working conventions

- Make focused changes and preserve existing public APIs unless the task calls
  for an intentional breaking change.
- Keep engine code under `src/robs_pge` and group related functionality within
  the existing package areas (`core`, `objects`, `rendering`, `physics`, etc.).
- Use type annotations where practical and follow the surrounding module's
  formatting, naming, and docstring style.
- Prefer package-relative imports where they make internal dependencies clear.
- Do not commit generated artefacts such as `__pycache__`, `.mypy_cache`, or
  virtual-environment contents.

## Dependencies

- Dependencies and Python requirements are defined in `pyproject.toml`.
- Use `uv` to manage the environment and dependencies; do not edit `uv.lock`
  unless dependency resolution is intentionally part of the change.
- Keep runtime dependencies minimal. Add a dependency only when the feature
  cannot reasonably use the existing stack.

## Validation

- Run the narrowest relevant check first. For a general smoke test, use:

  ```powershell
  uv run python -m compileall src
  ```

- If a change affects the example application or rendering behaviour, run the
  relevant entry point in `test/src` and confirm it starts without errors.
- Avoid tests that require a visible graphics window in unattended or headless
  environments unless explicitly requested.

## Change hygiene

- Update `README.md` when a user-facing API, setup requirement, or documented
  capability changes.
- Mention validation performed and any graphics-dependent checks that were not
  run in the final handoff.
