import "dotenv/config";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerAllTools } from "./tools/registry.js";

// IMPORTANT: In stdio mode, stdout is the MCP protocol channel.
// Never use console.log/console.warn here — use process.stderr only.

async function main(): Promise<void> {
  const server = new McpServer({
    name: "Bharat Vistaar MCP",
    version: "1.0.0",
  });

  registerAllTools(server);

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  process.stderr.write(`Fatal: ${err}\n`);
  process.exit(1);
});
