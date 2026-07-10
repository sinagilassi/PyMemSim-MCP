import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from pymemsim_mcp.server import create_mcp_server  # noqa: E402


def _load_reference_from_module(module_path: Path) -> str:
    spec = importlib.util.spec_from_file_location("mcp_example_reference", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference_content = getattr(module, "REFERENCE_CONTENT", None)
    if not isinstance(reference_content, str) or len(reference_content.strip()) == 0:
        raise ValueError("REFERENCE_CONTENT must be a non-empty string in examples/reference.py")
    return reference_content


def load_reference_content(path: str | None) -> str:
    if path is not None:
        return Path(path).read_text(encoding="utf-8")

    default_module_path = Path(__file__).resolve().parent / "reference.py"
    return _load_reference_from_module(default_module_path)


def build_request(reference_content: str) -> dict[str, Any]:
    return {
        "reference_content": reference_content,
        "ignore_state_props": ["Cp_LIQ", "VaPr", "EnVap", "rho_LIQ"],
        "components": [
            {
                "name": "carbon dioxide",
                "formula": "CO2",
                "state": "g",
                "mole_fraction": 0.6,
            },
            {
                "name": "methane",
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
        "modeling_type": "scale",
        "flow_pattern": "counter-current",
        "feed_pressure_mode": "constant",
        "permeate_pressure_mode": "constant",
        "gas_model": "ideal",
        "gas_heat_capacity_mode": "temperature-dependent",
        "ideal_gas_formation_enthalpy_mode": "model_source",
        "molecular_weight_mode": "model_source",
        "reaction_enthalpy_mode": "ideal_gas",
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
        help="Optional path to a text file containing reference_content. If omitted, examples/reference.py is used.",
    )
    args = parser.parse_args()

    request = build_request(load_reference_content(args.reference))

    mcp_server = create_mcp_server()
    async with Client(mcp_server) as client:
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
