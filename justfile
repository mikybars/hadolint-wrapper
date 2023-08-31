help:
  @just --list

[private]
@install:
	poetry install &>/dev/null

# Run hadolintw with args
[no-exit-message]
run *ARGS: install
	poetry run hadolintw {{ARGS}}