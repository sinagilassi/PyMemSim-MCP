# import libs
from typing import Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP

from pythermodb_settings.models import CustomProp, Temperature, Component
from pymemsim import HFM, create_hfm_module
from pymemsim.thermo import build_thermo_source
from pymemsim.models import (
    HeatTransferOptions,
    HollowFiberMembraneOptions,
    HollowFiberMembraneModuleGeometry,
)
from pymemsim.utils import analyze_hfm_result


mcp = FastMCP("PyMemSim-MCP")


# -----------------------------
# Generic unit-aware input
# -----------------------------
class PropInput(BaseModel):
    value: float
    unit: str = Field(...,
                      description="Physical unit, e.g. mol/s, K, kPa, GPU, cm")


class HFMGeometryInput(BaseModel):
    number_of_fibers: PropInput
    fiber_length: PropInput
    fiber_inner_diameter: PropInput
    fiber_outer_diameter: PropInput
    module_diameter: PropInput


class GasHFMSimulationInput(BaseModel):
    reference_content: str = Field(
        ...,
        description=(
            "Reference text/YAML/JSON content used to build model_source. "
            "This contains thermodynamic data_source and equation_source."
        ),
    )

    components: list[Component] = Field(
        ...,
        description="Component keys used by PyMemSim, e.g. ['CO2-g', 'CH4-g']",
    )

    feed_inlet_flow: PropInput
    feed_mole_fractions: dict[str, PropInput]
    feed_inlet_temperature: PropInput
    feed_pressure: PropInput

    permeate_inlet_temperature: PropInput
    permeate_pressure: PropInput

    gas_transport_coefficients: dict[str, PropInput]

    module_geometry: HFMGeometryInput

    overall_heat_transfer_coefficient: PropInput = PropInput(
        value=20.0, unit="W/m2.K")
    q_ext_feed: PropInput = PropInput(value=0.0, unit="W/m2")
    q_ext_permeate: PropInput = PropInput(value=0.0, unit="W/m2")

    flow_pattern: Literal["co-current", "counter-current"] = "counter-current"
    countercurrent_method: Literal["bvp", "shooting"] = "bvp"

    length_start: float = 0.0
    length_end: float = 0.15
    target_component: str = "CO2-g"


def to_custom_prop(x: PropInput) -> CustomProp:
    return CustomProp(value=x.value, unit=x.unit)


def to_temperature(x: PropInput) -> Temperature:
    return Temperature(value=x.value, unit=x.unit)


def build_model_source_from_reference(reference_content: str):
    """
    Replace this with your PyThermoLinkDB logic.

    Example idea:
        model_source = PyThermoLinkDB.from_yaml(reference_content)
        return model_source
    """
    raise NotImplementedError(
        "Connect this function to PyThermoLinkDB to convert reference_content into model_source."
    )


@mcp.tool
def simulate_gas_hfm_with_model_source(input_data: GasHFMSimulationInput) -> dict:
    """
    Simulate gas separation in a hollow-fiber membrane module using PyMemSim.

    The LLM provides:
    - reference_content as a string
    - conventional HFM operating inputs
    - membrane geometry
    - gas permeance data

    The server converts reference_content into model_source, builds thermo_source,
    creates the HFM module, runs the solver, and returns compact analysis.
    """

    model_source = build_model_source_from_reference(
        input_data.reference_content)

    heat_transfer_options = HeatTransferOptions(
        heat_transfer_mode="isothermal",
        heat_transfer_coefficient=CustomProp(value=100.0, unit="W/m2.K"),
        heat_transfer_area=CustomProp(value=2.0, unit="m2"),
        jacket_temperature=Temperature(value=330.0, unit="K"),
    )

    unit_options = HollowFiberMembraneOptions(
        modeling_type="scale",
        phase="gas",
        feed_pressure_mode="constant",
        permeate_pressure_mode="constant",
        gas_model="ideal",
        flow_pattern=input_data.flow_pattern,
    )

    module_geometry = HollowFiberMembraneModuleGeometry(
        number_of_fibers=to_custom_prop(
            input_data.module_geometry.number_of_fibers),
        fiber_length=to_custom_prop(input_data.module_geometry.fiber_length),
        fiber_inner_diameter=to_custom_prop(
            input_data.module_geometry.fiber_inner_diameter),
        fiber_outer_diameter=to_custom_prop(
            input_data.module_geometry.fiber_outer_diameter),
        module_diameter=to_custom_prop(
            input_data.module_geometry.module_diameter),
    )

    model_inputs = {
        "feed_inlet_flow": to_custom_prop(input_data.feed_inlet_flow),
        "feed_mole_fractions": {
            k: to_custom_prop(v) for k, v in input_data.feed_mole_fractions.items()
        },
        "feed_inlet_temperature": to_temperature(input_data.feed_inlet_temperature),
        "feed_pressure": to_custom_prop(input_data.feed_pressure),

        "permeate_inlet_temperature": to_temperature(input_data.permeate_inlet_temperature),
        "permeate_pressure": to_custom_prop(input_data.permeate_pressure),

        "module_geometry": module_geometry,

        "overall_heat_transfer_coefficient": to_custom_prop(
            input_data.overall_heat_transfer_coefficient
        ),
        "q_ext_feed": to_custom_prop(input_data.q_ext_feed),
        "q_ext_permeate": to_custom_prop(input_data.q_ext_permeate),

        "gas_transport_coefficients": {
            k: to_custom_prop(v)
            for k, v in input_data.gas_transport_coefficients.items()
        },
    }

    thermo_source = build_thermo_source(
        components=input_data.components,
        model_source=model_source,
        thermo_inputs={},
        unit_options=unit_options,
        heat_transfer_options=heat_transfer_options,
        reaction_rates=[],
        component_key="Name-Formula",
    )

    hfm_module: HFM = create_hfm_module(
        model_inputs=model_inputs,
        thermo_source=thermo_source,
    )

    if input_data.flow_pattern == "co-current":
        solver_options = {
            "method": "Radau",
            "rtol": 1e-6,
            "atol": 1e-9,
        }
    elif input_data.countercurrent_method == "bvp":
        solver_options = {
            "countercurrent_solver": "bvp",
            "mesh_points": 120,
            "tol": 1e-3,
            "bc_tol": 1e-3,
            "max_nodes": 50000,
            "verbose": 0,
            "debug_bc": False,
        }
    else:
        solver_options = {
            "countercurrent_solver": "shooting",
            "shooting_ivp_method": "auto",
            "shooting_ivp_rtol": 1e-6,
            "shooting_ivp_atol": 1e-9,
            "shooting_max_nfev": 1200,
            "shooting_ftol": 1e-8,
            "shooting_xtol": 1e-8,
            "shooting_gtol": 1e-8,
            "shooting_residual_tol": 1e-3,
            "shooting_multistart": True,
            "shooting_penalty": 1e3,
            "shooting_debug": False,
        }

    result = hfm_module.simulate(
        length_span=(input_data.length_start, input_data.length_end),
        solver_options=solver_options,
        mode="log",
    )

    if result is None:
        return {
            "success": False,
            "message": "Simulation failed and returned None.",
        }

    analysis = analyze_hfm_result(
        result=result,
        hfm_module=hfm_module,
        target_component=input_data.target_component,
    )

    return {
        "success": result.success,
        "message": result.message,
        "span_points": len(result.span),
        "state_shape": list(result.state.shape),
        "analysis": analysis,
    }


if __name__ == "__main__":
    mcp.run()
