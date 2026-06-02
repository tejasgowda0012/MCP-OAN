import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerSchemesInfoTool } from "./schemes-info.js";

/**
 * Central registry: add new tool registration functions here as the project grows.
 * Each tool module exports a registerXxxTool(server: McpServer) function.
 */
export function registerAllTools(server: McpServer): void {
  registerSchemesInfoTool(server);
  // registerCropAdvisoryTool(server);   ← future tools added here
}
