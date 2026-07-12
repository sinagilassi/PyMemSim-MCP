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
        choose_one:
          - membrane_area_per_length
          - full geometry keys
          - module_geometry
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
    missing_feed_total_or_composition: Provide feed_inlet_flow plus feed_mole_fractions, or feed_inlet_flows.
    mixed_feed_modes: Use feed_inlet_flows or total-flow plus composition, not both.
    missing_transport: Add every component to gas_transport_coefficients.
    missing_geometry: Add full geometry keys or module_geometry when feed_pressure_mode or permeate_pressure_mode is state_variable.
    missing_viscosity: Add Vis_GAS to model_source when any pressure side uses state_variable.
    missing_heat_capacity: Add Cp_IG to model_source when heat_transfer_mode is non-isothermal.
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
