#!/usr/bin/env node
/**
 * Pre-Commit Gate Hook
 *
 * PreToolUse hook on Bash that:
 * 1. Intercepts `git push` → checks for BLOCKER items in latest review → blocks if found
 * 2. Intercepts `git commit` → soft warning if no review exists for current branch
 *
 * Matcher: Bash
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

async function main() {
  let payload = '';
  for await (const chunk of process.stdin) {
    payload += chunk;
  }

  try {
    const data = JSON.parse(payload);
    const { tool_input } = data;
    const command = tool_input?.command || '';

    // Only intercept git push and git commit commands
    const isGitPush = /\bgit\s+push\b/.test(command);
    const isGitCommit = /\bgit\s+commit\b/.test(command);

    if (!isGitPush && !isGitCommit) {
      // Not a git command we care about — allow
      process.exit(0);
    }

    // Find the project root (look for .git directory)
    let projectRoot;
    try {
      projectRoot = execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
    } catch {
      // Not in a git repo — allow
      process.exit(0);
    }

    const discoveriesDir = path.join(projectRoot, 'rem', 'discoveries');

    if (isGitPush) {
      // Check for BLOCKER items in the most recent review file
      const reviewFile = findLatestReview(discoveriesDir);
      if (reviewFile) {
        const content = fs.readFileSync(reviewFile, 'utf8');
        const blockerCount = (content.match(/\bBLOCKER\b/g) || []).length;
        const verdict = content.match(/Verdict:\s*\*\*(\w[\w-]*)\*\*/);

        if (verdict && verdict[1] === 'BLOCK') {
          // Output JSON to block the action
          const result = {
            decision: "block",
            reason: `Code review verdict is BLOCK (${blockerCount} blocker(s) found). Fix blockers before pushing. Review: ${path.basename(reviewFile)}`
          };
          process.stdout.write(JSON.stringify(result));
          process.exit(0);
        }
      }
    }

    if (isGitCommit) {
      // Soft warning if no review exists for current branch
      let branch;
      try {
        branch = execSync('git branch --show-current', { encoding: 'utf8' }).trim();
      } catch {
        process.exit(0);
      }

      const reviewFile = findLatestReview(discoveriesDir);
      if (!reviewFile) {
        // Warn but don't block
        const result = {
          decision: "allow",
          reason: `Note: No code review found for branch '${branch}'. Consider running /review before committing.`
        };
        process.stdout.write(JSON.stringify(result));
        process.exit(0);
      }
    }

    // Allow by default
    process.exit(0);

  } catch (err) {
    // On any error, allow the command to proceed
    process.exit(0);
  }
}

/**
 * Find the most recent review-*.md file in the discoveries directory
 */
function findLatestReview(discoveriesDir) {
  if (!fs.existsSync(discoveriesDir)) return null;

  const files = fs.readdirSync(discoveriesDir)
    .filter(f => f.startsWith('review-') && f.endsWith('.md'))
    .sort()
    .reverse();

  return files.length > 0 ? path.join(discoveriesDir, files[0]) : null;
}

main();
