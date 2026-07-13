# SECTION: Gas-phase HFM reference and scenario requirements
GAS_PHASE_REFERENCE_REQUIREMENTS = """
reference_requirements:
  name: PyMemSim Gas-Phase HFM Validation Combinations
  phase: gas
  purpose: >
    Use this guide to decide which model inputs and thermophysical
    properties are required for supported gas-phase HFM simulations across
    flow pattern, heat transfer mode, and feed/permeate pressure handling.
    Component dictionaries use formula-state labels derived from
    components, such as CO2-g, CH4-g, O2-g, and N2-g.

  current_limitations:
    - gas_model accepts ideal and real options, but current thermodynamic flow calculations use ideal-gas behavior in practice.
    - counter-current simulation is implemented for gas modules.
    - For pressure-drop equations, geometry completeness is critical when state_variable pressure mode is enabled on either side.

  component_keys:
    format: "{Formula}-{State}"
    examples:
      - CO2-g
      - CH4-g
      - O2-g
      - N2-g
    rule: Every component-dependent input must include every active component.

  always_required_for_gas_hfm:
    model_inputs:
      feed:
        choose_exactly_one:
          total_flow_plus_composition:
            required:
              - feed_inlet_flow
              - feed_mole_fractions
          component_flows:
            required:
              - feed_inlet_flows
        rules:
          - feed_inlet_flows represents individual molar flowrate entries for every active component.
          - Do not mix feed_inlet_flows with total-flow plus composition inputs.
          - Mole fractions are dimensionless and must include every component.
      operating_conditions:
        required:
          - feed_inlet_temperature
          - feed_pressure
        optional_defaults:
          permeate_inlet_temperature: defaults to feed_inlet_temperature
          permeate_pressure: defaults to feed_pressure
          permeate_inlet_flows: defaults to zero flow for every component
      transport:
        required:
          gas_transport_coefficients: Gas permeance for every gas component.
      sizing:
        constant_pressure_choose_one:
          - membrane_area_per_length
          - module_geometry
        pressure_drop_required:
          - module_geometry
        rules:
          - Provide either membrane_area_per_length or module_geometry, not both.
          - membrane_area_per_length is enough only for constant-pressure simulations.
          - When feed_pressure_mode or permeate_pressure_mode is state_variable, provide complete module_geometry; membrane_area_per_length alone is not sufficient.
      simulation:
        required:
          - flow_pattern
          - heat_transfer_options
    model_source:
      required_general_data_fields:
        - Name
        - Formula
        - State
        - molecular-weight
      required_symbols:
        - MW

  supported_options:
    flow_pattern:
      accepted:
        - co-current
        - counter-current
        - cocurrent
        - countercurrent
      notes:
        - co-current uses an IVP solver.
        - counter-current uses BVP or shooting solver options.
    pressure_modes:
      accepted:
        - constant
        - state_variable
      notes:
        - state_variable adds pressure states and requires complete module_geometry.
    heat_transfer_mode:
      accepted:
        - isothermal
        - non-isothermal

  thermo_property_rules:
    MW:
      requirement: Required in practice for all gas workflows.
    Vis_GAS:
      requirement: Required when any pressure side uses state_variable.
    Cp_IG:
      requirement: Required when heat_transfer_mode is non-isothermal.

  combination_matrix:
    - flow_pattern: co-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: None beyond common set.
      required_thermo_properties: [MW]
    - flow_pattern: co-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS]
    - flow_pattern: co-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS]
    - flow_pattern: co-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS]
    - flow_pattern: co-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: None beyond common set.
      required_thermo_properties: [MW, Cp_IG]
    - flow_pattern: co-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS, Cp_IG]
    - flow_pattern: co-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS, Cp_IG]
    - flow_pattern: co-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS, Cp_IG]
    - flow_pattern: counter-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: None beyond common set.
      required_thermo_properties: [MW]
    - flow_pattern: counter-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS]
    - flow_pattern: counter-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS]
    - flow_pattern: counter-current
      heat_transfer_mode: isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS]
    - flow_pattern: counter-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: None beyond common set.
      required_thermo_properties: [MW, Cp_IG]
    - flow_pattern: counter-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: constant
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS, Cp_IG]
    - flow_pattern: counter-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: constant
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS, Cp_IG]
    - flow_pattern: counter-current
      heat_transfer_mode: non-isothermal
      feed_pressure_mode: state_variable
      permeate_pressure_mode: state_variable
      supported: true
      additional_model_input_requirement: Full geometry required for pressure-drop model.
      required_thermo_properties: [MW, Vis_GAS, Cp_IG]

  property_source_matrix:
    MW:
      needed_for:
        - all gas workflows in practice
      required_location: model_source
    Vis_GAS:
      needed_for:
        - pressure-drop model when feed_pressure_mode or permeate_pressure_mode is state_variable
      required_location: model_source
    Cp_IG:
      needed_for:
        - non-isothermal gas workflows
      required_location: model_source

  solver_guidance:
    co_current:
      typical_solver_options:
        method: Radau
        rtol: 1.0e-6
        atol: 1.0e-9
    counter_current_bvp:
      typical_solver_options:
        countercurrent_solver: bvp
        mesh_points: 30
        tol: 1.0e-2
        bc_tol: 1.0e-2
        max_nodes: 500
    counter_current_shooting:
      typical_solver_options:
        countercurrent_solver: shooting
        shooting_ivp_method: auto
        shooting_residual_tol: 1.0e-3
        shooting_multistart: true

  common_missing_input_diagnostics:
    missing_feed_total_or_composition: Provide feed_inlet_flow plus feed_mole_fractions, or feed_inlet_flows as individual component molar flowrates.
    mixed_feed_modes: Use feed_inlet_flows or total-flow plus composition, not both.
    missing_transport: Add every component to gas_transport_coefficients.
    missing_geometry: Add complete module_geometry when feed_pressure_mode or permeate_pressure_mode is state_variable; membrane_area_per_length alone is not sufficient.
    missing_viscosity: Add Vis_GAS to model_source when any pressure side uses state_variable.
    missing_heat_capacity: Add Cp_IG to model_source when heat_transfer_mode is non-isothermal.

    invalid_components_shape: >
      components must be a list of component dictionaries, not formula-state strings.
      Use entries such as {name: oxygen, formula: O2, state: g, mole_fraction: 0.205}.
      Formula-state labels such as O2-g are derived from these dictionaries and are used
      only as keys in component-dependent inputs.

    invalid_component_keys: >
      feed_mole_fractions, feed_inlet_flows, permeate_inlet_flows, and gas_transport_coefficients
      must be keyed by formula-state labels derived from components, such as O2-g and N2-g.
      Every active component must have a matching key.

    invalid_length_span_shape: >
      length_span must be a two-number list or tuple in meters, for example [0, 0.25].
      Do not pass unit strings such as ["0 m", "0.25 m"] and do not pass CustomProp objects.

    invalid_custom_property_shape: >
      Unit-bearing scalar fields such as feed_inlet_flow, feed_pressure, feed_inlet_temperature,
      permeate_pressure, membrane_area_per_length, and gas_transport_coefficients must use
      {value: <number>, unit: <unit>} objects unless the live schema states otherwise.

    invalid_transport_unit: >
      Gas permeance units must use an accepted unit string. Prefer GPU when source data are
      reported in GPU, or use mol/s.m2.Pa for SI permeance. Avoid alternate spellings such as
      mol/m2.s.Pa unless accepted by the live schema.

    invalid_feed_composition_units: >
      Mole fractions are dimensionless. Use unit: "" or unit: "1" only if accepted by the live
      schema, and ensure mole fractions include every component and sum to 1.0.

    invalid_reference_content_shape: >
      reference_content should be complete pyThermoDB-compatible YAML. If direct table snippets
      fail validation, wrap tables under REFERENCES -> <reference-id> -> DATABOOK-ID -> TABLES
      and validate again with check_yaml_reference.

    ambiguous_membrane_sizing: >
      Provide either membrane_area_per_length or module_geometry, not both. For constant-pressure
      simulations membrane_area_per_length is sufficient; for pressure-drop simulations use
      complete module_geometry.

    pressure_drop_reference_gap: >
      If feed_pressure_mode or permeate_pressure_mode is state_variable, reference_content must
      include gas viscosity requirements such as Vis_GAS in addition to molecular weight.
"""


# SECTION: Liquid-phase HFM reference and scenario requirements
LIQUID_PHASE_REFERENCE_REQUIREMENTS = """
reference_requirements:
  name: PyMemSim Liquid-Phase HFM Scenario Requirements
  phase: liquid
  purpose: >
    Use this guide to decide which reference data, thermo_inputs, and
    model inputs are required for liquid-phase HFM workflows. Liquid HFM
    should currently be treated as co-current and constant-pressure unless
    implementation support is extended.

  current_limitations:
    - liquid HFM workflows should be treated as co-current and constant-pressure.
    - liquid pressure-drop guidance is future-facing unless code support is added.
    - counter-current simulation is implemented for gas modules, not liquid modules.
    - heat-capacity mode differential is type-accepted but current paths explicitly support constant and temperature-dependent modes.
    - molecular weights are loaded from model_source in the current source path.

  component_keys:
    format: "{Formula}-{State}"
    examples:
      - CH3OH-l
      - H2O-l
    rule: Every component-dependent input must include every active component.

  always_required_for_liquid_hfm:
    model_inputs:
      feed:
        choose_exactly_one:
          total_flow_plus_composition:
            required:
              - feed_inlet_flow
              - feed_mole_fractions or Component.mole_fraction values summing to 1.0
          component_flows:
            required:
              - feed_inlet_flows
      operating_conditions:
        required:
          - feed_inlet_temperature
          - feed_pressure
        optional_defaults:
          permeate_inlet_temperature: defaults to feed_inlet_temperature
          permeate_pressure: defaults to feed_pressure
          permeate_inlet_flows: defaults to zero flow for every component
      transport:
        required:
          liquid_transport_coefficients: Liquid membrane mass-transfer coefficient for every liquid component.
        accepted_units:
          - m/s
          - meter per second
      sizing:
        choose_one:
          - membrane_area_per_length
          - module_geometry
    model_source:
      required_general_data_fields:
        - Name
        - Formula
        - State
        - molecular-weight
      required_symbols:
        - MW

  recommended_options:
    flow_pattern: co-current
    feed_pressure_mode: constant
    permeate_pressure_mode: constant
    heat_transfer_mode:
      accepted:
        - isothermal
        - non-isothermal

  scenario_matrix:
    liquid_isothermal_constant_pressure:
      description: Current practical liquid HFM workflow.
      model_inputs_required:
        - feed specification
        - feed_inlet_temperature
        - feed_pressure
        - permeate_inlet_temperature if different from feed
        - permeate_pressure if different from feed
        - liquid_transport_coefficients
        - membrane_area_per_length or module_geometry
      thermo_inputs_required:
        - liquid_density when liquid_density_mode is constant
      model_source_required:
        - MW
        - rho_LIQ when liquid_density_mode is temperature-dependent

    liquid_non_isothermal_constant_pressure:
      description: Liquid HFM with temperature states and heat-transfer terms.
      model_inputs_required:
        - liquid isothermal constant-pressure inputs
        - overall_heat_transfer_coefficient if side-to-side heat transfer is intended
        - q_ext_feed if external feed heat flux is used
        - q_ext_permeate if external permeate heat flux is used
      heat_transfer_options_required:
        - heat_transfer_mode: non-isothermal
        - heat_transfer_coefficient for global heat exchange when used
        - heat_transfer_area for global heat exchange when used
        - jacket_temperature for global heat exchange when used
      thermo_inputs_required:
        - liquid_heat_capacity when liquid_heat_capacity_mode is constant
        - liquid_density when liquid_density_mode is constant
      model_source_required:
        - MW
        - Cp_LIQ when liquid_heat_capacity_mode is temperature-dependent
        - rho_LIQ when liquid_density_mode is temperature-dependent

    liquid_variable_pressure:
      support_status: not_currently_recommended
      description: Treat as future-facing. Use constant pressure for current liquid HFM workflows.
      future_requirements:
        model_inputs:
          - complete module_geometry
        model_source_or_thermo_inputs:
          - Vis_LIQ or liquid_viscosity

  property_source_matrix:
    MW:
      needed_for:
        - liquid volumetric flow
        - mixture properties
      required_location: model_source
    rho_LIQ:
      needed_for:
        - liquid density with temperature-dependent density mode
      required_location: model_source
    liquid_density:
      needed_for:
        - liquid density with constant density mode
      required_location: thermo_inputs
    Cp_LIQ:
      needed_for:
        - non-isothermal liquid with temperature-dependent heat capacity
      required_location: model_source
    liquid_heat_capacity:
      needed_for:
        - non-isothermal liquid with constant heat capacity
      required_location: thermo_inputs
    Vis_LIQ:
      needed_for:
        - liquid mixture-viscosity data
        - future liquid pressure-drop support
      preferred_location: model_source
      fallback_location: thermo_inputs.liquid_viscosity

  thermo_input_formats:
    liquid_density:
      CH3OH-l: {value: 792.0, unit: kg/m3}
      H2O-l: {value: 997.0, unit: kg/m3}
    liquid_heat_capacity:
      CH3OH-l: {value: 81.1, unit: J/mol.K}
      H2O-l: {value: 75.3, unit: J/mol.K}
    liquid_viscosity:
      CH3OH-l: {value: 5.4e-4, unit: Pa.s}
      H2O-l: {value: 8.9e-4, unit: Pa.s}

  common_missing_input_diagnostics:
    missing_feed_total_or_composition: Provide feed_inlet_flow plus composition, or feed_inlet_flows.
    mixed_feed_modes: Use feed_inlet_flows or total-flow plus composition, not both.
    missing_transport: Add every component to liquid_transport_coefficients.
    missing_density: Add rho_LIQ to model_source or liquid_density to thermo_inputs, depending on liquid_density_mode.
    missing_heat_capacity: Add Cp_LIQ to model_source or liquid_heat_capacity to thermo_inputs, depending on liquid_heat_capacity_mode.
    pressure_drop_requested: Liquid pressure-drop workflows should be treated as unsupported/future-facing.
"""
