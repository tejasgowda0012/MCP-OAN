# Connecting to the Vistaar MCP Server

This document explains how to configure your AI agent or MCP client to connect to our server using your provided API Key.

## Authentication

Our server uses Bearer Token authentication to verify your identity and enforce Role-Based Access Control (RBAC). You must include your API Key in the HTTP headers of your connection request.

**Header Format:**
```
Authorization: Bearer <YOUR_API_KEY>
```
*(Alternatively, you can use the `x-api-key: <YOUR_API_KEY>` header)*

## Connection Endpoints

The Vistaar MCP Server operates using the **Server-Sent Events (SSE)** transport layer (often referred to as Streamable HTTP). 

- **Production URL**: `https://api.yourdomain.com/mcp` *(Ask your admin for the exact URL)*
- **Local Testing URL**: `http://localhost:3001/mcp`

---

## Integration Examples

### 1. Python (using `mcp` SDK)

To connect using the official Python MCP SDK, you need to use the `sse_client` and pass your API key via the `headers` dictionary.

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

API_KEY = "vistaar_your_api_key_here"
MCP_SERVER_URL = "http://localhost:3001/mcp/sse"

async def run_agent():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Establish the SSE connection with authentication headers
    async with sse_client(MCP_SERVER_URL, headers=headers) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            # Initialize the session
            await session.initialize()
            print("Connected successfully!")
            
            # List available tools (You will only see tools permitted for your role)
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
                
            # Example: Execute a permitted tool
            result = await session.call_tool("weather_forecast", {"location": "Pune"})
            print(result)

if __name__ == "__main__":
    asyncio.run(run_agent())
```

### 2. Node.js (using `@modelcontextprotocol/sdk`)

To connect using the official TypeScript/Node.js SDK, you'll instantiate the `SSEClientTransport` and pass your headers in the `EventSource` and fetch configurations.

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const API_KEY = "vistaar_your_api_key_here";
const MCP_SERVER_URL = new URL("http://localhost:3001/mcp/sse");

async function runAgent() {
    // 1. Initialize the transport with custom headers
    const transport = new SSEClientTransport(MCP_SERVER_URL, {
        eventSourceInit: {
            headers: {
                "Authorization": `Bearer ${API_KEY}`
            }
        },
        requestInit: {
            headers: {
                "Authorization": `Bearer ${API_KEY}`
            }
        }
    });

    // 2. Initialize the client
    const client = new Client({
        name: "my-external-agent",
        version: "1.0.0"
    }, {
        capabilities: {}
    });

    // 3. Connect and execute
    await client.connect(transport);
    console.log("Connected successfully!");

    // List available tools (Filtered by your role)
    const tools = await client.listTools();
    console.dir(tools, { depth: null });

    // Call a tool
    const result = await client.callTool({
        name: "weather_forecast",
        arguments: { location: "Pune" }
    });
    console.log(result);
}

runAgent().catch(console.error);
```

### 3. Using LangChain (Python)

If your external agent is built on LangChain or LangGraph, you can easily integrate the MCP tools using `langchain-mcp`.

```python
import asyncio
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_mcp.client import MCPClient

API_KEY = "vistaar_your_api_key_here"

async def main():
    # Configure the client with headers
    client = MCPClient(
        server_url="http://localhost:3001/mcp/sse",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    # Get your permitted tools as LangChain tools
    mcp_tools = await client.get_tools()
    
    # Bind them to an LLM
    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools(mcp_tools)
    
    # Send a prompt to the LLM
    msg = llm_with_tools.invoke([HumanMessage(content="What is the weather in Pune?")])
    print(msg.tool_calls)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Troubleshooting

### `401 Unauthorized`
- **Cause**: Your API key is missing, invalid, or has been deactivated by an administrator.
- **Fix**: Double-check that your headers match `Authorization: Bearer <key>` precisely. Contact your admin if you believe your key was rotated.

### `Access Denied` Error during Tool Execution
- **Cause**: You successfully connected to the server, but your assigned **Role** does not have permission to execute the specific tool you called. 
- **Fix**: Contact your admin to request the missing permissions be added to your role.

### Connection Refused
- **Cause**: The server is down, or you are trying to reach an internal IP from an external network.
- **Fix**: Ensure you are using the correct production URL provided by your administrator.
