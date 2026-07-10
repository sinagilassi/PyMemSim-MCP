from typing import Any

from pymemsim.models import HollowFiberMembraneOptions
from pymemsim.thermo import build_thermo_source
from pymemsim.utils import Q_std_to_mol_s

from pymemsim_mcp.interface.gas_hfm_helpers import feed_mole_fractions, normalize_flow_pattern
from pymemsim_mcp.interface.gas_hfm_models import GasHFMSimulationRequest


def build_unit_options(request: GasHFMSimulationRequest) -> HollowFiberMembraneOptions:
    return HollowFiberMembraneOptions(
        modeling_type="scale",
        phase="gas",
        feed_pressure_mode="constant",
        permeate_pressure_mode="constant",
        gas_model="ideal",
        flow_pattern=normalize_flow_pattern(request.flow_pattern),
    )


def build_model_inputs(request: GasHFMSimulationRequest) -> dict[str, Any]:
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
            model_inputs["feed_inlet_flow"] = Q_std_to_mol_s(request.feed_volumetric_flow)
        model_inputs["feed_mole_fractions"] = feed_mole_fractions(request)

    if request.permeate_inlet_flows is not None:
        model_inputs["permeate_inlet_flows"] = request.permeate_inlet_flows

    if request.membrane_area_per_length is not None:
        model_inputs["membrane_area_per_length"] = request.membrane_area_per_length
    else:
        model_inputs["module_geometry"] = request.module_geometry

    return model_inputs


def build_hfm_thermo_source(
    request: GasHFMSimulationRequest, model_source: Any, unit_options: Any
) -> Any:
    return build_thermo_source(
        components=request.components,
        model_source=model_source,
        thermo_inputs=request.thermo_inputs,
        unit_options=unit_options,
        heat_transfer_options=request.heat_transfer_options,
        reaction_rates=[],
        component_key="Name-Formula",
    )
