# SECTION: Gas-phase HFM reference and scenario requirements
GAS_PHASE_REFERENCE_REQUIREMENTS = """
reference_requirements:
  name: PyMemSim Gas-Phase HFM Scenario Requirements
  phase: gas
  purpose: >
    Use this guide to decide which reference data, thermo_inputs, and
    model inputs are required before running simulate_gas_hfm. Component
    dictionaries use formula-state labels derived from components, such as
    CO2-g, CH4-g, O2-g, and N2-g.

  current_limitations:
    - gas_model should be ideal; real gas paths are type-accepted but not ready for practical simulation.
    - counter-current simulation is implemented for gas modules.
    - molecular weights are loaded from model_source in the current source path.
    - heat-capacity mode differential is type-accepted but current paths explicitly support constant and temperature-dependent modes.

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
              - feed_inlet_flow or feed_volumetric_flow
              - feed_mole_fractions or Component.mole_fraction values summing to 1.0
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
        accepted_units:
          - GPU
          - gas permeation unit
          - mol/s.m2.Pa
      sizing:
        choose_one:
          - membrane_area_per_length
          - module_geometry
      simulation:
        required:
          - flow_pattern
          - length_span
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

  scenario_matrix:
    gas_isothermal_constant_pressure:
      description: Simplest gas HFM workflow.
      model_inputs_required:
        - feed specification
        - feed_inlet_temperature
        - feed_pressure
        - permeate_inlet_temperature if different from feed
        - permeate_pressure if different from feed
        - gas_transport_coefficients
        - membrane_area_per_length or module_geometry
      thermo_inputs_required:
        - none
      model_source_required:
        - MW
      not_required:
        - Cp_IG
        - EnFo_IG
        - Vis_GAS
        - vapor-pressure

    gas_isothermal_variable_pressure:
      description: Gas HFM with feed-side and/or permeate-side pressure drop.
      model_inputs_required:
        - gas isothermal constant-pressure inputs
        - complete module_geometry
      thermo_inputs_required:
        - gas_viscosity only if Vis_GAS is missing from model_source
      model_source_required:
        - MW
        - Vis_GAS unless gas_viscosity is supplied in thermo_inputs
      geometry_rule: Direct membrane_area_per_length alone is not sufficient for pressure-drop cases.

    gas_non_isothermal_constant_pressure:
      description: Gas HFM with feed/permeate temperature states and heat-transfer terms.
      model_inputs_required:
        - gas isothermal constant-pressure inputs
        - overall_heat_transfer_coefficient if side-to-side heat transfer is intended
        - q_ext_feed if external feed heat flux is used
        - q_ext_permeate if external permeate heat flux is used
      heat_transfer_options_required:
        - heat_transfer_mode: non-isothermal
        - heat_transfer_coefficient for global heat exchange when used
        - heat_transfer_area for global heat exchange when used
        - jacket_temperature for global heat exchange when used
      thermo_inputs_required:
        - gas_heat_capacity when gas_heat_capacity_mode is constant
        - ideal_gas_formation_enthalpy when ideal_gas_formation_enthalpy_mode is model_inputs
      model_source_required:
        - MW
        - Cp_IG when gas_heat_capacity_mode is temperature-dependent
        - EnFo_IG when ideal_gas_formation_enthalpy_mode is model_source

    gas_non_isothermal_variable_pressure:
      description: Most data-intensive gas HFM workflow.
      model_inputs_required:
        - gas non-isothermal constant-pressure inputs
        - complete module_geometry
      thermo_inputs_required:
        - gas_heat_capacity when gas_heat_capacity_mode is constant
        - ideal_gas_formation_enthalpy when ideal_gas_formation_enthalpy_mode is model_inputs
        - gas_viscosity only if Vis_GAS is missing from model_source
      model_source_required:
        - MW
        - Vis_GAS unless gas_viscosity is supplied in thermo_inputs
        - Cp_IG when gas_heat_capacity_mode is temperature-dependent
        - EnFo_IG when ideal_gas_formation_enthalpy_mode is model_source

  property_source_matrix:
    MW:
      needed_for:
        - gas volumetric flow
        - mixture properties
        - result analysis
      required_location: model_source
    Vis_GAS:
      needed_for:
        - gas pressure drop when either pressure mode is state_variable
      preferred_location: model_source
      fallback_location: thermo_inputs.gas_viscosity
    Cp_IG:
      needed_for:
        - non-isothermal gas with temperature-dependent heat capacity
      required_location: model_source
    gas_heat_capacity:
      needed_for:
        - non-isothermal gas with constant heat capacity
      required_location: thermo_inputs
    EnFo_IG:
      needed_for:
        - ideal-gas formation enthalpy from model_source
      required_location: model_source
    ideal_gas_formation_enthalpy:
      needed_for:
        - ideal-gas formation enthalpy from user constants
      required_location: thermo_inputs

  thermo_input_formats:
    gas_viscosity:
      CO2-g: {value: 1.48e-5, unit: Pa.s}
      CH4-g: {value: 1.10e-5, unit: Pa.s}
    gas_heat_capacity:
      CO2-g: {value: 37.1, unit: J/mol.K}
      CH4-g: {value: 35.7, unit: J/mol.K}
    ideal_gas_formation_enthalpy:
      CO2-g: {value: -393.5, unit: kJ/mol}
      CH4-g: {value: -74.8, unit: kJ/mol}

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
    missing_feed_total_or_composition: Provide feed_inlet_flow/feed_volumetric_flow plus composition, or feed_inlet_flows.
    mixed_feed_modes: Use feed_inlet_flows or total-flow plus composition, not both.
    missing_transport: Add every component to gas_transport_coefficients.
    missing_geometry: Complete module_geometry is required when a pressure mode is state_variable.
    missing_viscosity: Add Vis_GAS to model_source or gas_viscosity to thermo_inputs.
    missing_heat_capacity: Add Cp_IG to model_source or gas_heat_capacity to thermo_inputs, depending on gas_heat_capacity_mode.
    missing_formation_enthalpy: Add EnFo_IG to model_source or ideal_gas_formation_enthalpy to thermo_inputs, depending on ideal_gas_formation_enthalpy_mode.
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
