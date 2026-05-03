from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, Field
from pythermodb_settings.models import Component, CustomProp, Temperature, Pressure
from pymemsim import HFM, create_hfm_module
from pymemsim.models import (
    HeatTransferOptions,
    HollowFiberMembraneModuleGeometry,
    HollowFiberMembraneOptions,
)
from pymemsim.thermo import build_thermo_source
from pymemsim.utils import Q_std_to_mol_s, analyze_hfm_result

from pymemsim_mcp.tools.model_source_builder import build_model_source_from_reference


# SECTION: TYPE ALIASES
# NOTE: Accepted flow pattern values from user input.
FlowPattern = Literal["co-current",
                      "counter-current", "cocurrent", "countercurrent"]


# SECTION: BASIC HELPERS
# NOTE: Build a CustomProp from primitive value and unit.
def _custom_prop(value: float | int, unit: str) -> CustomProp:
    return CustomProp(value=value, unit=unit)


# NOTE: Build standard component id key used across dict inputs.
def _component_id(component: Component) -> str:
    return f"{component.formula}-{component.state}"


# NOTE: Normalize flow pattern aliases into canonical values.
def _normalize_flow_pattern(flow_pattern: FlowPattern) -> Literal["co-current", "counter-current"]:
    normalized = flow_pattern.strip().lower().replace("_", "-")
    if normalized in {"cocurrent", "co-current"}:
        return "co-current"
    if normalized in {"countercurrent", "counter-current"}:
        return "counter-current"
    raise ValueError("flow_pattern must be 'co-current' or 'counter-current'.")


# NOTE: Convert numpy/pydantic objects into JSON-safe primitives.
def _json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, BaseModel):
        return _json_safe(value.model_dump())
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return value


# SECTION: REQUEST MODEL
# NOTE: Full request schema for gas HFM simulation.
class GasHFMSimulationRequest(BaseModel):
    reference_content: str = Field(
        ...,
        description="**pythermodb yaml-based reference content** includes thermodynamic data and equations for all components in the simulation",
    )
    ignore_state_props: list[str] | None = Field(
        default=['MW', 'Cp_IG', 'Cp_LIQ', 'VaPr', 'EnVap', 'rho_LIQ'],
        description="State properties to ignore while building component model source.",
    )
    components: list[Component] = Field(
        ...,
        description=(
            "Gas-phase components to include in the membrane simulation to only specify name, formula, and state"
            "e.g. Component(name='carbon dioxide', formula='CO2', state='g')"
        ),
    )
    feed_volumetric_flow: CustomProp | None = Field(
        default=None,
        description=(
            "Optional feed volumetric flow at standard conditions; converted to mol/s internally. Overrides feed_inlet_flow when set."
        ),
    )
    feed_inlet_flows: dict[str, CustomProp] | None = Field(
        default=None,
        description=(
            "Optional component feed inlet flows keyed by component id as `formula-state`, "
            "e.g. `{'CO2-g': {'value': 0.5, 'unit': 'mol/s'}}`. When set, this overrides feed_inlet_flow and feed_volumetric_flow."
        ),
    )
    feed_inlet_flow: CustomProp | None = Field(
        default=None,
        description=(
            "Optional direct feed molar flow. Overrides feed_volumetric_flow when set, and is overridden by feed_inlet_flows when that is set."
            "e.g., CustomProp(value=12, unit='mol/s')"
        ),
    )
    feed_mole_fractions: dict[str, CustomProp] | None = Field(
        default=None,
        description=(
            "Feed mole fractions keyed by component id as `formula-state`, "
            "e.g. `{'CO2-g': {'value': 0.15, 'unit': ''}}`."
        ),
    )
    feed_inlet_temperature: Temperature = Field(
        ...,
        description="Feed inlet temperature.",
    )
    feed_pressure: Pressure = Field(
        ...,
        description="Feed-side pressure.",
    )
    permeate_inlet_temperature: Temperature | None = Field(
        default=None,
        description=(
            "Optional permeate inlet temperature. If omitted, PyMemSim falls back "
            "to the feed inlet temperature."
        ),
    )
    permeate_inlet_flows: dict[str, CustomProp] | None = Field(
        default=None,
        description=(
            "Optional component permeate inlet flows keyed by component id, e.g. CO2-g. "
            "If omitted, PyMemSim uses its default permeate inlet handling."
        ),
    )
    permeate_pressure: Pressure | None = Field(
        default=None,
        description=(
            "Optional permeate-side pressure. If omitted, PyMemSim falls back to "
            "the feed pressure."
        ),
    )
    gas_transport_coefficients: dict[str, CustomProp] = Field(
        ...,
        description=(
            "Gas permeance values keyed by component id as `formula-state`, "
            "e.g. `{'CO2-g': {'value': 32, 'unit': 'GPU'}}`."
        ),
    )
    membrane_area_per_length: CustomProp | None = Field(
        default=None,
        description=(
            "Optional direct membrane area per unit length. When provided, it is used "
            "instead of module_geometry."
        ),
    )
    module_geometry: HollowFiberMembraneModuleGeometry | None = Field(
        default=None,
        description=(
            "Hollow-fiber membrane module geometry. Used when membrane_area_per_length "
            "is not provided."
        ),
    )
    overall_heat_transfer_coefficient: CustomProp | None = Field(
        default=None,
        description=(
            "Optional overall heat-transfer coefficient used by the HFM model. "
            "If omitted, PyMemSim uses 0.0."
        ),
    )
    q_ext_feed: CustomProp | None = Field(
        default=None,
        description="Optional external feed-side heat flux. If omitted, PyMemSim uses 0.0.",
    )
    q_ext_permeate: CustomProp | None = Field(
        default=None,
        description="Optional external permeate-side heat flux. If omitted, PyMemSim uses 0.0.",
    )
    heat_transfer_options: HeatTransferOptions = Field(
        ...,
        description="Thermo-source heat-transfer options.",
    )
    thermo_inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional thermo inputs passed through to build_thermo_source.",
    )
    flow_pattern: FlowPattern = Field(
        ...,
        description="HFM flow pattern.",
    )
    length_span: tuple[float, float] = Field(
        ...,
        description="Simulation axial span in meters.",
    )
    solver_options: dict[str, Any] | None = Field(
        default=None,
        description="Optional solver options passed through to PyMemSim.",
    )
    target_component: str | None = Field(
        default=None,
        description="Component id to use for analysis metrics. Defaults to the first component.",
    )
    simulation_mode: Literal["silent", "log", "attach"] = Field(
        default="silent",
        description="Simulation logging mode passed to hfm_module.simulate to measure computation time",
    )


# SECTION: INPUT NORMALIZATION HELPERS
# NOTE: Resolve feed mole fractions from explicit input or component defaults.
def _feed_mole_fractions(request: GasHFMSimulationRequest) -> dict[str, CustomProp]:
    if request.feed_mole_fractions is not None:
        return request.feed_mole_fractions
    return {
        _component_id(component): _custom_prop(component.mole_fraction, "")
        for component in request.components
    }


# NOTE: Get all component ids in request order.
def _component_ids(components: list[Component]) -> list[str]:
    return [_component_id(component) for component in components]


# NOTE: Return missing keys compared to required component ids.
def _missing_component_keys(keys: set[str], components: list[Component]) -> list[str]:
    return [component_id for component_id in _component_ids(components) if component_id not in keys]


# SECTION: RESPONSE HELPERS
# NOTE: Standard failure payload for all early exits.
def _failure_response(message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "span": [],
        "state": [],
        "analysis": {},
        "warnings": warnings or [],
    }


# SECTION: VALIDATION HELPERS
# NOTE: Validate transport coefficients include all requested components.
def _validate_gas_transport(
    request: GasHFMSimulationRequest, component_ids: list[str]
) -> dict[str, Any] | None:
    missing_transport = _missing_component_keys(
        set(request.gas_transport_coefficients.keys()),
        request.components,
    )
    if len(missing_transport) == 0:
        return None
    return _failure_response(
        "Missing gas transport coefficients.",
        warnings=[
            "gas_transport_coefficients must include every component id: "
            f"{component_ids}. Missing: {missing_transport}."
        ],
    )


# NOTE: Validate feed flow/composition inputs and defaults.
def _validate_feed_inputs(
    request: GasHFMSimulationRequest, component_ids: list[str]
) -> dict[str, Any] | None:
    if request.feed_inlet_flows is not None:
        missing_feed_flows = _missing_component_keys(
            set(request.feed_inlet_flows.keys()),
            request.components,
        )
        if len(missing_feed_flows) > 0:
            return _failure_response(
                "Missing feed inlet flow entries.",
                warnings=[
                    "feed_inlet_flows must include every component id: "
                    f"{component_ids}. Missing: {missing_feed_flows}."
                ],
            )
        return None

    if request.feed_inlet_flow is None and request.feed_volumetric_flow is None:
        return _failure_response(
            "Feed total flow is missing.",
            warnings=[
                "Provide feed_inlet_flows, or provide feed_inlet_flow or "
                "feed_volumetric_flow with feed composition."
            ],
        )

    if request.feed_mole_fractions is not None:
        missing_feed_fractions = _missing_component_keys(
            set(request.feed_mole_fractions.keys()),
            request.components,
        )
        if len(missing_feed_fractions) > 0:
            return _failure_response(
                "Missing feed mole fraction entries.",
                warnings=[
                    "feed_mole_fractions must include every component id: "
                    f"{component_ids}. Missing: {missing_feed_fractions}."
                ],
            )
        return None

    mole_fraction_sum = sum(float(component.mole_fraction)
                            for component in request.components)
    if mole_fraction_sum <= 0.0:
        return _failure_response(
            "Feed composition is missing.",
            warnings=[
                "Provide feed_mole_fractions or set positive Component.mole_fraction "
                "values that sum to 1.0."
            ],
        )
    if not np.isclose(mole_fraction_sum, 1.0, rtol=1e-6, atol=1e-8):
        return _failure_response(
            "Component mole fractions must sum to 1.0.",
            warnings=[
                "When feed_mole_fractions is omitted, Component.mole_fraction "
                f"values are used and must sum to 1.0. Current sum: {mole_fraction_sum}."
            ],
        )
    return None


# NOTE: Validate membrane sizing inputs are present and not ambiguous.
def _validate_membrane_inputs(request: GasHFMSimulationRequest) -> dict[str, Any] | None:
    if request.membrane_area_per_length is None and request.module_geometry is None:
        return _failure_response(
            "Membrane sizing is missing.",
            warnings=["Provide membrane_area_per_length or module_geometry."],
        )
    if request.membrane_area_per_length is not None and request.module_geometry is not None:
        return _failure_response(
            "Ambiguous membrane sizing.",
            warnings=[
                "Provide either membrane_area_per_length or module_geometry, not both."],
        )
    return None


# NOTE: Validate mutually-exclusive feed input combinations.
def _validate_ambiguous_inputs(request: GasHFMSimulationRequest) -> dict[str, Any] | None:
    if request.feed_inlet_flows is not None and (
        request.feed_inlet_flow is not None
        or request.feed_volumetric_flow is not None
        or request.feed_mole_fractions is not None
    ):
        return _failure_response(
            "Ambiguous feed specification.",
            warnings=[
                "Use either feed_inlet_flows or total-flow plus composition inputs, not both.",
            ],
        )
    if request.feed_inlet_flow is not None and request.feed_volumetric_flow is not None:
        return _failure_response(
            "Ambiguous feed total flow.",
            warnings=[
                "Provide either feed_inlet_flow or feed_volumetric_flow, not both."],
        )
    return None


# NOTE: Validate optional permeate inlet flows when provided.
def _validate_permeate_inputs(
    request: GasHFMSimulationRequest, component_ids: list[str]
) -> dict[str, Any] | None:
    if request.permeate_inlet_flows is None:
        return None
    missing_permeate_flows = _missing_component_keys(
        set(request.permeate_inlet_flows.keys()),
        request.components,
    )
    if len(missing_permeate_flows) == 0:
        return None
    return _failure_response(
        "Missing permeate inlet flow entries.",
        warnings=[
            "permeate_inlet_flows must include every component id: "
            f"{component_ids}. Missing: {missing_permeate_flows}."
        ],
    )


# NOTE: Run all request validations and return first failure.
def _validate_request(request: GasHFMSimulationRequest) -> dict[str, Any] | None:
    if len(request.components) == 0:
        return _failure_response("At least one component is required.")

    component_ids = _component_ids(request.components)
    validation_steps = (
        _validate_gas_transport(request, component_ids),
        _validate_feed_inputs(request, component_ids),
        _validate_membrane_inputs(request),
        _validate_ambiguous_inputs(request),
        _validate_permeate_inputs(request, component_ids),
    )
    for step in validation_steps:
        if step is not None:
            return step
    return None


# SECTION: BUILD HELPERS
# NOTE: Build membrane unit options from request settings.
def _build_unit_options(request: GasHFMSimulationRequest) -> HollowFiberMembraneOptions:
    return HollowFiberMembraneOptions(
        modeling_type="scale",
        phase="gas",
        feed_pressure_mode="constant",
        permeate_pressure_mode="constant",
        gas_model="ideal",
        flow_pattern=_normalize_flow_pattern(request.flow_pattern),
    )


# NOTE: Build model input dict expected by PyMemSim module builder.
def _build_model_inputs(request: GasHFMSimulationRequest) -> dict[str, Any]:
    model_inputs: dict[str, Any] = {
        "feed_inlet_temperature": request.feed_inlet_temperature,
        "feed_pressure": request.feed_pressure,
        "gas_transport_coefficients": request.gas_transport_coefficients,
    }
    if request.permeate_inlet_temperature is not None:
        model_inputs["permeate_inlet_temperature"] = request.permeate_inlet_temperature
    if request.permeate_pressure is not None:
        model_inputs["permeate_pressure"] = request.permeate_pressure
    if request.overall_heat_transfer_coefficient is not None:
        model_inputs["overall_heat_transfer_coefficient"] = request.overall_heat_transfer_coefficient
    if request.q_ext_feed is not None:
        model_inputs["q_ext_feed"] = request.q_ext_feed
    if request.q_ext_permeate is not None:
        model_inputs["q_ext_permeate"] = request.q_ext_permeate

    if request.feed_inlet_flows is not None:
        model_inputs["feed_inlet_flows"] = request.feed_inlet_flows
    else:
        if request.feed_inlet_flow is not None:
            model_inputs["feed_inlet_flow"] = request.feed_inlet_flow
        elif request.feed_volumetric_flow is not None:
            model_inputs["feed_inlet_flow"] = Q_std_to_mol_s(
                request.feed_volumetric_flow)
        model_inputs["feed_mole_fractions"] = _feed_mole_fractions(request)

    if request.permeate_inlet_flows is not None:
        model_inputs["permeate_inlet_flows"] = request.permeate_inlet_flows

    if request.membrane_area_per_length is not None:
        model_inputs["membrane_area_per_length"] = request.membrane_area_per_length
    else:
        model_inputs["module_geometry"] = request.module_geometry

    return model_inputs


# NOTE: Build thermo source from model source and thermo options.
def _build_thermo_source(request: GasHFMSimulationRequest, model_source: Any, unit_options: Any) -> Any:
    return build_thermo_source(
        components=request.components,
        model_source=model_source,
        thermo_inputs=request.thermo_inputs,
        unit_options=unit_options,
        heat_transfer_options=request.heat_transfer_options,
        reaction_rates=[],
        component_key="Name-Formula",
    )


# SECTION: POST-PROCESSING
# NOTE: Build final API response from raw simulation result and analysis.
def _analyze_result(
    simulation_results: Any,
    hfm_module: HFM,
    target_component: str,
    warnings: list[str],
) -> dict[str, Any]:
    analysis = analyze_hfm_result(
        result=simulation_results,
        hfm_module=hfm_module,
        target_component=target_component,
    )
    return _json_safe(
        {
            "success": simulation_results.success,
            "message": simulation_results.message,
            "span": simulation_results.span,
            "state": simulation_results.state,
            "analysis": analysis,
            "warnings": warnings + analysis.get("warnings", []),
        }
    )


# SECTION: PUBLIC TOOL
# NOTE: Main entrypoint used by MCP tool registration.
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
    validation_error = _validate_request(request)
    if validation_error is not None:
        return validation_error

    model_source = build_model_source_from_reference(
        components=request.components,
        reference_content=request.reference_content,
        ignore_state_props=request.ignore_state_props,
    )
    if model_source is None:
        return _failure_response("Model source could not be built from reference_content.")

    warnings: list[str] = []
    target_component = request.target_component or _component_id(
        request.components[0])
    unit_options = _build_unit_options(request)
    model_inputs = _build_model_inputs(request)

    try:
        thermo_source = _build_thermo_source(
            request, model_source, unit_options)
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
            return _failure_response("Simulation failed and returned None.", warnings=warnings)

        return _analyze_result(
            simulation_results=simulation_results,
            hfm_module=hfm_module,
            target_component=target_component,
            warnings=warnings,
        )
    except Exception as exc:
        return _failure_response(str(exc), warnings=warnings)
