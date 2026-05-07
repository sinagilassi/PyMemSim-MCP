# import libs

# locals
from pymemsim_mcp.server import create_mcp_server

# NOTE: build mcp
mcp_server = create_mcp_server()

# NOTE: run mcp server (stdio)
if __name__ == "__main__":
    mcp_server.run()
