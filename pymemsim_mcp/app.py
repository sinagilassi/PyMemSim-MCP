# import libs
from typing import Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP

from pythermodb_settings.models import CustomProp, Temperature, Component
from pymemsim import HFM, create_hfm_module
from pymemsim.thermo import build_thermo_source
from pymemsim.models import (
    HeatTransferOptions,
    HollowFiberMembraneOptions,
    HollowFiberMembraneModuleGeometry,
)
from pymemsim.utils import analyze_hfm_result


mcp = FastMCP("PyMemSim-MCP")


if __name__ == "__main__":
    mcp.run()
