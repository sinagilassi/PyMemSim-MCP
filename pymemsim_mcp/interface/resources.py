# import libs


# SECTION: Gas-phase reference requirements
GAS_PHASE_REFERENCE_REQUIREMENTS = """
reference_requirements:
  name: PyMemSim Gas-Phase Reference Requirements
  phase: gas
  purpose: >
    For gas-phase PyMemSim calculations, the reference must include the
    following thermodynamic data and equations.
  required_data_tables:
    - general-data
  required_general_data_fields:
    - No.
    - Name
    - Formula
    - State
    - critical-temperature
    - critical-pressure
    - critical-molar-volume
    - molecular-weight
    - acentric-factor
    - enthalpy-of-formation
    - gibbs-energy-of-formation
  required_equation_tables:
    - table: ideal-gas-heat-capacity
      symbol: Cp_IG
    - table: vapor-pressure
      symbol: VaPr
"""

# SECTION: Liquid-phase reference requirements
LIQUID_PHASE_REFERENCE_REQUIREMENTS = """
reference_requirements:
  name: PyMemSim Liquid-Phase Reference Requirements
  phase: liquid
  purpose: >
    For liquid-phase PyMemSim calculations, the reference must include the
    following thermodynamic data and equations.
  required_data_tables:
    - general-data
  required_general_data_fields:
    - No.
    - Name
    - Formula
    - State
    - critical-temperature
    - critical-pressure
    - critical-molar-volume
    - molecular-weight
    - acentric-factor
    - enthalpy-of-formation
    - gibbs-energy-of-formation
  required_equation_tables:
    - table: ideal-gas-heat-capacity
      symbol: Cp_IG
    - table: vapor-pressure
      symbol: VaPr
    - table: liquid-heat-capacity
      symbol: Cp_LIQ
    - table: liquid-density
      symbol: rho_LIQ
    - table: enthalpy-of-vaporization
      symbol: EnVap
"""
