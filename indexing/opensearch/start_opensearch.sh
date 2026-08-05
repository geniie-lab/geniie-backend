#!/bin/bash
# start-opensearch.sh — recreate the OpenSearch container, with or without snapshot support.
# Usage:  bash indexing/opensearch/start_opensearch.sh DATA_DIR                       (no snapshot volume, default)
#         bash indexing/opensearch/start_opensearch.sh DATA_DIR --snapshot SNAP_DIR   (mount snapshot volume + register repo)
#         bash indexing/opensearch/start_opensearch.sh DATA_DIR --ja                  (install Japanese analysis plugins)
#   DATA_DIR: existing host folder holding OpenSearch data (bind-mounted into the container)
#   SNAP_DIR: host folder for the snapshot repository (created if missing).
#             NOT /tmp: systemd-tmpfiles age-cleanup deletes old /tmp files (~10 days)
#             and silently corrupts the shared-file snapshot repo.
#   --ja:     install Japanese analysis plugins (kuromoji + icu). REQUIRED when the
#             data folder holds Japanese indices (e.g. NTCIR) — they stay RED otherwise.
# Safe to re-run: data lives in DATA_DIR and survives recreation.
set -euo pipefail

USAGE="Usage: $0 DATA_DIR [--snapshot SNAP_DIR] [--ja]"
WITH_SNAPSHOT=false
WITH_JA=false
DATA_DIR=""
SNAP_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ja) WITH_JA=true ;;
    --snapshot)
      WITH_SNAPSHOT=true
      if [[ $# -lt 2 || "$2" == -* ]]; then
        echo "ERROR: --snapshot requires a SNAP_DIR argument." >&2
        echo "$USAGE" >&2; exit 1
      fi
      SNAP_DIR="$2"; shift
      ;;
    -*) echo "$USAGE" >&2; exit 1 ;;
    *)
      if [[ -n "$DATA_DIR" ]]; then
        echo "$USAGE" >&2; exit 1
      fi
      DATA_DIR="$1"
      ;;
  esac
  shift
done

if [[ -z "$DATA_DIR" ]]; then
  echo "ERROR: DATA_DIR is required." >&2
  echo "$USAGE" >&2
  exit 1
fi
if [[ ! -d "$DATA_DIR" ]]; then
  echo "ERROR: DATA_DIR '$DATA_DIR' does not exist or is not a directory." >&2
  echo "Refusing to start: a wrong path would launch OpenSearch with an empty data folder." >&2
  exit 1
fi
DATA_DIR="$(realpath "$DATA_DIR")"   # docker -v requires an absolute path

### ── Edit these ──────────────────────────────────────────────
PLUGINS=""                                # analysis plugins to install (none by default)
if $WITH_JA; then
  # Japanese text processing (required by the NTCIR indices — without these
  # plugins any index using the kuromoji analyzer stays RED).
  PLUGINS="analysis-kuromoji analysis-icu"
fi
IMAGE="opensearchproject/opensearch:3.5.0"  # pin to your actual version (check: curl -k -u ... https://localhost:9200)
HEAP="4g"
### ────────────────────────────────────────────────────────────

# Load credentials from .env at the REPO ROOT (not the script's folder).
# Intended invocation:  bash indexing/opensearch/start_opensearch.sh   (from repo root)
# .env must contain:  OPENSEARCH_INITIAL_ADMIN_PASSWORD="strong password"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ENV_FILE="${REPO_ROOT}/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found." >&2
  echo "Create it with:  echo 'OPENSEARCH_INITIAL_ADMIN_PASSWORD=\"yourpassword\"' > $ENV_FILE && chmod 600 $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

if [[ -z "${OPENSEARCH_INITIAL_ADMIN_PASSWORD:-}" ]]; then
  echo "ERROR: OPENSEARCH_INITIAL_ADMIN_PASSWORD is not set in $ENV_FILE" >&2
  exit 1
fi
ADMIN_PASSWORD="$OPENSEARCH_INITIAL_ADMIN_PASSWORD"
CRED="admin:${ADMIN_PASSWORD}"

# Snapshot volume args (only when enabled)
SNAP_ARGS=()
if $WITH_SNAPSHOT; then
  # Snapshot dir must exist and be writable by container UID 1000
  mkdir -p "$SNAP_DIR"
  chown 1000:1000 "$SNAP_DIR"
  SNAP_DIR="$(realpath "$SNAP_DIR")"   # docker -v requires an absolute path
  SNAP_ARGS=(-v "$SNAP_DIR":/mnt/snapshots -e "path.repo=/mnt/snapshots")
fi

# Recreate container (idempotent)
docker rm -f opensearch-node 2>/dev/null || true

docker run -d -p 9200:9200 -p 9600:9600 \
    -v "$DATA_DIR":/usr/share/opensearch/data \
    "${SNAP_ARGS[@]}" \
    -e "discovery.type=single-node" \
    -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=${ADMIN_PASSWORD}" \
    -e "OPENSEARCH_JAVA_OPTS=-Xms${HEAP} -Xmx${HEAP}" \
    --add-host=host.docker.internal:host-gateway \
    --restart unless-stopped \
    --name opensearch-node "$IMAGE"

# Install required analysis plugins (wiped on every recreate — container-side, not in DATA_DIR).
# Indices using these analyzers (e.g. kuromoji for Japanese) stay RED until plugins are present.
if [[ -n "$PLUGINS" ]]; then
  echo "Installing plugins: $PLUGINS"
  sleep 5   # container process needs a moment before exec works reliably
  # shellcheck disable=SC2086
  docker exec opensearch-node \
    /usr/share/opensearch/bin/opensearch-plugin install --batch $PLUGINS
  docker restart opensearch-node > /dev/null
fi

# Wait for the API to come up (max ~2 minutes)
echo -n "Waiting for OpenSearch"
for i in $(seq 1 60); do
  if curl -sk -u "$CRED" "https://localhost:9200/_cluster/health" | grep -q '"status"'; then
    echo " — up."
    break
  fi
  echo -n "."
  sleep 2
  if [[ $i -eq 60 ]]; then
    echo " ERROR: OpenSearch did not become ready. Check: docker logs opensearch-node" >&2
    exit 1
  fi
done

if $WITH_SNAPSHOT; then
  # Register snapshot repository (idempotent — PUT overwrites with same settings)
  curl -sk -u "$CRED" -X PUT "https://localhost:9200/_snapshot/local_backup" \
    -H 'Content-Type: application/json' \
    -d '{ "type": "fs", "settings": { "location": "/mnt/snapshots", "compress": true } }' \
    && echo ""
  echo "OpenSearch ready. Snapshot repo 'local_backup' registered at $SNAP_DIR."
else
  echo "OpenSearch ready (snapshot support disabled — nightly OpenSearch snapshots will fail until re-run with --snapshot)."
fi