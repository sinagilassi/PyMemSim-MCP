# PyMemSim-MCP

[![PyPI Downloads](https://static.pepy.tech/badge/pymemsim-mcp/month)](https://pepy.tech/projects/pymemsim-mcp)
![PyPI](https://img.shields.io/pypi/v/pymemsim-mcp)
![Python Version](https://img.shields.io/pypi/pyversions/pymemsim-mcp.svg)
![License](https://img.shields.io/pypi/l/pymemsim-mcp)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-Compatible-orange)](https://modelcontextprotocol.io)

PyMemSim-MCP exposes PyMemSim membrane simulation capabilities through an MCP server.

## Overview 🌐

PyMemSim-MCP is a next-generation framework that brings the Model Context Protocol into chemical engineering modeling and simulation, specifically for membrane-based separation systems.

Built on top of PyMemSim, this package introduces a model-source-driven architecture in which thermodynamic data, transport properties, and governing equations are defined externally in a structured, machine-readable format (e.g., YAML). These model sources are dynamically constructed using tools such as PyThermoLinkDB and PyThermoDB, and then supplied, alongside conventional inputs like temperature, pressure, and composition, to simulation workflows.

Unlike traditional tightly coupled simulation tools, PyMemSim-MCP decouples data, equations, and numerical solvers, enabling:

- ✅ Consistent and unit-safe thermodynamic definitions across simulations
- 🔗 Flexible integration with multiple modeling packages and workflows
- ⚙️ Solver-agnostic execution of mass and heat balance equations
- 🔍 Transparent and interpretable simulation pipelines

A key innovation of PyMemSim-MCP is its compatibility with agentic workflows, where specialized agents can:

- 🧠 Extract and structure thermodynamic data from unstructured sources into validated model sources
- 🤖 Interact with MCP-enabled endpoints to perform simulations, sensitivity analysis, and optimization

This approach addresses critical gaps in current LLM-integrated engineering tools, where inconsistencies in data formats, units, and equations often lead to unreliable results. By enforcing a unified scientific contract, PyMemSim-MCP allows LLMs to control both conventional inputs and structured model sources before executing physics-based computations, significantly improving robustness and reproducibility.

PyMemSim-MCP is particularly suited for:

- 🧪 Membrane process modeling (e.g., hollow fiber modules, gas separation)
- 🤝 AI-assisted simulation workflows
- 🚀 Rapid prototyping and validation of process models
- 🎓 Educational and research applications in computational chemical engineering

Overall, PyMemSim-MCP represents a step toward trustworthy AI-driven simulation environments, where domain knowledge, data, and numerical methods are seamlessly integrated under a standardized and extensible framework.

## Requirements 📋

- Python `>=3.11`
- `pip` (or `uv`)

## Install the package 📦

```bash
pip install pymemsim-mcp
```

This installs the CLI entrypoint:

- `pymemsim-mcp`

## Start / Activate the MCP Server ▶️

The server entrypoint is:

- module: `python -m pymemsim_mcp.server`
- script: `pymemsim-mcp`

Both support the same options.

### Case A: STDIO transport (recommended for MCP desktop/agent clients) 🧵

```bash
pymemsim-mcp --mode stdio
```

Equivalent:

```bash
python -m pymemsim_mcp.server --mode stdio
```

### Case B: HTTP transport (for network-accessible clients) 🌍

```bash
pymemsim-mcp --mode http --host 127.0.0.1 --port 8000 --path /mcp
```

Equivalent:

```bash
python -m pymemsim_mcp.server --mode http --host 127.0.0.1 --port 8000 --path /mcp
```

## CLI Options ⌨️

- `--mode`: `stdio` or `http` (default: `stdio`)
- `--host`: HTTP bind host (default: `127.0.0.1`)
- `--port`: HTTP bind port (default: `8000`)
- `--path`: HTTP endpoint path (default: `/mcp`)

## MCP Client Configuration Examples 🔌

### STDIO client config (generic)

```json
{
  "mcpServers": {
    "pymemsim": {
      "command": "pymemsim-mcp",
      "args": ["--mode", "stdio"]
    }
  }
}
```

### HTTP client config (generic)

```json
{
  "mcpServers": {
    "pymemsim": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## Available Tool 🧩

- `simulate_gas_hfm`: build thermo model source from reference content and run gas hollow-fiber membrane simulation.

## Development Quick Check ✅

```bash
python -m py_compile pymemsim_mcp/server.py
python -m py_compile pymemsim_mcp/interface/gas_hfm.py
```

## Troubleshooting 🩺

- `pymemsim-mcp: command not found`
  - Run `pip install -e .` in the active environment.
  - Confirm environment is activated.

- Port already in use (HTTP mode)
  - Change port, for example: `--port 8010`.

- Import errors
  - Reinstall dependencies: `pip install -e .`.

## ❓ FAQ

For any questions, contact me on [LinkedIn](https://www.linkedin.com/in/sina-gilassi/).

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- [@sinagilassi](https://www.github.com/sinagilassi)