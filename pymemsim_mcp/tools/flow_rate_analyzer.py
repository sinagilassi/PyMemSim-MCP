# import libs
import logging
from typing import Optional, Any, Dict
from pythermodb_settings.models import CustomProp
from pymemsim.utils.hfm_tools import calculate_hfm_feed_flow_rate_bounds

# NOTE: Set up logging
logging.basicConfig(level=logging.INFO)

# SECTION: analyze feed flow rate


def hfm_feed_flow_rate_analyzer(
        number_of_fibers: CustomProp,
        fiber_inner_diameter: CustomProp,
        fiber_outer_diameter: CustomProp,
        fiber_length: CustomProp,
        feed_pressure: CustomProp,
        feed_temperature: CustomProp,
        permeate_pressure: CustomProp,
        viscosity: CustomProp,
        permeance: dict[str, CustomProp],
        feed_mole_fraction: dict[str, CustomProp],
        velocity_min: CustomProp = CustomProp(value=0.01, unit='m/s'),
        velocity_max: CustomProp = CustomProp(value=10.0, unit='m/s'),
        max_pressure_drop: CustomProp = CustomProp(value=20_000.0, unit='Pa'),
        theta_max: float = 0.8,
) -> Optional[Dict[str, Any]]:
    """
    Analyze the feed flow rate for a hollow fiber membrane (HFM) system.

    Parameters
    ----------
    number_of_fibers : CustomProp
        The number of fibers in the HFM system.
    fiber_inner_diameter : CustomProp
        The inner diameter of the fibers.
    fiber_outer_diameter : CustomProp
        The outer diameter of the fibers.
    fiber_length : CustomProp
        The length of the fibers.
    feed_pressure : CustomProp
        The pressure of the feed stream.
    feed_temperature : CustomProp
        The temperature of the feed stream.
    permeate_pressure : CustomProp
        The pressure of the permeate stream.
    viscosity : CustomProp
        The viscosity of the feed stream.
    permeance : dict[str, CustomProp]
        A dictionary containing the permeance values for each component in the feed stream.
    feed_mole_fraction : dict[str, CustomProp]
        A dictionary containing the mole fraction values for each component in the feed stream.
    velocity_min : CustomProp, optional
        The minimum velocity to consider for the analysis (default is 0.01 m/s).
    velocity_max : CustomProp, optional
        The maximum velocity to consider for the analysis (default is 10.0 m/s).
    max_pressure_drop : CustomProp, optional
        The maximum allowable pressure drop across the fibers (default is 20,000 Pa).
    theta_max : float, optional
        The maximum allowable packing density of the fibers (default is 0.8).

    Returns
    -------
    dict[str, any]
        Dictionary containing:
        - ``lumen_cross_section_area`` : total lumen flow area (m2)
        - ``q_min_velocity`` : minimum flow rate from velocity constraint (m3/s)
        - ``q_max_velocity`` : maximum flow rate from velocity constraint (m3/s)
        - ``q_max_pressure_drop`` : maximum flow rate from pressure-drop constraint (m3/s)
        - ``q_min_capacity`` : minimum flow rate from membrane capacity constraint (m3/s)
        - ``q_min_recommended`` : final recommended minimum volumetric flow rate (m3/s)
        - ``q_max_recommended`` : final recommended maximum volumetric flow rate (m3/s)
        - ``f_min_recommended`` : final recommended minimum molar flow rate (mol/s)
        - ``f_max_recommended`` : final recommended maximum molar flow rate (mol/s)
        - ``estimated_total_permeation_capacity`` : total permeation capacity (mol/s)
        - ``estimated_component_capacity`` : per-component permeation capacity (mol/s)
        - ``theta_max`` : stage-cut limit used
        - ``is_feasible_range`` : True if the recommended min < max
    """
    try:
        # Calculate feed flow rate bounds
        res = calculate_hfm_feed_flow_rate_bounds(
            number_of_fibers=number_of_fibers,
            fiber_inner_diameter=fiber_inner_diameter,
            fiber_outer_diameter=fiber_outer_diameter,
            fiber_length=fiber_length,
            feed_pressure=feed_pressure,
            feed_temperature=feed_temperature,
            permeate_pressure=permeate_pressure,
            viscosity=viscosity,
            permeance=permeance,
            feed_mole_fraction=feed_mole_fraction,
            velocity_min=velocity_min,
            velocity_max=velocity_max,
            max_pressure_drop=max_pressure_drop,
            theta_max=theta_max
        )

        # Analyze results and determine feasibility
        return res

    except Exception as e:
        logging.error(
            f"An error occurred during the feed flow rate analysis: {e}")
        return None
