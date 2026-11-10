#!/bin/bash
# Installs the solar (projects 13, 14, 16) and DASCH (project 03) packages at the start of
# each cloud session. They aren't in the environment's setup script because that script is
# stopped after about 5 minutes. Only installs when something is missing or changed, so
# after the first time this finishes in well under a second.
set -euo pipefail

# Only run in Claude Code cloud sessions, not on a student's own computer.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# The hash file lives next to the installed packages, so it disappears if they do.
hashes="$(python3 -I -c 'import sysconfig; print(sysconfig.get_path("purelib"))')/.cs85-session-start.sha256"
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  echo "Installing solar and DASCH packages (requirements-extras.txt)..." >&2
  python3 -m pip install --break-system-packages -q --use-pep517 --root-user-action=ignore \
    -r requirements-extras.txt >&2
  sha256sum .claude/hooks/session-start.sh requirements-extras.txt > "$hashes"
fi
