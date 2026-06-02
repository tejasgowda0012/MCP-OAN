import dotenv from "dotenv";

dotenv.config();

export const PORT = parseInt(process.env.PORT ?? "3000", 10);

export const MCP_API_KEY = process.env.MCP_API_KEY;

// Warn only when running as HTTP server (stdio uses stderr which is safe)
export function warnIfNoApiKey(): void {
  if (!MCP_API_KEY) {
    process.stderr.write("[WARN] MCP_API_KEY is not set. All requests will be rejected.\n");
  }
}

// Static Beckn/Vistaar context fields — auto-filled on every request
export const BECKN_CONFIG = {
  domain: "schemes:vistaar",
  action: "search",
  version: "1.1.0",
  bap_id: "seeker-network-vistaar.da.gov.in",
  bap_uri: "https://seeker-network-vistaar.da.gov.in",
  bpp_id: "provider-network-vistaar.da.gov.in",
  bpp_uri: "https://provider-network-vistaar.da.gov.in",
  ttl: "PT10M",
  location: {
    country: { code: "IND" },
    city: { code: "*" },
  },
} as const;

export const BECKN_SEARCH_URL =
  "https://seeker-client-vistaar.da.gov.in/search";
