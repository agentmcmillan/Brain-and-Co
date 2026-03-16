#!/usr/bin/env node
/**
 * Brain-Wave Auto-Sync REM Hook
 *
 * PostToolUse hook that updates REM memory after file edits.
 * Maintains CHANGELOG.md and LAST-RUN.md automatically.
 *
 * Matcher: Edit|Write
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BRAIN_WAVE_ROOT = process.env.BRAIN_WAVE_ROOT || process.cwd();
const AUTO_SYNC = process.env.BRAIN_WAVE_AUTO_SYNC !== 'false';
const VERBOSE = process.env.BRAIN_WAVE_VERBOSE === 'true';

// Paths
const REM_DIR = path.join(BRAIN_WAVE_ROOT, 'rem');
const CHANGELOG_PATH = path.join(REM_DIR, 'CHANGELOG.md');
const LASTRUN_PATH = path.join(REM_DIR, 'LAST-RUN.md');

function log(msg) {
  if (VERBOSE) console.error(`[brain-wave-sync] ${msg}`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function formatTimestamp() {
  return new Date().toISOString().replace('T', ' ').split('.')[0];
}

function getRelativePath(filePath) {
  return path.relative(BRAIN_WAVE_ROOT, filePath);
}

function appendToChangelog(entry) {
  ensureDir(REM_DIR);

  const timestamp = formatTimestamp();
  const line = `- [${timestamp}] ${entry}\n`;

  if (fs.existsSync(CHANGELOG_PATH)) {
    // Insert after header
    let content = fs.readFileSync(CHANGELOG_PATH, 'utf8');
    const headerEnd = content.indexOf('\n## ');
    if (headerEnd > -1) {
      // Insert before first section
      const beforeSection = content.substring(0, headerEnd);
      const afterSection = content.substring(headerEnd);
      content = beforeSection + '\n' + line + afterSection;
    } else {
      content += line;
    }
    fs.writeFileSync(CHANGELOG_PATH, content);
  } else {
    // Create new changelog
    const content = `# REM Changelog\n\nAutomatically tracked changes.\n\n${line}`;
    fs.writeFileSync(CHANGELOG_PATH, content);
  }

  log(`Appended to CHANGELOG: ${entry}`);
}

function updateLastRun(toolName, filePath) {
  ensureDir(REM_DIR);

  const timestamp = formatTimestamp();
  const relativePath = getRelativePath(filePath);

  const content = `# Last Run State

**Updated**: ${timestamp}
**Last Tool**: ${toolName}
**Last File**: ${relativePath}

## Session Info

This file is auto-updated by the brain-wave-sync hook.
Check \`rem/sessions/\` for full session history.

## Quick Actions

- View changelog: \`rem/CHANGELOG.md\`
- Restore context: \`rem/restoration/PROTOCOL.md\`
- Recent discoveries: \`rem/discoveries/\`
`;

  fs.writeFileSync(LASTRUN_PATH, content);
  log(`Updated LAST-RUN.md`);
}

async function main() {
  if (!AUTO_SYNC) {
    log('Auto-sync disabled');
    process.exit(0);
  }

  // Read hook payload from stdin
  let payload = '';
  for await (const chunk of process.stdin) {
    payload += chunk;
  }

  try {
    const data = JSON.parse(payload);
    const { tool_name, tool_input, tool_result } = data;

    // Extract file path from tool input
    const filePath = tool_input?.file_path || tool_input?.path || 'unknown';

    // Skip if no valid path
    if (filePath === 'unknown') {
      log('No file path in tool input, skipping');
      process.exit(0);
    }

    // Skip Brain-Wave internal files to prevent loops
    const relativePath = getRelativePath(filePath);
    if (relativePath.startsWith('rem/') ||
        relativePath.startsWith('alpha-wave/') ||
        relativePath.startsWith('beta-wave/')) {
      log('Skipping Brain-Wave internal file');
      process.exit(0);
    }

    // Determine action type
    const action = tool_name === 'Write' ? 'Created/Wrote' : 'Edited';

    // Update REM state
    appendToChangelog(`${action}: \`${relativePath}\``);
    updateLastRun(tool_name, filePath);

    log('REM sync complete');

  } catch (err) {
    log(`Error: ${err.message}`);
    // Don't fail the hook on errors
    process.exit(0);
  }
}

main();
