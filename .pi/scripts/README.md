# pi helper scripts

## `testlog`

`testlog` records test/lint command results and can tell whether a previous passing result still applies to the current git worktree. It is intended for coding-agent workflows where `/step` may already have run tests and `/finish` should avoid rerunning the same command when nothing relevant changed.

### Commands

```bash
.pi/scripts/testlog run -- <command> [args...]
.pi/scripts/testlog status -- <command> [args...]
.pi/scripts/testlog latest
```

Examples:

```bash
.pi/scripts/testlog run -- pytest -q
.pi/scripts/testlog status -- pytest -q
.pi/scripts/testlog run -- python -m compileall wmath tests
.pi/scripts/testlog run -- .venv/bin/python -m ruff check .
```

The `--` separates `testlog` options from the command being checked or run. Use the exact same command for `status` that you used for `run`; command strings are matched exactly.

### Workflow

During implementation:

```bash
.pi/scripts/testlog run -- pytest -q
```

During finish/checkpoint:

```bash
.pi/scripts/testlog status -- pytest -q
```

If the result is `fresh pass`, report the previous passing result and do not rerun. If the result is `stale` or `missing`, rerun:

```bash
.pi/scripts/testlog run -- pytest -q
```

### Output meanings

- `fresh pass`: the same command already passed for the current source tree.
- `stale`: the command passed before, but `HEAD`, tracked changes, or untracked files differ now.
- `missing`: no previous passing run exists for that exact command.

`status` exit codes:

- `0`: fresh pass
- `1`: stale
- `2`: missing or command usage error

`run` exits with the wrapped command's exit code.

### Log file

Runs are appended to:

```text
.pi/test-runs.jsonl
```

Each line is JSON with fields like:

```json
{"cmd":"pytest -q","exit_code":0,"fingerprint":{"head":"...","tracked_diff":"...","untracked":"..."},"status":"pass","time":"2026-05-28T19:06:19Z"}
```

The log file should be ignored by git:

```gitignore
.pi/test-runs.jsonl
```

### Freshness fingerprint

`testlog` records three source-state values:

1. `head`: current `git rev-parse HEAD`.
2. `tracked_diff`: SHA-256 of `git diff --binary HEAD -- .`, excluding the test log files.
3. `untracked`: SHA-256 of untracked, non-ignored file paths and contents.

This means a previous pass becomes stale when tracked files change, staged files change, `HEAD` changes, or untracked non-ignored files change.

Ignored files are not fingerprinted. Changes in `.venv/`, caches, ignored build outputs, external services, dependency versions, environment variables, and flaky tests can still invalidate practical confidence even when `testlog status` says `fresh pass`.

### Safe manual smoke test

This procedure only appends to the ignored log file.

```bash
git status --short
.pi/scripts/testlog status -- python -c "print('ok')"
.pi/scripts/testlog run -- python -c "print('ok')"
.pi/scripts/testlog status -- python -c "print('ok')"
.pi/scripts/testlog latest
.pi/scripts/testlog run -- python -c "raise SystemExit(3)"; echo $?
git status --short
```

Expected behavior:

- First `status` is usually `missing` unless already run.
- `run -- python -c "print('ok')"` prints `ok` and records `pass`.
- Second `status` reports `fresh pass`.
- Failing command records `fail` and returns exit code `3`.
- `git status --short` should not show `.pi/test-runs.jsonl`.

### Reusing in another project

To copy this workflow into another git repository:

1. Copy `.pi/scripts/testlog` into the target repo.
2. Make it executable:

   ```bash
   chmod +x .pi/scripts/testlog
   ```

3. Add the log file to `.gitignore`:

   ```gitignore
   .pi/test-runs.jsonl
   ```

4. Update project agent prompts/instructions to use:

   ```bash
   .pi/scripts/testlog run -- <command>
   .pi/scripts/testlog status -- <command>
   ```

The script assumes it lives at `.pi/scripts/testlog` and treats two parent directories above the script as the repository root.
