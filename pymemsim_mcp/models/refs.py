from pydantic import BaseModel, Field


class MCPHTTPConfig(BaseModel):
    host: str = Field(default="127.0.0.1", description="HTTP bind host.")
    port: int = Field(default=8000, ge=1, le=65535, description="HTTP bind port.")
    path: str = Field(default="/mcp", description="MCP HTTP endpoint path.")
