#!/bin/bash
set -euo pipefail

# Run asynchronously in the background during session startup
echo '{"async": true, "asyncTimeout": 300000}'

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

HUGO_VERSION="0.147.0"

# Install Hugo (extended) if not already installed
if ! command -v hugo &>/dev/null || [[ "$(hugo version 2>/dev/null)" != *"${HUGO_VERSION}"* ]]; then
  echo "Installing Hugo v${HUGO_VERSION} (extended)..."
  HUGO_INSTALL_DIR="${HOME}/.local/bin"
  mkdir -p "${HUGO_INSTALL_DIR}"
  wget -qO /tmp/hugo.tar.gz "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" \
    && tar -xzf /tmp/hugo.tar.gz -C "${HUGO_INSTALL_DIR}" hugo \
    && rm -f /tmp/hugo.tar.gz
  # Make hugo available on PATH for this session
  echo "export PATH=\"${HUGO_INSTALL_DIR}:\${PATH}\"" >> "${CLAUDE_ENV_FILE}"
  export PATH="${HUGO_INSTALL_DIR}:${PATH}"
fi

# Initialize git submodules (hugo-book theme)
if [ ! -f "${CLAUDE_PROJECT_DIR}/themes/hugo-book/theme.toml" ]; then
  echo "Initializing git submodules..."
  git -C "${CLAUDE_PROJECT_DIR}" submodule update --init --recursive
fi

# Ensure PyYAML is available (needed by validation scripts)
if ! python3 -c "import yaml" &>/dev/null; then
  echo "Installing PyYAML..."
  pip3 install --quiet PyYAML
fi
