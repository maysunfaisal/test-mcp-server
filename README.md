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
