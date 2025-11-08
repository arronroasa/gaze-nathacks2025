#!/usr/bin/env bash
set -e

IMAGE_NAME="lem_poop"

CLEAN_IMAGE=false
LIST_IMAGE=false
REM_WHEN_DONE=true

BUILD_CMD="docker build -t ${IMAGE_NAME} -f ./Dockerfile ."

# Parse flags
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean) CLEAN_IMAGE=true; shift ;;
        --list) LIST_IMAGE=true; shift ;;
        --n-rm) REM_WHEN_DONE=false; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Rebuild with no cache if --clean was provided
$CLEAN_IMAGE && BUILD_CMD="docker build --no-cache -t ${IMAGE_NAME} ."

echo "Building Docker image..."
eval "$BUILD_CMD"

# List images if --list was provided
if [ "$LIST_IMAGE" = true ]; then
    echo "Docker Images on PC (for potential image issues):"
    docker images
fi

# Run container
if [ "$REM_WHEN_DONE" = true ]; then
    docker run --rm "${IMAGE_NAME}"
else
    docker run "${IMAGE_NAME}"
fi
