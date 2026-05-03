# import libs
import argparse
from typing import Literal
from fastmcp import FastMCP
# local
from pymemsim_mcp.interface.gas_hfm import simulate_gas_hfm
from pymemsim_mcp.interface.resources import (
    GAS_PHASE_REFERENCE_REQUIREMENTS,
    LIQUID_PHASE_REFERENCE_REQUIREMENTS,
)
from pymemsim_mcp.models.refs import MCPHTTPConfig
from pymemsim_mcp.tools.check_reference import check_yaml_reference
from pymemsim_mcp.tools.flow_rate_analyzer import hfm_feed_flow_rate_analyzer


RunMode = Literal["stdio", "http"]

# SECTION: MCP server setup and execution


def create_mcp_server() -> FastMCP:
    mcp = FastMCP("PyMemSim-MCP")

    @mcp.resource(
        uri="pymemsim://references/gas-phase-requirements",
        name="Gas Phase Reference Requirements",
        description=(
            "Thermodynamic data and equation requirements for gas-phase "
            "PyMemSim calculations."
        ),
        mime_type="application/yaml",
        tags={"references", "requirements", "gas-phase"},
    )
    def get_gas_phase_reference_requirements() -> str:
        return GAS_PHASE_REFERENCE_REQUIREMENTS

    @mcp.resource(
        uri="pymemsim://references/liquid-phase-requirements",
        name="Liquid Phase Reference Requirements",
        description=(
            "Thermodynamic data and equation requirements for liquid-phase "
            "PyMemSim calculations."
        ),
        mime_type="application/yaml",
        tags={"references", "requirements", "liquid-phase"},
    )
    def get_liquid_phase_reference_requirements() -> str:
        return LIQUID_PHASE_REFERENCE_REQUIREMENTS

    mcp.tool(
        simulate_gas_hfm,
        description=(
            "run a gas hollow-fiber membrane simulation, using pyThermoDB YAML reference content to build the model source."
        ),
    )
    mcp.tool(
        check_yaml_reference,
        description="Validate pythermodb YAML reference content for use with pyThermoDB.",
    )
    mcp.tool(
        hfm_feed_flow_rate_analyzer,
        description=(
            "analyze recommended feed flow rate bounds for a hollow-fiber membrane "
            "module from geometry, operating conditions, and permeance inputs."
        ),
    )
    return mcp

# SECTION: MCP server execution


def run_mcp(
        mode: RunMode = "stdio",
        http_config: MCPHTTPConfig | None = None
) -> None:
    mcp = create_mcp_server()
    if mode == "stdio":
        mcp.run()
        return

    config = http_config or MCPHTTPConfig()
    mcp.run(transport="http", host=config.host,
            port=config.port, path=config.path)


# SECTION: Main execution
def main() -> None:
    parser = argparse.ArgumentParser(description="Run PyMemSim MCP server.")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default="stdio",
        help="MCP transport mode.",
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="HTTP host (http mode only).")
    parser.add_argument("--port", type=int, default=8000,
                        help="HTTP port (http mode only).")
    parser.add_argument("--path", default="/mcp",
                        help="HTTP path (http mode only).")
    args = parser.parse_args()

    if args.mode == "http":
        run_mcp(
            mode="http",
            http_config=MCPHTTPConfig(
                host=args.host, port=args.port, path=args.path),
        )
        return

    run_mcp(mode="stdio")


if __name__ == "__main__":
    main()
