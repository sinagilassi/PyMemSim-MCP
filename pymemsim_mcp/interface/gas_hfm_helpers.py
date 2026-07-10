from typing import Any, Literal

import numpy as np
from pydantic import BaseModel
from pythermodb_settings.models import Component, CustomProp

from pymemsim_mcp.interface.gas_hfm_models import FlowPattern, GasHFMSimulationRequest


def custom_prop(value: float | int, unit: str) -> CustomProp:
    return CustomProp(value=value, unit=unit)


def component_id(component: Component) -> str:
    return f"{component.formula}-{component.state}"


def component_ids(components: list[Component]) -> list[str]:
    return [component_id(component) for component in components]


def missing_component_keys(keys: set[str], components: list[Component]) -> list[str]:
    return [component_key for component_key in component_ids(components) if component_key not in keys]


def normalize_flow_pattern(flow_pattern: FlowPattern) -> Literal["co-current", "counter-current"]:
    normalized = flow_pattern.strip().lower().replace("_", "-")
    if normalized in {"cocurrent", "co-current"}:
        return "co-current"
    if normalized in {"countercurrent", "counter-current"}:
        return "counter-current"
    raise ValueError("flow_pattern must be 'co-current' or 'counter-current'.")


def feed_mole_fractions(request: GasHFMSimulationRequest) -> dict[str, CustomProp]:
    if request.feed_mole_fractions is not None:
        return request.feed_mole_fractions
    return {
        component_id(component): custom_prop(component.mole_fraction, "")
        for component in request.components
    }


def json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, BaseModel):
        return json_safe(value.model_dump())
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    return value
