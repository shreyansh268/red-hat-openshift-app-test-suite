#!/usr/bin/env bash
set -euo pipefail

APP_URL="${1:-${APP_URL:-}}"
MAX_RETRIES="${2:-30}"
SLEEP_SECONDS=10

if [[ -z "$APP_URL" ]]; then
  echo "Usage: $0 <app-url> [max-retries]"
  exit 1
fi

echo "Waiting for ${APP_URL}/healthz to respond 200..."

for i in $(seq 1 "$MAX_RETRIES"); do
  STATUS=$(curl -sk -o /dev/null -w "%{http_code}" "${APP_URL}/healthz" || true)
  if [[ "$STATUS" == "200" ]]; then
    echo "Ready after attempt ${i} (status ${STATUS})"
    exit 0
  fi
  echo "Attempt ${i}/${MAX_RETRIES}: status=${STATUS} — retrying in ${SLEEP_SECONDS}s"
  sleep "$SLEEP_SECONDS"
done

echo "ERROR: App did not become ready after $((MAX_RETRIES * SLEEP_SECONDS))s"
exit 1
