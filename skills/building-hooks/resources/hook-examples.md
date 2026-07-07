# Complete Hook Examples

This guide provides complete, production-ready hook implementations you can use and adapt.

## Example 1: File Edit Tracker (PostToolUse)

**Purpose:** Track which files were edited and in which repos for later analysis.

**File:** `~/.claude/hooks/post-tool-use/log-edits.sh`

```bash
#!/bin/bash

# Configuration
LOG_FILE="$HOME/.claude/logs/file-edits.log"
MAX_LOG_LINES=1000

# Create log if doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Function to log edit
log_edit() {
    local file_path="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local repo=$(find_repo "$file_path")

    echo "$timestamp | $repo | $file_path" >> "$LOG_FILE"
}

# Function to find repo root
find_repo() {
    local dir=$(dirname "$1")
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ]; then
            basename "$dir"
            return
        fi
        dir=$(dirname "$dir")
    done
    echo "unknown"
}

# Read tool use event from stdin (Claude Code's real PostToolUse schema:
# top-level tool_name/tool_input, not a nested "tool" object)
read -r tool_use_json

tool_name=$(echo "$tool_use_json" | jq -r '.tool_name')
file_path=""

case "$tool_name" in
    "Edit"|"Write")
        file_path=$(echo "$tool_use_json" | jq -r '.tool_input.file_path')
        ;;
    "MultiEdit")
        # MultiEdit has multiple files - log each
        echo "$tool_use_json" | jq -r '.tool_input.edits[].file_path' | while read -r path; do
            log_edit "$path"
        done
        exit 0
        ;;
esac

# Log single edit
if [ -n "$file_path" ] && [ "$file_path" != "null" ]; then
    log_edit "$file_path"
fi

# Rotate log if too large
line_count=$(wc -l < "$LOG_FILE")
if [ "$line_count" -gt "$MAX_LOG_LINES" ]; then
    tail -n "$MAX_LOG_LINES" "$LOG_FILE" > "$LOG_FILE.tmp"
    mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

# Non-blocking, nothing to report: exit 0 with no output.
exit 0
```

**Configuration (`hooks.json`):** wiring uses a matcher plus a `hooks` array, not a
flat list — this is the shape `hooks/hooks.json` actually uses in this plugin:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/post-tool-use/log-edits.sh"
          }
        ]
      }
    ]
  }
}
```

## Example 2: Multi-Repo Build Checker (Stop)

**Purpose:** Run builds on all repos that were modified, report errors.

**File:** `~/.claude/hooks/stop/20-build-checker.sh`

```bash
#!/bin/bash

# Configuration
LOG_FILE="$HOME/.claude/logs/file-edits.log"
PROJECT_ROOT="$HOME/git/myproject"
ERROR_THRESHOLD=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get repos modified since last check
get_modified_repos() {
    # Get unique repos from recent edits
    tail -50 "$LOG_FILE" 2>/dev/null | \
        cut -d'|' -f2 | \
        tr -d ' ' | \
        sort -u | \
        grep -v "unknown"
}

# Run build in repo
build_repo() {
    local repo_name="$1"
    local repo_path="$PROJECT_ROOT/$repo_name"

    if [ ! -d "$repo_path" ]; then
        return 0
    fi

    # Determine build command
    local build_cmd=""
    if [ -f "$repo_path/package.json" ]; then
        build_cmd="npm run build"
    elif [ -f "$repo_path/Cargo.toml" ]; then
        build_cmd="cargo build"
    elif [ -f "$repo_path/go.mod" ]; then
        build_cmd="go build ./..."
    else
        return 0  # No build system found
    fi

    echo "Building $repo_name..."

    # Run build and capture output
    cd "$repo_path"
    local output=$(eval "$build_cmd" 2>&1)
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        # Count errors
        local error_count=$(echo "$output" | grep -c "error" || echo "0")

        if [ "$error_count" -ge "$ERROR_THRESHOLD" ]; then
            echo -e "${YELLOW}⚠️  $repo_name: $error_count errors found${NC}"
            echo "   Consider launching auto-error-resolver agent"
        else
            echo -e "${RED}🔴 $repo_name: $error_count errors${NC}"
            echo "$output" | grep "error" | head -10
        fi

        return 1
    else
        echo -e "${GREEN}✅ $repo_name: Build passed${NC}"
        return 0
    fi
}

# Main execution
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 BUILD VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

modified_repos=$(get_modified_repos)

if [ -z "$modified_repos" ]; then
    echo "No repos modified since last check"
    exit 0
fi

build_failures=0

for repo in $modified_repos; do
    if ! build_repo "$repo"; then
        ((build_failures++))
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$build_failures" -gt 0 ]; then
    echo -e "${RED}$build_failures repo(s) failed to build${NC}"
else
    echo -e "${GREEN}All builds passed${NC}"
fi

# Non-blocking - always return success
echo '{}'
```

## Example 3: TypeScript Prettier Formatter (Stop)

**Purpose:** Auto-format all edited TypeScript/JavaScript files.

**File:** `~/.claude/hooks/stop/30-format-code.sh`

```bash
#!/bin/bash

# Configuration
LOG_FILE="$HOME/.claude/logs/file-edits.log"
PROJECT_ROOT="$HOME/git/myproject"

# Get recently edited files
get_edited_files() {
    tail -50 "$LOG_FILE" 2>/dev/null | \
        cut -d'|' -f3 | \
        tr -d ' ' | \
        grep -E '\.(ts|tsx|js|jsx)$' | \
        sort -u
}

# Format file with prettier
format_file() {
    local file="$1"

    if [ ! -f "$file" ]; then
        return 0
    fi

    # Find prettier config
    local dir=$(dirname "$file")
    local prettier_config=""

    while [ "$dir" != "/" ]; do
        if [ -f "$dir/.prettierrc" ] || [ -f "$dir/.prettierrc.json" ]; then
            prettier_config="$dir"
            break
        fi
        dir=$(dirname "$dir")
    done

    if [ -z "$prettier_config" ]; then
        return 0
    fi

    # Format the file
    cd "$prettier_config"
    npx prettier --write "$file" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✓ Formatted: $(basename $file)"
    fi
}

# Main execution
echo "🎨 Formatting edited files..."

edited_files=$(get_edited_files)

if [ -z "$edited_files" ]; then
    echo "No files to format"
    exit 0
fi

formatted_count=0

for file in $edited_files; do
    if format_file "$file"; then
        ((formatted_count++))
    fi
done

echo "✅ Formatted $formatted_count file(s)"

# Non-blocking
echo '{}'
```

## Example 4: Contextual Reminder Injector (UserPromptSubmit)

**Purpose:** Analyze the user's prompt and inject a contextual reminder before Claude processes it.

**File:** `~/.claude/hooks/user-prompt-submit/keyword-reminder.js`

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Load keyword rules (a small local config, not shared with anything else)
const rulesPath = process.env.KEYWORD_RULES || path.join(process.env.HOME, '.claude/keyword-rules.json');
const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));

// Read the event from stdin. Claude Code's real UserPromptSubmit schema
// carries the text in a top-level "prompt" field, not "text".
let inputData = '';
process.stdin.on('data', chunk => {
    inputData += chunk;
});

process.stdin.on('end', () => {
    const input = JSON.parse(inputData);
    const matches = analyzePrompt(input.prompt);

    if (matches.length > 0) {
        // Context injection lives under hookSpecificOutput, mirroring the
        // shape hooks/session-start.sh uses for SessionStart (see HOOKS.md).
        console.log(JSON.stringify({
            hookSpecificOutput: {
                hookEventName: 'UserPromptSubmit',
                additionalContext: generateContext(matches)
            }
        }));
    } else {
        // No match: no output needed, exit 0 (nothing printed above).
    }
});

function analyzePrompt(text) {
    const lowerText = text.toLowerCase();
    const matched = [];

    for (const [reminderName, config] of Object.entries(rules)) {
        for (const keyword of config.keywords) {
            if (lowerText.includes(keyword.toLowerCase())) {
                matched.push({ name: reminderName, priority: config.priority || 'medium' });
                break;
            }
        }
    }

    return matched.sort((a, b) => {
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
}

function generateContext(matches) {
    return `
🎯 REMINDER CHECK

The following reminders may be relevant to this prompt:
${matches.map(m => `- **${m.name}** (${m.priority} priority)`).join('\n')}
`;
}
```

**Configuration (`keyword-rules.json`):**
```json
{
  "backend-conventions": {
    "priority": "high",
    "keywords": ["backend", "controller", "service", "API", "endpoint"]
  },
  "frontend-conventions": {
    "priority": "high",
    "keywords": ["frontend", "component", "react", "UI", "layout"]
  }
}
```

## Example 5: Error Handling Reminder (Stop)

**Purpose:** Gentle reminder to check error handling in risky code.

**File:** `~/.claude/hooks/stop/40-error-reminder.sh`

```bash
#!/bin/bash

LOG_FILE="$HOME/.claude/logs/file-edits.log"

# Get recently edited files
get_edited_files() {
    tail -20 "$LOG_FILE" 2>/dev/null | \
        cut -d'|' -f3 | \
        tr -d ' ' | \
        sort -u
}

# Check for risky patterns
check_file_risk() {
    local file="$1"

    if [ ! -f "$file" ]; then
        return 1
    fi

    # Look for risky patterns
    if grep -q -E "try|catch|async|await|prisma|\.execute\(|fetch\(|axios\." "$file"; then
        return 0
    fi

    return 1
}

# Main execution
risky_count=0
backend_files=0

for file in $(get_edited_files); do
    if check_file_risk "$file"; then
        ((risky_count++))

        if echo "$file" | grep -q "backend\|server\|api"; then
            ((backend_files++))
        fi
    fi
done

if [ "$risky_count" -gt 0 ]; then
    cat <<EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ERROR HANDLING SELF-CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Risky Patterns Detected
   $risky_count file(s) with async/try-catch/database operations

   ❓ Did you add proper error handling?
   ❓ Are errors logged/captured appropriately?
   ❓ Are promises handled correctly?

EOF

    if [ "$backend_files" -gt 0 ]; then
        cat <<EOF
   💡 Backend Best Practice:
      - All errors should be captured (Sentry, logging)
      - Database operations need try-catch
      - API routes should use error middleware

EOF
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Non-blocking
echo '{}'
```

## Example 6: Dangerous Operation Blocker (PreToolUse)

**Purpose:** Block dangerous file operations (deletion, overwrite) in production paths.

**File:** `~/.claude/hooks/pre-tool-use/dangerous-ops.sh`

```bash
#!/bin/bash

# Read tool use event. Real PreToolUse schema: top-level tool_name/tool_input
# (see hooks/pre-tool-use/02-version-bump-guard.py and HOOKS.md for the
# hook this plugin actually ships).
read -r tool_use_json

tool_name=$(echo "$tool_use_json" | jq -r '.tool_name')
file_path=$(echo "$tool_use_json" | jq -r '.tool_input.file_path // empty')

# Dangerous paths (customize for your project)
PROTECTED_PATHS=(
    "/production/"
    "/prod/"
    "/.env.production"
    "/config/production"
)

# Check if operation is dangerous
is_dangerous() {
    local path="$1"

    for protected in "${PROTECTED_PATHS[@]}"; do
        if [[ "$path" == *"$protected"* ]]; then
            return 0
        fi
    done

    return 1
}

# Check dangerous operations
if [ "$tool_name" == "Write" ] || [ "$tool_name" == "Edit" ]; then
    if is_dangerous "$file_path"; then
        reason="BLOCKED: Attempting to modify protected path ${file_path}. This path is protected from automatic modification. Use manual file editing and confirm with a teammate, or edit the PROTECTED_PATHS list in this hook to override."
        jq -n --arg reason "$reason" \
            '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
        exit 0
    fi
fi

# Allow: no output needed, exit 0 (the guard shipped with this plugin,
# hooks/pre-tool-use/02-version-bump-guard.py, follows the same
# fail-open-with-no-output convention on its allow path).
exit 0
```

## Testing These Examples

### Test Edit Tracker
```bash
# Create test log entry
mkdir -p ~/.claude/logs
echo "2025-01-15 10:30:00 | frontend | /path/to/file.ts" > ~/.claude/logs/file-edits.log

# Test formatting script
bash ~/.claude/hooks/stop/30-format-code.sh
```

### Test Build Checker
```bash
# Add some edits to log
echo "2025-01-15 10:30:00 | backend | /path/to/backend/file.ts" >> ~/.claude/logs/file-edits.log

# Run build checker
bash ~/.claude/hooks/stop/20-build-checker.sh
```

### Test Contextual Reminder Injector
```bash
# Test with a mock UserPromptSubmit event (real field is "prompt", not "text")
echo '{"prompt": "How do I create a new API endpoint?"}' | node ~/.claude/hooks/user-prompt-submit/keyword-reminder.js
```

## Debugging Tips

**Enable debug mode:**
```bash
# Add to top of any bash script
set -x
exec 2>>~/.claude/hooks/debug.log
```

**Check hook execution:**
```bash
# Watch hooks run in real-time
tail -f ~/.claude/logs/hooks.log
```

**Test hook output:**
```bash
# Capture output
bash ~/.claude/hooks/stop/20-build-checker.sh > /tmp/hook-test.log 2>&1
cat /tmp/hook-test.log
```
