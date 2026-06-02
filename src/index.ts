import "dotenv/config";
import express, { Request, Response, NextFunction } from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { PORT, MCP_API_KEY, warnIfNoApiKey } from "./config.js";
warnIfNoApiKey();
import { registerAllTools } from "./tools/registry.js";

const app = express();
app.use(express.json());

// ---------------------------------------------------------------------------
// API Key Auth Middleware
// ---------------------------------------------------------------------------
function apiKeyAuth(req: Request, res: Response, next: NextFunction): void {
  if (!MCP_API_KEY) {
    res
      .status(500)
      .json({ error: "Server misconfiguration: MCP_API_KEY not set" });
    return;
  }

  const authHeader = req.headers["authorization"];
  const xApiKey = req.headers["x-api-key"];

  let providedKey: string | undefined;

  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    providedKey = authHeader.slice(7).trim();
  } else if (typeof xApiKey === "string") {
    providedKey = xApiKey.trim();
  }

  if (!providedKey || providedKey !== MCP_API_KEY) {
    res.status(401).json({ error: "Unauthorized: invalid or missing API key" });
    return;
  }

  next();
}

// ---------------------------------------------------------------------------
// MCP endpoint (stateless — new transport + server per request)
// ---------------------------------------------------------------------------
function createMcpServer(): McpServer {
  const server = new McpServer({
    name: "Bharat Vistaar MCP",
    version: "1.0.0",
  });
  registerAllTools(server);
  return server;
}

app.all("/mcp", apiKeyAuth, async (req: Request, res: Response) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined, // stateless mode
  });

  const mcpServer = createMcpServer();

  try {
    await mcpServer.connect(transport);
    await transport.handleRequest(req, res, req.body);

    res.on("finish", () => {
      transport.close().catch(() => {});
      mcpServer.close().catch(() => {});
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[MCP] Request handling error:", message);
    if (!res.headersSent) {
      res.status(500).json({ error: "Internal server error" });
    }
  }
});

// ---------------------------------------------------------------------------
// SSE endpoint — for pydantic-ai MCPServerHTTP (SSE transport)
// ---------------------------------------------------------------------------
const sseTransports: Record<string, SSEServerTransport> = {};

app.get("/sse", apiKeyAuth, async (req: Request, res: Response) => {
  const transport = new SSEServerTransport("/sse/message", res);
  const mcpServer = createMcpServer();
  sseTransports[transport.sessionId] = transport;
  res.on("close", () => {
    delete sseTransports[transport.sessionId];
    mcpServer.close().catch(() => {});
  });
  await mcpServer.connect(transport);
});

app.post("/sse/message", apiKeyAuth, async (req: Request, res: Response) => {
  const sessionId = req.query.sessionId as string;
  const transport = sseTransports[sessionId];
  if (!transport) {
    res.status(404).json({ error: "Session not found" });
    return;
  }
  await transport.handlePostMessage(req, res, req.body);
});

// ---------------------------------------------------------------------------
// Health check — no auth, for uptime monitors / load balancers
// ---------------------------------------------------------------------------
app.get("/health", (_req: Request, res: Response) => {
  res.json({ status: "ok", server: "Bharat Vistaar MCP", version: "1.0.0" });
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`[Bharat Vistaar MCP] Running on http://localhost:${PORT}`);
  console.log(`[Bharat Vistaar MCP] MCP endpoint (streamable HTTP): http://localhost:${PORT}/mcp`);
  console.log(`[Bharat Vistaar MCP] SSE endpoint: http://localhost:${PORT}/sse`);
  console.log(`[Bharat Vistaar MCP] Health check: http://localhost:${PORT}/health`);
});
