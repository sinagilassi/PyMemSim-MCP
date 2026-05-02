# import libs


# SECTION: Gas-phase reference requirements
GAS_PHASE_REFERENCE_REQUIREMENTS = """
# PyMemSim Gas-Phase Reference Requirements

For gas-phase PyMemSim calculations, the reference-making agent must provide the following thermodynamic data and equations.

## Required data tables

- general-data

## Required general-data fields

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

## Required equation tables

- ideal-gas-heat-capacity (Cp_IG)
- vapor-pressure (VaPr)
"""

# SECTION: Liquid-phase reference requirements
LIQUID_PHASE_REFERENCE_REQUIREMENTS = """
# PyMemSim Liquid-Phase Reference Requirements

For liquid-phase PyMemSim calculations, the reference-making agent must provide the following thermodynamic data and equations.

## Required data tables

- general-data

## Required general-data fields

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

## Required equation tables

- ideal-gas-heat-capacity (Cp_IG)
- vapor-pressure (VaPr)
- liquid-heat-capacity (Cp_LIQ)
- liquid-density (rho_LIQ)
- enthalpy-of-vaporization (EnVap)
"""
