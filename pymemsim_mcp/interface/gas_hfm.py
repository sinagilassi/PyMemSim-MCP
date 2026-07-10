from typing import Any

from pymemsim import HFM, create_hfm_module

from pymemsim_mcp.interface.gas_hfm_builder import (
    build_hfm_thermo_source,
    build_model_inputs,
    build_unit_options,
)
from pymemsim_mcp.interface.gas_hfm_helpers import component_id
from pymemsim_mcp.interface.gas_hfm_models import GasHFMSimulationRequest
from pymemsim_mcp.interface.gas_hfm_response import analyze_result, failure_response
from pymemsim_mcp.interface.gas_hfm_validation import validate_request
from pymemsim_mcp.tools.model_source_builder import build_model_source_from_reference


def simulate_gas_hfm(request: GasHFMSimulationRequest) -> dict[str, Any]:
    """
    Run a gas hollow-fiber membrane simulation from reference content.

    Input modes
    - Feed specification (choose one mode):
      1. Component-wise feed flows:
         - `feed_inlet_flows` (must include all component ids).
         - Do not also provide `feed_inlet_flow`, `feed_volumetric_flow`, or
           `feed_mole_fractions`.
      2. Total feed flow + composition:
         - Total flow from either:
           - `feed_inlet_flow` (molar flow), or
           - `feed_volumetric_flow` (converted internally to mol/s).
         - Composition from either:
           - `feed_mole_fractions` (must include all component ids), or
           - `components[*].mole_fraction` (must sum to 1.0).

    - Membrane sizing (choose one):
      1. `membrane_area_per_length`, or
      2. `module_geometry`.
      Providing both or neither is treated as invalid input.

    Optional operating inputs
    - `permeate_inlet_temperature`, `permeate_pressure`,
      `permeate_inlet_flows` (if provided, must include all component ids).
    - `overall_heat_transfer_coefficient`, `q_ext_feed`, `q_ext_permeate`,
      `solver_options`, and `target_component`.

    Returns
    - A JSON-safe dict with:
      - `success`, `message`
      - `span`, `state`
      - `analysis`
      - `warnings`
    - On validation/runtime failure, returns `success=False` with a diagnostic
      `message` and optional `warnings`.
    """
    validation_error = validate_request(request)
    if validation_error is not None:
        return validation_error

    model_source = build_model_source_from_reference(
        components=request.components,
        reference_content=request.reference_content,
        ignore_state_props=request.ignore_state_props,
    )
    if model_source is None:
        return failure_response("Model source could not be built from reference_content.")

    warnings: list[str] = []
    target_component = request.target_component or component_id(request.components[0])
    unit_options = build_unit_options(request)
    model_inputs = build_model_inputs(request)

    try:
        thermo_source = build_hfm_thermo_source(request, model_source, unit_options)
        hfm_module: HFM = create_hfm_module(
            model_inputs=model_inputs,
            thermo_source=thermo_source,
        )
        simulation_results = hfm_module.simulate(
            length_span=request.length_span,
            solver_options=request.solver_options,
            mode=request.simulation_mode,
        )
        if simulation_results is None:
            return failure_response("Simulation failed and returned None.", warnings=warnings)

        return analyze_result(
            simulation_results=simulation_results,
            hfm_module=hfm_module,
            target_component=target_component,
            warnings=warnings,
        )
    except Exception as exc:
        return failure_response(str(exc), warnings=warnings)
