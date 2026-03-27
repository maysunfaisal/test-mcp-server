# Test MCP Server

A simple MCP (Model Context Protocol) server for testing Lightspeed integration. Built with FastMCP and uvicorn, it includes middleware to handle Docker-to-host communication.

## Features

- **echo** - Echo back a message for testing connectivity
- **get_current_time** - Get the current server time
- **add_numbers** - Add two numbers together
- **get_server_info** - Get information about the MCP server

## Requirements

- Python 3.10+
- Dependencies: `mcp`, `uvicorn`

## Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install mcp uvicorn
```

## Usage

```bash
python test_mcp_server.py
```

The server starts on port 8888 by default.

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_PORT` | `8888` | Port the server listens on |
| `MCP_AUTH_TOKEN` | `test-secret-token` | Authentication token |

## Authentication

All requests must include a Bearer token in the Authorization header:

```bash
curl -H "Authorization: Bearer test-secret-token" http://localhost:8888/mcp
```

Requests without a valid token will receive a `401 Unauthorized` response.

## Docker Support

The server includes `HostRewriteMiddleware` to handle host header validation when running in Docker containers communicating with the host machine.

### Build and run as a container

Build the image (Docker or Podman):

```bash
podman build -t test-mcp-server -f Containerfile .
```

Run it with an auth token and exposed port:

```bash
podman run --rm -p 8888:8888 \
  -e MCP_SERVER_PORT=8888 \
  -e MCP_AUTH_TOKEN=test-secret-token \
  test-mcp-server
```

Quick auth check:

```bash
## Should fail
curl -i http://localhost:8888/mcp
```

### Multi-arch build and push (amd64 + arm64)

Use the helper script to build a multi-arch manifest with Podman. By default it uses `localhost/test-mcp-server:latest` and does not push.

> [!WARNING]
> `quay.io/redhat-ai-dev/test-mcp-server:latest` is the official upstream location. Pushing to that `latest` tag can overwrite what is already published there.

```bash
./scripts/build-multiarch.sh
```

Optional overrides:

```bash
IMAGE_REF=quay.io/<your-org>/test-mcp-server:latest ./scripts/build-multiarch.sh
PUSH=1 IMAGE_REF=quay.io/<your-org>/test-mcp-server:latest ./scripts/build-multiarch.sh
PLATFORMS=linux/amd64,linux/arm64 PUSH=1 IMAGE_REF=quay.io/<your-org>/test-mcp-server:latest ./scripts/build-multiarch.sh
```

Troubleshooting Quay push permissions:

- If `PUSH=1` fails with `unauthorized: access to the requested resource is not authorized`, the repository may have been auto-created as private or your token may not have write permissions.
- Fixes:
  - In Quay, set repository visibility/settings as needed for your workflow.
  - Ensure you are logged in to Quay with credentials/token that has push access to that namespace/repo.
  - Re-run with `PUSH=1` after updating visibility/permissions.
