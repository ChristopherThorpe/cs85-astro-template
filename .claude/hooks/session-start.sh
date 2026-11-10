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

# Point Python at the system certificate list. The environment's setup script adds the
# "emSign Root CA - G1" authority there (needed for gwosc.org and mastresolver.stsci.edu,
# projects 18, 19, 25). But the cloud proxy sets REQUESTS_CA_BUNDLE and SSL_CERT_FILE to its
# own copy, /root/.ccr/ca-bundle.crt, which can be made before the setup script runs and so
# lack emSign. The system list holds everything the proxy's list does, plus emSign. We only
# switch when that's true, so verification never gets looser. The settings go to:
#   - CLAUDE_ENV_FILE: every command Claude runs this session;
#   - /etc/profile.d/cs85-ca-bundle.sh: login shells (loads after ccr-agent-proxy-ca.sh);
#   - /etc/bash.bashrc: interactive terminal shells, which don't read /etc/profile.
system_ca=/etc/ssl/certs/ca-certificates.crt
proxy_ca=/root/.ccr/agent-proxy-ca.crt
profile_file=/etc/profile.d/cs85-ca-bundle.sh
if grep -q "MIIDlDCCAnygAwIBAgIKMfXkYgxsWO3W2D" "$system_ca" 2>/dev/null \
   && { [ ! -f "$proxy_ca" ] || python3 -I -c '
import re, sys
pems = lambda f: set(re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", open(f).read(), re.S))
sys.exit(0 if pems(sys.argv[1]) <= pems(sys.argv[2]) else 1)' "$proxy_ca" "$system_ca"; }; then
  if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    echo "export REQUESTS_CA_BUNDLE=$system_ca SSL_CERT_FILE=$system_ca" >> "$CLAUDE_ENV_FILE"
  fi
  # Overwrite (not set-if-missing): terminals usually inherit the proxy's value already.
  if { printf '# Written by the CS85 SessionStart hook (.claude/hooks/session-start.sh).\n'
       printf 'export REQUESTS_CA_BUNDLE=%s SSL_CERT_FILE=%s\n' "$system_ca" "$system_ca"; } > "$profile_file" 2>/dev/null; then
    grep -qF "$profile_file" /etc/bash.bashrc 2>/dev/null \
      || printf '\n# CS85: certificate list for Python downloads\n[ -r %s ] && . %s\n' "$profile_file" "$profile_file" >> /etc/bash.bashrc \
      || echo "Note: couldn't update /etc/bash.bashrc; terminal shells keep the default certificate list." >&2
  else
    echo "Note: couldn't write $profile_file; terminal shells keep the default certificate list." >&2
  fi
else
  rm -f "$profile_file" 2>/dev/null || true   # don't leave an old setting behind
  echo "Note: kept the default certificate list; projects 18, 19, 25 may fail with CERTIFICATE_VERIFY_FAILED." >&2
fi

# The hash file lives next to the installed packages, so it disappears if they do.
hashes="$(python3 -I -c 'import sysconfig; print(sysconfig.get_path("purelib"))')/.cs85-session-start.sha256"
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  echo "Installing solar and DASCH packages (requirements-extras.txt)..." >&2
  python3 -m pip install --break-system-packages -q --use-pep517 --root-user-action=ignore \
    -r requirements-extras.txt >&2
  sha256sum .claude/hooks/session-start.sh requirements-extras.txt > "$hashes"
fi
