import argparse
import sys
from pathlib import Path
from typing import Literal


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from pymemsim_mcp.app import mcp  # noqa: E402


Transport = Literal["http", "streamable-http", "sse"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the PyMemSim FastMCP server for external MCP clients.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind. Use 0.0.0.0 for LAN access.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP port.",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="MCP endpoint path.",
    )
    parser.add_argument(
        "--transport",
        choices=["http", "streamable-http", "sse"],
        default="streamable-http",
        help="FastMCP HTTP transport.",
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        help="Run streamable HTTP in stateless mode. Not valid with SSE.",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        help="Uvicorn log level.",
    )
    args = parser.parse_args()

    endpoint = f"http://{args.host}:{args.port}{args.path}"
    print(f"Starting PyMemSim-MCP server at {endpoint}")
    print("External clients should connect to this endpoint as an MCP server.")
    print("Stop the server with Ctrl+C.")

    mcp.run(
        transport=args.transport,
        host=args.host,
        port=args.port,
        path=args.path,
        log_level=args.log_level,
        stateless_http=args.stateless,
    )


if __name__ == "__main__":
    main()
