import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from pymemsim_mcp.app import mcp  # noqa: E402


def load_reference_content(path: str | None) -> str:
    if path is None:
        return "replace this string with valid pyThermoDB reference content"
    return Path(path).read_text(encoding="utf-8")


def build_request(reference_content: str) -> dict[str, Any]:
    return {
        "reference_content": reference_content,
        "components": [
            {
                "name": "Carbon dioxide",
                "formula": "CO2",
                "state": "g",
                "mole_fraction": 0.6,
            },
            {
                "name": "Methane",
                "formula": "CH4",
                "state": "g",
                "mole_fraction": 0.4,
            },
        ],
        "feed_volumetric_flow": {"value": 2.5e-4, "unit": "m3/min"},
        "feed_inlet_temperature": {"value": 338.15, "unit": "K"},
        "feed_pressure": {"value": 405, "unit": "kPa"},
        "permeate_inlet_temperature": {"value": 338.15, "unit": "K"},
        "permeate_pressure": {"value": 101, "unit": "kPa"},
        "gas_transport_coefficients": {
            "CO2-g": {"value": 31.60, "unit": "GPU"},
            "CH4-g": {"value": 8.81, "unit": "GPU"},
        },
        "module_geometry": {
            "number_of_fibers": {"value": 100, "unit": ""},
            "fiber_length": {"value": 15, "unit": "cm"},
            "fiber_inner_diameter": {"value": 0.0389, "unit": "cm"},
            "fiber_outer_diameter": {"value": 0.0735, "unit": "cm"},
            "module_diameter": {"value": 1, "unit": "cm"},
        },
        "overall_heat_transfer_coefficient": {"value": 20.0, "unit": "W/m2.K"},
        "q_ext_feed": {"value": 0.0, "unit": "W/m2"},
        "q_ext_permeate": {"value": 0.0, "unit": "W/m2"},
        "heat_transfer_options": {
            "heat_transfer_mode": "isothermal",
        },
        "flow_pattern": "counter-current",
        "length_span": [0.0, 0.15],
        "solver_options": {
            "countercurrent_solver": "bvp",
            "mesh_points": 120,
            "tol": 1e-3,
            "bc_tol": 1e-3,
            "max_nodes": 50000,
        },
        "target_component": "CO2-g",
        "simulation_mode": "silent",
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference",
        help="Path to a text file containing valid reference_content.",
    )
    args = parser.parse_args()

    request = build_request(load_reference_content(args.reference))

    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("tools:", [tool.name for tool in tools])

        result = await client.call_tool(
            "simulate_gas_hfm",
            {"request": request},
            raise_on_error=False,
        )

    response = result.data
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
