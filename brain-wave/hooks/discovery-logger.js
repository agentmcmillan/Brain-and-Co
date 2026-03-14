#!/usr/bin/env node
/**
 * Brain-Wave Discovery Logger Hook
 *
 * PostToolUse hook that captures insights from agent tasks.
 * Logs patterns, decisions, and learnings to REM discoveries.
 *
 * Matcher: Task
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BRAIN_WAVE_ROOT = process.env.BRAIN_WAVE_ROOT || process.cwd();
const VERBOSE = process.env.BRAIN_WAVE_VERBOSE === 'true';

// Paths
const REM_DIR = path.join(BRAIN_WAVE_ROOT, 'rem');
const DISCOVERIES_DIR = path.join(REM_DIR, 'discoveries');

// Discovery patterns to detect
const DISCOVERY_PATTERNS = [
  { pattern: /found.*pattern/i, category: 'patterns' },
  { pattern: /discovered/i, category: 'discoveries' },
  { pattern: /architecture|design/i, category: 'architecture' },
  { pattern: /decision|chose|selected/i, category: 'decisions' },
  { pattern: /bug|issue|problem|error/i, category: 'issues' },
  { pattern: /optimization|performance|improve/i, category: 'optimizations' },
  { pattern: /security|vulnerability/i, category: 'security' },
  { pattern: /dependency|connection|relationship/i, category: 'connections' },
];

function log(msg) {
  if (VERBOSE) console.error(`[brain-wave-discovery] ${msg}`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function formatTimestamp() {
  return new Date().toISOString().replace('T', ' ').split('.')[0];
}

function formatDate() {
  return new Date().toISOString().split('T')[0];
}

function detectCategory(text) {
  for (const { pattern, category } of DISCOVERY_PATTERNS) {
    if (pattern.test(text)) {
      return category;
    }
  }
  return 'general';
}

function extractKeyInsights(result) {
  if (!result || typeof result !== 'string') return [];

  const insights = [];

  // Look for bullet points
  const bullets = result.match(/^[-*]\s+.+$/gm);
  if (bullets) {
    insights.push(...bullets.slice(0, 5).map(b => b.replace(/^[-*]\s+/, '')));
  }

  // Look for "Key" or "Important" sections
  const keyMatches = result.match(/(?:key|important|note|insight):\s*(.+)/gi);
  if (keyMatches) {
    insights.push(...keyMatches.slice(0, 3));
  }

  return insights;
}

function appendToDiscoveryFile(category, entry) {
  ensureDir(DISCOVERIES_DIR);

  const filename = `${category}.md`;
  const filepath = path.join(DISCOVERIES_DIR, filename);

  const timestamp = formatTimestamp();
  const formattedEntry = `\n### ${timestamp}\n\n${entry}\n`;

  if (fs.existsSync(filepath)) {
    const content = fs.readFileSync(filepath, 'utf8');
    fs.writeFileSync(filepath, content + formattedEntry);
  } else {
    const header = `# ${category.charAt(0).toUpperCase() + category.slice(1)} Discoveries\n\nAutomatically logged insights and patterns.\n`;
    fs.writeFileSync(filepath, header + formattedEntry);
  }

  log(`Logged to ${filename}`);
}

function createDailyLog(agentType, description, insights) {
  ensureDir(DISCOVERIES_DIR);

  const date = formatDate();
  const filename = `daily-${date}.md`;
  const filepath = path.join(DISCOVERIES_DIR, filename);

  const timestamp = formatTimestamp();
  const entry = `
## ${timestamp} - ${agentType}

**Task**: ${description}

${insights.length > 0 ? '**Insights**:\n' + insights.map(i => `- ${i}`).join('\n') : '*No specific insights extracted*'}

---
`;

  if (fs.existsSync(filepath)) {
    const content = fs.readFileSync(filepath, 'utf8');
    fs.writeFileSync(filepath, content + entry);
  } else {
    const header = `# Daily Discovery Log - ${date}\n\nAgent task insights and learnings.\n`;
    fs.writeFileSync(filepath, header + entry);
  }

  log(`Logged to daily: ${filename}`);
}

async function main() {
  // Read hook payload from stdin
  let payload = '';
  for await (const chunk of process.stdin) {
    payload += chunk;
  }

  try {
    const data = JSON.parse(payload);
    const { tool_name, tool_input, tool_result } = data;

    // Only process Task tool
    if (tool_name !== 'Task') {
      log('Not a Task operation, skipping');
      process.exit(0);
    }

    const agentType = tool_input?.subagent_type || 'unknown';
    const description = tool_input?.description || 'No description';
    const result = tool_result?.content || '';

    // Skip Brain-Wave internal agents to prevent recursion
    if (['alpha-wave', 'beta-wave', 'rem', 'brain-wave-init'].includes(agentType)) {
      log('Skipping Brain-Wave internal agent');
      process.exit(0);
    }

    // Extract insights from result
    const insights = extractKeyInsights(result);

    // Detect category
    const category = detectCategory(description + ' ' + result);

    // Log to category file if significant
    if (insights.length > 0) {
      const entry = `**Agent**: ${agentType}\n**Task**: ${description}\n\n${insights.map(i => `- ${i}`).join('\n')}`;
      appendToDiscoveryFile(category, entry);
    }

    // Always log to daily file
    createDailyLog(agentType, description, insights);

    log('Discovery logging complete');

  } catch (err) {
    log(`Error: ${err.message}`);
    process.exit(0);
  }
}

main();
