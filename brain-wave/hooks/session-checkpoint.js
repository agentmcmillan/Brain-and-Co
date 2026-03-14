#!/usr/bin/env node
/**
 * Brain-Wave Session Checkpoint Hook
 *
 * Notification hook that saves session state when Claude goes idle.
 * Creates restoration checkpoints for context recovery.
 *
 * Matcher: idle_prompt
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BRAIN_WAVE_ROOT = process.env.BRAIN_WAVE_ROOT || process.cwd();
const VERBOSE = process.env.BRAIN_WAVE_VERBOSE === 'true';

// Paths
const REM_DIR = path.join(BRAIN_WAVE_ROOT, 'rem');
const SESSIONS_DIR = path.join(REM_DIR, 'sessions');
const LASTRUN_PATH = path.join(REM_DIR, 'LAST-RUN.md');

// Session tracking
let sessionStartTime = null;

function log(msg) {
  if (VERBOSE) console.error(`[brain-wave-checkpoint] ${msg}`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function formatDate(date = new Date()) {
  return date.toISOString().split('T')[0];
}

function formatTime(date = new Date()) {
  return date.toISOString().replace('T', ' ').split('.')[0];
}

function getSessionFilename() {
  const date = formatDate();
  const hour = new Date().getHours().toString().padStart(2, '0');
  return `${date}-${hour}00-checkpoint.md`;
}

function getRecentChanges() {
  const changelogPath = path.join(REM_DIR, 'CHANGELOG.md');
  if (!fs.existsSync(changelogPath)) return [];

  const content = fs.readFileSync(changelogPath, 'utf8');
  const lines = content.split('\n');
  const today = formatDate();

  // Get today's changes
  const recentChanges = [];
  for (const line of lines) {
    if (line.startsWith('- [') && line.includes(today)) {
      recentChanges.push(line);
    }
    if (recentChanges.length >= 10) break;
  }

  return recentChanges;
}

function getLastRunInfo() {
  if (!fs.existsSync(LASTRUN_PATH)) {
    return { lastTool: 'unknown', lastFile: 'unknown' };
  }

  const content = fs.readFileSync(LASTRUN_PATH, 'utf8');
  const toolMatch = content.match(/\*\*Last Tool\*\*: (.+)/);
  const fileMatch = content.match(/\*\*Last File\*\*: (.+)/);

  return {
    lastTool: toolMatch ? toolMatch[1] : 'unknown',
    lastFile: fileMatch ? fileMatch[1] : 'unknown'
  };
}

function createCheckpoint(reason) {
  ensureDir(SESSIONS_DIR);

  const timestamp = formatTime();
  const filename = getSessionFilename();
  const filepath = path.join(SESSIONS_DIR, filename);

  const recentChanges = getRecentChanges();
  const lastRun = getLastRunInfo();

  const content = `# Session Checkpoint

**Created**: ${timestamp}
**Reason**: ${reason}
**Status**: Idle

## Last Activity

- **Tool**: ${lastRun.lastTool}
- **File**: ${lastRun.lastFile}

## Recent Changes (Today)

${recentChanges.length > 0 ? recentChanges.join('\n') : '- No changes recorded today'}

## Context Restoration

To resume this session:

1. Read this file for context
2. Check \`rem/CHANGELOG.md\` for full history
3. Use \`rem/restoration/PROTOCOL.md\` for detailed steps

## Notes

This checkpoint was auto-created by the Brain-Wave session-checkpoint hook.
The session can be resumed by loading context from these files.

---

*Auto-generated checkpoint*
`;

  // Append or create
  if (fs.existsSync(filepath)) {
    // Append to existing checkpoint
    const existing = fs.readFileSync(filepath, 'utf8');
    const appendContent = `\n---\n\n## Update: ${timestamp}\n\n- Reason: ${reason}\n- Last Tool: ${lastRun.lastTool}\n- Last File: ${lastRun.lastFile}\n`;
    fs.writeFileSync(filepath, existing + appendContent);
    log(`Updated checkpoint: ${filename}`);
  } else {
    fs.writeFileSync(filepath, content);
    log(`Created checkpoint: ${filename}`);
  }

  return filepath;
}

async function main() {
  // Read hook payload from stdin
  let payload = '';
  for await (const chunk of process.stdin) {
    payload += chunk;
  }

  try {
    const data = JSON.parse(payload);
    const { notification_type, message } = data;

    // Only process idle prompts
    if (notification_type !== 'idle_prompt') {
      log('Not an idle prompt, skipping');
      process.exit(0);
    }

    // Create checkpoint
    const checkpointPath = createCheckpoint('Session idle timeout');

    log(`Checkpoint saved: ${checkpointPath}`);

    // Output success message (shown to user)
    console.log(JSON.stringify({
      status: 'ok',
      message: 'Brain-Wave session checkpoint saved'
    }));

  } catch (err) {
    log(`Error: ${err.message}`);
    process.exit(0);
  }
}

main();
