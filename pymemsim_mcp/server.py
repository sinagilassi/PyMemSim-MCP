import argparse
from typing import Literal

from fastmcp import FastMCP

from pymemsim_mcp.interface.gas_hfm import simulate_gas_hfm
from pymemsim_mcp.models.refs import MCPHTTPConfig


RunMode = Literal["stdio", "http"]


def create_mcp_server() -> FastMCP:
    mcp = FastMCP("PyMemSim-MCP")
    mcp.tool(
        simulate_gas_hfm,
        description=(
            "Build a thermodynamic model source from reference content and run a gas "
            "hollow-fiber membrane simulation."
        ),
    )
    return mcp


def run_mcp(mode: RunMode = "stdio", http_config: MCPHTTPConfig | None = None) -> None:
    mcp = create_mcp_server()
    if mode == "stdio":
        mcp.run()
        return

    config = http_config or MCPHTTPConfig()
    mcp.run(transport="http", host=config.host, port=config.port, path=config.path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PyMemSim MCP server.")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default="stdio",
        help="MCP transport mode.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP host (http mode only).")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (http mode only).")
    parser.add_argument("--path", default="/mcp", help="HTTP path (http mode only).")
    args = parser.parse_args()

    if args.mode == "http":
        run_mcp(
            mode="http",
            http_config=MCPHTTPConfig(host=args.host, port=args.port, path=args.path),
        )
        return

    run_mcp(mode="stdio")


if __name__ == "__main__":
    main()
