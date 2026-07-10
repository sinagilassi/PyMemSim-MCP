from typing import Any

import numpy as np

from pymemsim_mcp.interface.gas_hfm_helpers import component_ids, missing_component_keys
from pymemsim_mcp.interface.gas_hfm_models import GasHFMSimulationRequest
from pymemsim_mcp.interface.gas_hfm_response import failure_response


def validate_gas_transport(
    request: GasHFMSimulationRequest, required_component_ids: list[str]
) -> dict[str, Any] | None:
    missing_transport = missing_component_keys(
        set(request.gas_transport_coefficients.keys()),
        request.components,
    )
    if len(missing_transport) == 0:
        return None
    return failure_response(
        "Missing gas transport coefficients.",
        warnings=[
            "gas_transport_coefficients must include every component id: "
            f"{required_component_ids}. Missing: {missing_transport}."
        ],
    )


def validate_feed_inputs(
    request: GasHFMSimulationRequest, required_component_ids: list[str]
) -> dict[str, Any] | None:
    if request.feed_inlet_flows is not None:
        missing_feed_flows = missing_component_keys(
            set(request.feed_inlet_flows.keys()),
            request.components,
        )
        if len(missing_feed_flows) > 0:
            return failure_response(
                "Missing feed inlet flow entries.",
                warnings=[
                    "feed_inlet_flows must include every component id: "
                    f"{required_component_ids}. Missing: {missing_feed_flows}."
                ],
            )
        return None

    if request.feed_inlet_flow is None and request.feed_volumetric_flow is None:
        return failure_response(
            "Feed total flow is missing.",
            warnings=[
                "Provide feed_inlet_flows, or provide feed_inlet_flow or "
                "feed_volumetric_flow with feed composition."
            ],
        )

    if request.feed_mole_fractions is not None:
        missing_feed_fractions = missing_component_keys(
            set(request.feed_mole_fractions.keys()),
            request.components,
        )
        if len(missing_feed_fractions) > 0:
            return failure_response(
                "Missing feed mole fraction entries.",
                warnings=[
                    "feed_mole_fractions must include every component id: "
                    f"{required_component_ids}. Missing: {missing_feed_fractions}."
                ],
            )
        return None

    mole_fraction_sum = sum(float(component.mole_fraction) for component in request.components)
    if mole_fraction_sum <= 0.0:
        return failure_response(
            "Feed composition is missing.",
            warnings=[
                "Provide feed_mole_fractions or set positive Component.mole_fraction "
                "values that sum to 1.0."
            ],
        )
    if not np.isclose(mole_fraction_sum, 1.0, rtol=1e-6, atol=1e-8):
        return failure_response(
            "Component mole fractions must sum to 1.0.",
            warnings=[
                "When feed_mole_fractions is omitted, Component.mole_fraction "
                f"values are used and must sum to 1.0. Current sum: {mole_fraction_sum}."
            ],
        )
    return None


def validate_membrane_inputs(request: GasHFMSimulationRequest) -> dict[str, Any] | None:
    if request.membrane_area_per_length is None and request.module_geometry is None:
        return failure_response(
            "Membrane sizing is missing.",
            warnings=["Provide membrane_area_per_length or module_geometry."],
        )
    if request.membrane_area_per_length is not None and request.module_geometry is not None:
        return failure_response(
            "Ambiguous membrane sizing.",
            warnings=["Provide either membrane_area_per_length or module_geometry, not both."],
        )
    return None


def validate_ambiguous_inputs(request: GasHFMSimulationRequest) -> dict[str, Any] | None:
    if request.feed_inlet_flows is not None and (
        request.feed_inlet_flow is not None
        or request.feed_volumetric_flow is not None
        or request.feed_mole_fractions is not None
    ):
        return failure_response(
            "Ambiguous feed specification.",
            warnings=[
                "Use either feed_inlet_flows or total-flow plus composition inputs, not both.",
            ],
        )
    if request.feed_inlet_flow is not None and request.feed_volumetric_flow is not None:
        return failure_response(
            "Ambiguous feed total flow.",
            warnings=["Provide either feed_inlet_flow or feed_volumetric_flow, not both."],
        )
    return None


def validate_permeate_inputs(
    request: GasHFMSimulationRequest, required_component_ids: list[str]
) -> dict[str, Any] | None:
    if request.permeate_inlet_flows is None:
        return None
    missing_permeate_flows = missing_component_keys(
        set(request.permeate_inlet_flows.keys()),
        request.components,
    )
    if len(missing_permeate_flows) == 0:
        return None
    return failure_response(
        "Missing permeate inlet flow entries.",
        warnings=[
            "permeate_inlet_flows must include every component id: "
            f"{required_component_ids}. Missing: {missing_permeate_flows}."
        ],
    )


def validate_request(request: GasHFMSimulationRequest) -> dict[str, Any] | None:
    if len(request.components) == 0:
        return failure_response("At least one component is required.")

    required_component_ids = component_ids(request.components)
    validation_steps = (
        validate_gas_transport(request, required_component_ids),
        validate_feed_inputs(request, required_component_ids),
        validate_membrane_inputs(request),
        validate_ambiguous_inputs(request),
        validate_permeate_inputs(request, required_component_ids),
    )
    for step in validation_steps:
        if step is not None:
            return step
    return None
