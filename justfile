help:
  @just --list

[private]
install:
  #!/usr/bin/env bash
  if [[ pyproject.toml -nt poetry.lock ]]; then
    poetry install
  fi

# Run hadolintw with args
[no-exit-message]
@run *ARGS: install
	poetry run hadolintw {{ARGS}}
