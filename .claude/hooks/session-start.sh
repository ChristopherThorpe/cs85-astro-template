#!/bin/bash
# Runs at the start of each cloud session. It (1) sets up the certificate list so projects
# 18, 19 and 25 can download, and (2) starts installing the solar (projects 13, 14, 16) and
# DASCH (project 03) packages in the background. Those aren't in the environment's setup
# script because that script is stopped after about 5 minutes. The hook itself takes a few
# seconds at most.
set -euo pipefail

# Only run in Claude Code cloud sessions, not on a student's own computer.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Certificates: gwosc.org and mastresolver.stsci.edu (projects 18, 19, 25) use certificates
# from the "emSign Root CA - G1" authority. It's in Mozilla's trusted list, but not in this
# container's system list.
system_ca=/etc/ssl/certs/ca-certificates.crt
proxy_ca=/root/.ccr/agent-proxy-ca.crt
profile_file=/etc/profile.d/cs85-ca-bundle.sh
emsign_marker="MIIDlDCCAnygAwIBAgIKMfXkYgxsWO3W2D"   # first line of the emSign certificate

# Step 1: add emSign to the system list. The setup script does this too, but when a session
# reuses the saved environment, the cloud proxy rebuilds the system list at start-up and
# emSign is lost. This hook runs after that, every session, so we add it again here. We
# check the certificate's fingerprint first, so only the real emSign root gets added.
emsign_src=certs/emSign_Root_CA_-_G1.crt
emsign_sha256="40:F6:AF:03:46:A9:9A:A1:CD:1D:55:5A:4E:9C:CE:62:C7:F9:63:46:03:EE:40:66:15:83:3D:C8:C8:D0:03:67"
if ! grep -q "$emsign_marker" "$system_ca" 2>/dev/null; then
  if [ "$(openssl x509 -in "$emsign_src" -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2)" = "$emsign_sha256" ]; then
    { cp "$emsign_src" /usr/local/share/ca-certificates/emSign_Root_CA_-_G1.crt \
        && update-ca-certificates >/dev/null 2>&1; } \
      || echo "Note: couldn't add the emSign certificate to the system list." >&2
  else
    echo "Note: $emsign_src is missing or has the wrong fingerprint; not adding it." >&2
  fi
fi

# Step 2: point Python at the system list. The cloud proxy sets REQUESTS_CA_BUNDLE and
# SSL_CERT_FILE to its own copy, /root/.ccr/ca-bundle.crt, which lacks emSign. We only
# switch when the system list holds everything the proxy's list does, plus emSign, so
# verification never gets looser. The settings go to:
#   - CLAUDE_ENV_FILE: every command Claude runs this session;
#   - /etc/profile.d/cs85-ca-bundle.sh: login shells (loads after ccr-agent-proxy-ca.sh);
#   - /etc/bash.bashrc: interactive terminal shells, which don't read /etc/profile.
if grep -q "$emsign_marker" "$system_ca" 2>/dev/null \
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

# Solar and DASCH packages: install them in the background, so the session starts right away.
# The saved environment doesn't keep what this hook installs, so this runs in most sessions
# and takes a couple of minutes. Starters 03, 13, 14 and 16 wait for it (they take the same
# lock file) or install the package themselves if it's still missing.
# The hash file lives next to the installed packages, so it disappears if they do.
hashes="$(python3 -I -c 'import sysconfig; print(sysconfig.get_path("purelib"))')/.cs85-session-start.sha256"
lock="${TMPDIR:-/tmp}/cs85-extras.lock"
log="${TMPDIR:-/tmp}/cs85-extras-install.log"
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  echo "Installing solar and DASCH packages in the background (log: $log)." >&2
  # setsid + nohup: keep running after this hook exits. flock -n: skip if one is already running.
  setsid nohup flock -n "$lock" bash -c '
    python3 -m pip install --break-system-packages -q --use-pep517 --root-user-action=ignore \
      -r requirements-extras.txt \
    && sha256sum .claude/hooks/session-start.sh requirements-extras.txt > "$1" \
    && echo "cs85: solar and DASCH packages installed."' _ "$hashes" > "$log" 2>&1 < /dev/null &
fi
