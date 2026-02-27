#!/usr/bin/env python3
"""
Test MCP Server with tools for testing Lightspeed integration.
Fixes host header validation for Docker-to-host communication.
"""

import logging
import os
import uvicorn
from datetime import datetime
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SERVER_PORT = int(os.environ.get("MCP_SERVER_PORT", "8888"))
AUTH_TOKEN = os.environ.get("MCP_AUTH_TOKEN", "test-secret-token")

# Create MCP server
mcp = FastMCP("test-mcp-server")


@mcp.tool()
def echo(message: str) -> str:
    """Echo back a message - useful for testing connectivity."""
    return f"Echo: {message}"


@mcp.tool()
def get_current_time() -> str:
    """Get the current server time."""
    return datetime.now().isoformat()


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_server_info() -> dict:
    """Get information about this MCP server."""
    return {
        "name": "test-mcp-server",
        "version": "1.0.0",
        "tools": ["echo", "get_current_time", "add_numbers", "get_server_info"],
    }


class AuthMiddleware:
    """
    ASGI middleware that validates Bearer token authentication.
    Returns 401 Unauthorized if the token is missing or invalid.
    """

    def __init__(self, app, token: str):
        self.app = app
        self.token = token

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            method = scope.get("method", "?")
            path = scope.get("path", "?")

            if not auth_header.startswith("Bearer "):
                logger.warning(f"Auth failed: missing or malformed Bearer token - {method} {path}")
                response_body = b'{"error": "Unauthorized"}'
                await send({
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(response_body)).encode()),
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": response_body,
                })
                return

            if auth_header[7:] != self.token:
                logger.warning(f"Auth failed: invalid token - {method} {path}")
                response_body = b'{"error": "Unauthorized"}'
                await send({
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(response_body)).encode()),
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": response_body,
                })
                return

            logger.info(f"Auth successful - {method} {path}")

        await self.app(scope, receive, send)


class HostRewriteMiddleware:
    """
    ASGI middleware that rewrites the Host header to localhost.
    This bypasses MCP SDK's host validation for Docker networking.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Rewrite headers to use localhost
            new_headers = []
            for name, value in scope.get("headers", []):
                if name == b"host":
                    # Replace host.docker.internal with localhost
                    new_headers.append((b"host", f"localhost:{SERVER_PORT}".encode()))
                else:
                    new_headers.append((name, value))
            scope = dict(scope)
            scope["headers"] = new_headers

        await self.app(scope, receive, send)


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     Test MCP Server - Port: {SERVER_PORT}                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Get the ASGI app and wrap it with our middleware
    app = mcp.streamable_http_app()
    app = HostRewriteMiddleware(app)
    app = AuthMiddleware(app, AUTH_TOKEN)

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)