#!/usr/bin/env node

/**
 * MiroFish MCP Server — stdio bridge to MiroFish REST API.
 *
 * Exposes MiroFish swarm-intelligence simulation endpoints as MCP tools
 * so they can be proxied through supergateway into the Brain-and-Co gateway.
 *
 * Environment:
 *   MIROFISH_BACKEND_URL  — MiroFish Flask API (default http://localhost:5001)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const BACKEND = process.env.MIROFISH_BACKEND_URL || "http://localhost:5001";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function api(method, path, body) {
  const url = `${BACKEND}${path}`;
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
    signal: AbortSignal.timeout(30_000),
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const text = await res.text();

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    return {
      error: true,
      status: res.status,
      detail: data,
    };
  }
  return data;
}

function result(obj) {
  return {
    content: [{ type: "text", text: JSON.stringify(obj, null, 2) }],
  };
}

function errorResult(msg) {
  return {
    content: [{ type: "text", text: JSON.stringify({ error: msg }, null, 2) }],
    isError: true,
  };
}

// ---------------------------------------------------------------------------
// Tool definitions
// ---------------------------------------------------------------------------

const TOOLS = [
  {
    name: "create_simulation",
    description:
      "Create a new MiroFish predictive simulation. Submits seed text and a prediction question. Returns the simulation ID for status polling.",
    inputSchema: {
      type: "object",
      properties: {
        seed_text: {
          type: "string",
          description:
            "Seed material for the simulation — article text, project description, or any context the swarm should digest.",
        },
        prediction_requirement: {
          type: "string",
          description:
            "The specific question or prediction to evaluate (e.g. 'What happens if we raise prices 20%?').",
        },
      },
      required: ["seed_text", "prediction_requirement"],
    },
  },
  {
    name: "get_simulation_status",
    description:
      "Check the current status and progress of a MiroFish simulation. Returns status (queued/running/completed/failed), progress percentage, and active agent count.",
    inputSchema: {
      type: "object",
      properties: {
        simulation_id: {
          type: "string",
          description: "The simulation ID returned by create_simulation.",
        },
      },
      required: ["simulation_id"],
    },
  },
  {
    name: "get_report",
    description:
      "Fetch the completed prediction report for a simulation. Includes consensus prediction, confidence score, key factors, dissenting views, and agent cluster analysis.",
    inputSchema: {
      type: "object",
      properties: {
        simulation_id: {
          type: "string",
          description: "The simulation ID to fetch the report for.",
        },
      },
      required: ["simulation_id"],
    },
  },
  {
    name: "interview_agent",
    description:
      "Interview a specific simulated agent from a completed simulation. Ask follow-up questions to understand their reasoning and perspective.",
    inputSchema: {
      type: "object",
      properties: {
        simulation_id: {
          type: "string",
          description: "The simulation the agent belongs to.",
        },
        agent_name: {
          type: "string",
          description:
            "Name or identifier of the agent to interview (from the report's agent_clusters or agent list).",
        },
        question: {
          type: "string",
          description: "The question to ask the simulated agent.",
        },
      },
      required: ["simulation_id", "agent_name", "question"],
    },
  },
];

// ---------------------------------------------------------------------------
// Tool dispatch
// ---------------------------------------------------------------------------

async function handleTool(name, args) {
  switch (name) {
    case "create_simulation": {
      const { seed_text, prediction_requirement } = args;
      if (!seed_text || !prediction_requirement) {
        return errorResult("Both seed_text and prediction_requirement are required.");
      }
      const data = await api("POST", "/api/simulations", {
        seed_text,
        prediction_requirement,
      });
      return result(data);
    }

    case "get_simulation_status": {
      const { simulation_id } = args;
      if (!simulation_id) return errorResult("simulation_id is required.");
      const data = await api("GET", `/api/simulations/${encodeURIComponent(simulation_id)}`);
      return result(data);
    }

    case "get_report": {
      const { simulation_id } = args;
      if (!simulation_id) return errorResult("simulation_id is required.");
      const data = await api("GET", `/api/simulations/${encodeURIComponent(simulation_id)}/report`);
      return result(data);
    }

    case "interview_agent": {
      const { simulation_id, agent_name, question } = args;
      if (!simulation_id || !agent_name || !question) {
        return errorResult("simulation_id, agent_name, and question are all required.");
      }
      const data = await api(
        "POST",
        `/api/simulations/${encodeURIComponent(simulation_id)}/interview`,
        { agent_name, question }
      );
      return result(data);
    }

    default:
      return errorResult(`Unknown tool: ${name}`);
  }
}

// ---------------------------------------------------------------------------
// Server bootstrap
// ---------------------------------------------------------------------------

const server = new Server(
  { name: "mirofish-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    return await handleTool(name, args || {});
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return errorResult(`MiroFish API error: ${msg}`);
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
