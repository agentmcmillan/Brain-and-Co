#!/usr/bin/env node
/**
 * Brain-Wave Context Hint Hook
 *
 * PreToolUse hook that suggests related files before reading.
 * Uses Beta-Wave connections to provide context hints.
 *
 * Matcher: Read
 *
 * Note: This is a "suggest" hook - it outputs hints but doesn't block.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BRAIN_WAVE_ROOT = process.env.BRAIN_WAVE_ROOT || process.cwd();
const VERBOSE = process.env.BRAIN_WAVE_VERBOSE === 'true';
const ENABLE_HINTS = process.env.BRAIN_WAVE_CONTEXT_HINTS !== 'false';
const MAX_HINTS = parseInt(process.env.BRAIN_WAVE_MAX_HINTS) || 3;

// Paths
const BETA_WAVE_DIR = path.join(BRAIN_WAVE_ROOT, 'beta-wave');
const CONNECTIONS_PATH = path.join(BETA_WAVE_DIR, '_CONNECTIONS.md');

// Cache for connections
let connectionsCache = null;

function log(msg) {
  if (VERBOSE) console.error(`[brain-wave-hint] ${msg}`);
}

function getRelativePath(filePath) {
  return path.relative(BRAIN_WAVE_ROOT, filePath);
}

function loadConnections() {
  if (connectionsCache) return connectionsCache;

  if (!fs.existsSync(CONNECTIONS_PATH)) {
    log('No connections file found');
    return null;
  }

  try {
    const content = fs.readFileSync(CONNECTIONS_PATH, 'utf8');
    connectionsCache = content;
    return content;
  } catch (err) {
    log(`Error loading connections: ${err.message}`);
    return null;
  }
}

function findRelatedFiles(targetFile, connectionsContent) {
  if (!connectionsContent) return [];

  const related = new Set();
  const targetName = path.basename(targetFile);
  const targetDir = path.dirname(targetFile);

  // Parse connections looking for mentions of the target file
  const lines = connectionsContent.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check if this line mentions our target file
    if (line.includes(targetFile) || line.includes(targetName)) {
      // Look for other file references nearby (within 5 lines)
      for (let j = Math.max(0, i - 5); j < Math.min(lines.length, i + 6); j++) {
        const nearbyLine = lines[j];
        // Extract file paths (backtick-wrapped or markdown links)
        const fileMatches = nearbyLine.match(/`([^`]+\.(md|js|ts|tsx|json|yaml|yml))`/g);
        if (fileMatches) {
          fileMatches.forEach(match => {
            const file = match.replace(/`/g, '');
            if (file !== targetFile && file !== targetName) {
              related.add(file);
            }
          });
        }
      }
    }
  }

  // Also look for files in same directory that might be related
  const sameDirFiles = [];
  try {
    const dirPath = path.join(BRAIN_WAVE_ROOT, targetDir);
    if (fs.existsSync(dirPath)) {
      const files = fs.readdirSync(dirPath);
      files.forEach(file => {
        if (file !== targetName && !file.startsWith('.')) {
          sameDirFiles.push(path.join(targetDir, file));
        }
      });
    }
  } catch (err) {
    log(`Error reading directory: ${err.message}`);
  }

  // Combine and limit
  const allRelated = [...related, ...sameDirFiles.slice(0, 2)];
  return [...new Set(allRelated)].slice(0, MAX_HINTS);
}

function getFileContext(filePath) {
  // Check for Beta-Wave map in the file's directory
  const dir = path.dirname(filePath);
  const mapPath = path.join(BETA_WAVE_DIR, dir, '_MAP.md');

  if (fs.existsSync(mapPath)) {
    return `Directory map available: beta-wave/${dir}/_MAP.md`;
  }

  return null;
}

async function main() {
  if (!ENABLE_HINTS) {
    log('Context hints disabled');
    // Output empty response to continue
    console.log(JSON.stringify({ decision: 'continue' }));
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

    // Only process Read operations
    if (tool_name !== 'Read') {
      console.log(JSON.stringify({ decision: 'continue' }));
      process.exit(0);
    }

    const filePath = tool_input?.file_path || tool_input?.path;
    if (!filePath) {
      console.log(JSON.stringify({ decision: 'continue' }));
      process.exit(0);
    }

    const relativePath = getRelativePath(filePath);

    // Skip Brain-Wave internal files
    if (relativePath.startsWith('rem/') ||
        relativePath.startsWith('alpha-wave/') ||
        relativePath.startsWith('beta-wave/')) {
      console.log(JSON.stringify({ decision: 'continue' }));
      process.exit(0);
    }

    // Load connections and find related files
    const connections = loadConnections();
    const relatedFiles = findRelatedFiles(relativePath, connections);
    const dirContext = getFileContext(relativePath);

    // Build hints
    const hints = [];

    if (relatedFiles.length > 0) {
      hints.push(`Related files: ${relatedFiles.join(', ')}`);
    }

    if (dirContext) {
      hints.push(dirContext);
    }

    // Output hints (these appear as stderr, visible in verbose mode)
    if (hints.length > 0) {
      log(`Context hints for ${relativePath}:`);
      hints.forEach(h => log(`  - ${h}`));
    }

    // Always continue - this is a non-blocking hint hook
    console.log(JSON.stringify({
      decision: 'continue',
      hints: hints
    }));

  } catch (err) {
    log(`Error: ${err.message}`);
    console.log(JSON.stringify({ decision: 'continue' }));
    process.exit(0);
  }
}

main();
