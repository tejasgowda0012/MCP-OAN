import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { randomBytes } from "crypto";

function uuidv4(): string {
  const b = randomBytes(16);
  b[6] = (b[6] & 0x0f) | 0x40;
  b[8] = (b[8] & 0x3f) | 0x80;
  const h = b.toString("hex");
  return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`;
}
import { BECKN_CONFIG, BECKN_SEARCH_URL } from "../config.js";

// ---------------------------------------------------------------------------
// Beckn response → human-readable text  (mirrors mh-oan-api parsing logic)
// ---------------------------------------------------------------------------
interface BecknDescriptor {
  code?: string;
  name?: string;
  short_desc?: string;
  long_desc?: string;
}

interface BecknTagItem {
  descriptor?: BecknDescriptor;
  value?: string;
}

interface BecknTag {
  descriptor?: BecknDescriptor;
  list?: BecknTagItem[];
}

interface BecknItem {
  id?: string;
  descriptor?: BecknDescriptor;
  tags?: BecknTag[];
}

interface BecknProvider {
  id?: string;
  descriptor?: BecknDescriptor;
  items?: BecknItem[];
}

interface BecknCatalog {
  descriptor?: BecknDescriptor;
  providers?: BecknProvider[];
}

interface BecknResponseItem {
  context?: Record<string, unknown>;
  message?: { catalog?: BecknCatalog };
}

function formatItem(item: BecknItem): string {
  const lines: string[] = [];
  if (item.tags) {
    for (const tag of item.tags) {
      if (!tag.list) continue;
      for (const tagItem of tag.list) {
        const val = tagItem.value?.trim();
        const label = tagItem.descriptor?.name || tagItem.descriptor?.code;
        if (val && val.toLowerCase() !== "null" && label) {
          lines.push(`*${label}*:\n${val}`);
        }
      }
    }
  }
  return lines.join("\n\n");
}

function formatProvider(provider: BecknProvider): string {
  if (!provider.items?.length) return "";
  return provider.items.map(formatItem).filter(Boolean).join("\n\n---\n\n");
}

function formatBecknResponse(data: unknown): string {
  // The response can be either { responses: [...] } or a single response object
  let responseItems: BecknResponseItem[] = [];

  const obj = data as Record<string, unknown>;
  if (Array.isArray(obj.responses)) {
    responseItems = obj.responses as BecknResponseItem[];
  } else if (obj.message) {
    responseItems = [obj as BecknResponseItem];
  } else {
    return "No scheme data found.";
  }

  // Check if any provider has items
  let hasData = false;
  for (const resp of responseItems) {
    const providers = resp.message?.catalog?.providers;
    if (providers?.some((p) => p.items && p.items.length > 0)) {
      hasData = true;
      break;
    }
  }

  if (!hasData) return "No scheme data found.";

  const parts: string[] = [];
  for (const resp of responseItems) {
    const providers = resp.message?.catalog?.providers;
    if (!providers) continue;
    for (const provider of providers) {
      const text = formatProvider(provider);
      if (text) parts.push(text);
    }
  }

  return parts.join("\n\n") || "No scheme data found.";
}

// Flat schema — "name" maps to descriptor.name in the Beckn request.
// Nested z.object() inside ZodRawShape causes TS 5.8 type depth errors.
const SchemesInfoInputSchema = {
  name: z.string(),
};

export function registerSchemesInfoTool(server: McpServer): void {
  server.tool(
    "schemes-info",
    "Search for Indian agricultural scheme information via the Vistaar/Beckn network. Pass the scheme name (maps to descriptor.name in the Beckn protocol, e.g. 'pmkisan', 'fasal-bima'). All other protocol details are handled automatically.",
    SchemesInfoInputSchema,
    async ({ name }) => {
      const requestBody = {
        context: {
          ...BECKN_CONFIG,
          transaction_id: uuidv4(),
          message_id: uuidv4(),
          timestamp: new Date().toISOString(),
        },
        message: {
          intent: {
            category: {
              descriptor: { code: "schemes-agri" },
            },
            item: {
              descriptor: { name },
            },
          },
        },
      };

      try {
        const response = await fetch(BECKN_SEARCH_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          const errBody = await response.text();
          return {
            content: [
              {
                type: "text",
                text: `Beckn API error: HTTP ${response.status} — ${errBody}`,
              },
            ],
            isError: true,
          };
        }

        const data = await response.json();
        const formatted = formatBecknResponse(data);
        return {
          content: [
            {
              type: "text",
              text: formatted,
            },
          ],
        };
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        return {
          content: [
            {
              type: "text",
              text: `Network error calling Vistaar API: ${message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}
