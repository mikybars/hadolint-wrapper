#!/usr/bin/env bash

echo 'alias l="ls -CF"' >> $HOME/.bashrc

poetry install
sudo cp .devcontainer/welcome.txt > /workspaces/.codespaces/shared/first-run-notice.txt

echo "Done!"
