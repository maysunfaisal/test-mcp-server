#!/usr/bin/env bash
set -euo pipefail

# Build and optionally push a multi-arch image manifest with Podman.
#
# Example:
#   ./scripts/build-multiarch.sh
#   PUSH=1 ./scripts/build-multiarch.sh

if ! command -v podman >/dev/null 2>&1; then
  echo "Error: podman is required but not installed." >&2
  exit 1
fi

IMAGE_REF="${IMAGE_REF:-localhost/test-mcp-server:latest}"

CONTAINERFILE="${CONTAINERFILE:-Containerfile}"
CONTEXT_DIR="${CONTEXT_DIR:-.}"
PLATFORMS="${PLATFORMS:-linux/amd64,linux/arm64}"
PUSH="${PUSH:-0}"

echo "Building manifest ${IMAGE_REF} for platforms: ${PLATFORMS}"

# Replace any pre-existing local manifest with the same name.
podman manifest rm "${IMAGE_REF}" >/dev/null 2>&1 || true

podman build \
  --platform "${PLATFORMS}" \
  --manifest "${IMAGE_REF}" \
  -f "${CONTAINERFILE}" \
  "${CONTEXT_DIR}"

if [[ "${PUSH}" == "1" ]]; then
  echo "Pushing multi-arch manifest to registry: ${IMAGE_REF}"
  podman manifest push --all "${IMAGE_REF}" "docker://${IMAGE_REF}"
  echo "Push complete."
else
  echo "PUSH=${PUSH}; skipped manifest push."
fi
