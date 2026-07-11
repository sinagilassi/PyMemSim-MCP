import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from pymemsim_mcp.interface.gas_hfm import simulate_gas_hfm  # noqa: E402
from pymemsim_mcp.interface.gas_hfm_models import GasHFMSimulationRequest  # noqa: E402


CASE_ID = "case-1"
VALIDATION_RESULT_DIR = Path(__file__).resolve().parent / "validation result"
FLOWRATES_PATH = VALIDATION_RESULT_DIR / "flowrates.json"
DEFAULT_OUTPUT_PATH = VALIDATION_RESULT_DIR / "case-1-result.json"

PERMEANCE_BY_TEMPERATURE = {
    298.15: {
        "CO2-g": {"value": 9.43, "unit": "GPU"},
        "CH4-g": {"value": 2.63, "unit": "GPU"},
    },
    338.15: {
        "CO2-g": {"value": 17.98, "unit": "GPU"},
        "CH4-g": {"value": 6.21, "unit": "GPU"},
    },
}


def load_reference_content() -> str:
    module_path = Path(__file__).resolve().parent / "reference.py"
    spec = importlib.util.spec_from_file_location("case_1_reference", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load reference module from: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference_content = getattr(module, "REFERENCE_CONTENT", None)
    if not isinstance(reference_content, str) or len(reference_content.strip()) == 0:
        raise ValueError("REFERENCE_CONTENT must be a non-empty string in examples/reference.py")
    return sanitize_reference_content(reference_content)


def sanitize_reference_content(reference_content: str) -> str:
    reference_data = yaml.safe_load(reference_content)
    tables = reference_data["REFERENCES"]["CUSTOM-REF-1"]["TABLES"]
    tables.pop("gas-viscosity-data", None)
    tables.pop("liquid-viscosity-data", None)
    return yaml.safe_dump(reference_data, sort_keys=False)


def load_case_flowrate() -> dict[str, Any]:
    flowrates = json.loads(FLOWRATES_PATH.read_text(encoding="utf-8"))
    case_flowrate = flowrates["cases"][CASE_ID]["feed_volumetric_flow"]
    if case_flowrate["value"] is None:
        raise ValueError(f"No feed flow rate configured for {CASE_ID} in {FLOWRATES_PATH}")
    return case_flowrate


def build_request(reference_content: str, temperature: float) -> dict[str, Any]:
    if temperature not in PERMEANCE_BY_TEMPERATURE:
        supported = ", ".join(str(value) for value in sorted(PERMEANCE_BY_TEMPERATURE))
        raise ValueError(f"Unsupported temperature {temperature}. Supported temperatures: {supported}")

    return {
        "reference_content": reference_content,
        "ignore_state_props": [
            "Cp_LIQ",
            "VaPr",
            "EnVap",
            "rho_LIQ",
            "Vis_GAS",
            "gas-viscosity",
        ],
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
        "feed_volumetric_flow": load_case_flowrate(),
        "feed_inlet_temperature": {"value": temperature, "unit": "K"},
        "feed_pressure": {"value": 401.3, "unit": "kPa"},
        "permeate_inlet_temperature": {"value": temperature, "unit": "K"},
        "permeate_pressure": {"value": 101.3, "unit": "kPa"},
        "gas_transport_coefficients": PERMEANCE_BY_TEMPERATURE[temperature],
        "module_geometry": {
            "number_of_fibers": {"value": 100, "unit": ""},
            "fiber_outer_diameter": {"value": 0.0735, "unit": "cm"},
            "fiber_inner_diameter": {"value": 0.0389, "unit": "cm"},
            "fiber_length": {"value": 15, "unit": "cm"},
            "module_diameter": {"value": 1, "unit": "cm"},
        },
        "overall_heat_transfer_coefficient": {"value": 0.0, "unit": "W/m2.K"},
        "q_ext_feed": {"value": 0.0, "unit": "W/m2"},
        "q_ext_permeate": {"value": 0.0, "unit": "W/m2"},
        "heat_transfer_options": {
            "heat_transfer_mode": "isothermal",
        },
        "modeling_type": "scale",
        "flow_pattern": "co-current",
        "feed_pressure_mode": "constant",
        "permeate_pressure_mode": "constant",
        "gas_model": "ideal",
        "gas_heat_capacity_mode": "temperature-dependent",
        "ideal_gas_formation_enthalpy_mode": "model_source",
        "molecular_weight_mode": "model_source",
        "reaction_enthalpy_mode": "ideal_gas",
        "length_span": [0.0, 0.15],
        "solver_options": {
            "rtol": 1e-6,
            "atol": 1e-9,
        },
        "target_component": "CO2-g",
        "simulation_mode": "silent",
    }


def run_case(temperatures: list[float]) -> dict[str, Any]:
    reference_content = load_reference_content()
    simulations: dict[str, Any] = {}

    for temperature in temperatures:
        request_data = build_request(reference_content, temperature)
        request = GasHFMSimulationRequest(**request_data)
        simulations[f"{temperature:.2f} K"] = simulate_gas_hfm(request)

    return {
        "case": CASE_ID,
        "source": "examples/case-1.md",
        "assumptions": {
            "feed_volumetric_flow_source": str(FLOWRATES_PATH.relative_to(PROJECT_DIR)),
            "number_of_elements": "30 documented in case-1.md; current co-current IVP solver uses adaptive points",
            "packing_fraction": "documented in case-1.md but not accepted by the current module_geometry schema",
        },
        "simulations": simulations,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run validation simulation for examples/case-1.md.")
    parser.add_argument(
        "--temperature",
        type=float,
        choices=sorted(PERMEANCE_BY_TEMPERATURE),
        action="append",
        help="Temperature in K to run. Repeat to run multiple endpoints. Defaults to both case endpoints.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path for the complete JSON result. Defaults to validation result/case-1-result.json.",
    )
    parser.add_argument(
        "--print-full",
        action="store_true",
        help="Print the complete simulation JSON to stdout in addition to saving it.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    temperatures = args.temperature or sorted(PERMEANCE_BY_TEMPERATURE)
    result = run_case(temperatures)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if args.print_full:
        print(json.dumps(result, indent=2))
        return

    summary = {
        "case": result["case"],
        "output": str(args.output),
        "simulations": {
            temperature: {
                "success": simulation["success"],
                "message": simulation["message"],
                "stage_cut_molar": simulation.get("analysis", {})
                .get("performance", {})
                .get("stage_cut_molar"),
                "purity_permeate_target": simulation.get("analysis", {})
                .get("performance", {})
                .get("purity_permeate_target"),
                "recovery_permeate_target": simulation.get("analysis", {})
                .get("performance", {})
                .get("recoveries_permeate", {})
                .get("CO2-g"),
            }
            for temperature, simulation in result["simulations"].items()
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
