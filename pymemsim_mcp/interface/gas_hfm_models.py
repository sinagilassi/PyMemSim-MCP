from typing import Any, Literal

from pydantic import BaseModel, Field
from pythermodb_settings.models import Component, CustomProp, Temperature, Pressure
from pymemsim.models import HeatTransferOptions, HollowFiberMembraneModuleGeometry


FlowPattern = Literal["co-current", "counter-current", "cocurrent", "countercurrent"]


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
