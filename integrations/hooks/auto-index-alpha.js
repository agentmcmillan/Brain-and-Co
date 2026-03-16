#!/usr/bin/env node
/**
 * Brain-Wave Auto-Index Alpha Hook
 *
 * PostToolUse hook that updates Alpha-Wave INDEX when new files are created.
 *
 * Matcher: Write
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BRAIN_WAVE_ROOT = process.env.BRAIN_WAVE_ROOT || process.cwd();
const AUTO_INDEX = process.env.BRAIN_WAVE_AUTO_INDEX !== 'false';
const VERBOSE = process.env.BRAIN_WAVE_VERBOSE === 'true';

// Paths
const ALPHA_DIR = path.join(BRAIN_WAVE_ROOT, 'alpha-wave');
const INDEX_PATH = path.join(ALPHA_DIR, 'INDEX.md');
const TOPICS_PATH = path.join(ALPHA_DIR, 'TOPICS.md');

// Topic keywords for classification
const TOPIC_KEYWORDS = {
  'architecture': ['architecture', 'system', 'design', 'structure'],
  'api': ['api', 'endpoint', 'rest', 'graphql'],
  'testing': ['test', 'spec', 'jest', 'cypress'],
  'documentation': ['readme', 'docs', 'guide', 'tutorial'],
  'configuration': ['config', 'settings', 'env', 'setup'],
  'components': ['component', 'widget', 'ui', 'view'],
  'database': ['database', 'db', 'schema', 'migration'],
  'security': ['auth', 'security', 'permission', 'token'],
  'investor': ['investor', 'pitch', 'deck', 'fundraising'],
  'product': ['prd', 'product', 'feature', 'requirement'],
};

function log(msg) {
  if (VERBOSE) console.error(`[brain-wave-index] ${msg}`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function getRelativePath(filePath) {
  return path.relative(BRAIN_WAVE_ROOT, filePath);
}

function detectTopics(filePath) {
  const lowerPath = filePath.toLowerCase();
  const detected = [];

  for (const [topic, keywords] of Object.entries(TOPIC_KEYWORDS)) {
    if (keywords.some(kw => lowerPath.includes(kw))) {
      detected.push(topic);
    }
  }

  return detected;
}

function addToIndex(relativePath) {
  ensureDir(ALPHA_DIR);

  if (!fs.existsSync(INDEX_PATH)) {
    log('INDEX.md not found, skipping');
    return false;
  }

  let content = fs.readFileSync(INDEX_PATH, 'utf8');

  // Check if already indexed
  if (content.includes(relativePath)) {
    log('File already in index');
    return false;
  }

  // Find the appropriate section based on file extension
  const ext = path.extname(relativePath).slice(1) || 'other';
  const dir = path.dirname(relativePath);

  // Add to recent files section at top
  const recentMarker = '## Recent Files';
  if (content.includes(recentMarker)) {
    const insertPos = content.indexOf(recentMarker) + recentMarker.length;
    const nextNewline = content.indexOf('\n', insertPos);
    const before = content.substring(0, nextNewline + 1);
    const after = content.substring(nextNewline + 1);
    content = before + `- \`${relativePath}\` (auto-indexed)\n` + after;
  } else {
    // Add recent section at top after header
    const firstSection = content.indexOf('\n## ');
    if (firstSection > -1) {
      const before = content.substring(0, firstSection);
      const after = content.substring(firstSection);
      content = before + `\n## Recent Files\n\n- \`${relativePath}\` (auto-indexed)\n` + after;
    }
  }

  fs.writeFileSync(INDEX_PATH, content);
  log(`Added to INDEX: ${relativePath}`);
  return true;
}

function addToTopics(relativePath, topics) {
  if (topics.length === 0) return;
  if (!fs.existsSync(TOPICS_PATH)) {
    log('TOPICS.md not found, skipping');
    return;
  }

  let content = fs.readFileSync(TOPICS_PATH, 'utf8');

  for (const topic of topics) {
    // Find topic section
    const topicHeader = `### ${topic.charAt(0).toUpperCase() + topic.slice(1)}`;
    if (content.includes(topicHeader)) {
      // Check if already listed
      if (!content.includes(relativePath)) {
        const headerPos = content.indexOf(topicHeader);
        const nextNewline = content.indexOf('\n', headerPos);
        const before = content.substring(0, nextNewline + 1);
        const after = content.substring(nextNewline + 1);
        content = before + `- \`${relativePath}\`\n` + after;
        log(`Added to topic '${topic}': ${relativePath}`);
      }
    }
  }

  fs.writeFileSync(TOPICS_PATH, content);
}

async function main() {
  if (!AUTO_INDEX) {
    log('Auto-index disabled');
    process.exit(0);
  }

  // Read hook payload from stdin
  let payload = '';
  for await (const chunk of process.stdin) {
    payload += chunk;
  }

  try {
    const data = JSON.parse(payload);
    const { tool_name, tool_input } = data;

    // Only process Write operations
    if (tool_name !== 'Write') {
      log('Not a Write operation, skipping');
      process.exit(0);
    }

    const filePath = tool_input?.file_path || tool_input?.path;
    if (!filePath) {
      log('No file path, skipping');
      process.exit(0);
    }

    const relativePath = getRelativePath(filePath);

    // Skip Brain-Wave internal files
    if (relativePath.startsWith('rem/') ||
        relativePath.startsWith('alpha-wave/') ||
        relativePath.startsWith('beta-wave/')) {
      log('Skipping Brain-Wave internal file');
      process.exit(0);
    }

    // Skip hidden files and node_modules
    if (relativePath.includes('node_modules') ||
        relativePath.startsWith('.') ||
        relativePath.includes('/.')) {
      log('Skipping hidden/vendor file');
      process.exit(0);
    }

    // Add to index
    const added = addToIndex(relativePath);

    // Detect and add to topics
    if (added) {
      const topics = detectTopics(relativePath);
      if (topics.length > 0) {
        addToTopics(relativePath, topics);
        log(`Detected topics: ${topics.join(', ')}`);
      }
    }

    log('Alpha index complete');

  } catch (err) {
    log(`Error: ${err.message}`);
    process.exit(0);
  }
}

main();
