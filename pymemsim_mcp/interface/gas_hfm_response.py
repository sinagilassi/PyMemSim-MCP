from typing import Any

from pymemsim import HFM
from pymemsim.utils import analyze_hfm_result

from pymemsim_mcp.interface.gas_hfm_helpers import json_safe


def failure_response(message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "span": [],
        "state": [],
        "analysis": {},
        "warnings": warnings or [],
    }


def analyze_result(
    simulation_results: Any,
    hfm_module: HFM,
    target_component: str,
    warnings: list[str],
) -> dict[str, Any]:
    analysis = analyze_hfm_result(
        result=simulation_results,
        hfm_module=hfm_module,
        target_component=target_component,
    )
    return json_safe(
        {
            "success": simulation_results.success,
            "message": simulation_results.message,
            "span": simulation_results.span,
            "state": simulation_results.state,
            "analysis": analysis,
            "warnings": warnings + analysis.get("warnings", []),
        }
    )
