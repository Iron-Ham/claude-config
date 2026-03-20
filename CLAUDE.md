# Personal Claude Code Instructions

## Agent Delegation Strategy

### General Rules
- Always use `model: "sonnet"` when spawning Explore agents via the Task tool
- **Prefer delegating** to a specialized agent when the task requires domain depth (architecture, security, UX, performance, etc.) — don't do specialist work inline when a purpose-built agent exists
- **Do work inline** for quick, focused tasks that don't need specialist knowledge
- **Parallel-spawn** independent agents when a task decomposes into sub-problems in different domains
- Use `isolation: "worktree"` for agents making code changes in parallel to avoid conflicts

### Task → Agent Routing

When you recognize these patterns, spawn the matching agent:

| Task pattern | Agent(s) to spawn |
|---|---|
| System design, architecture decisions | Software Architect |
| Deep code review | Code Reviewer |
| Security audit, threat modeling | Security Engineer |
| Database schema/query optimization | Database Optimizer |
| CI/CD, deployment, infrastructure | DevOps Automator |
| Complex frontend implementation | Frontend Developer |
| API design/backend implementation | Backend Architect |
| Performance investigation | Performance Benchmarker |
| Comprehensive test execution | Evidence Collector, API Tester |
| UX/design decisions | UX Architect, UI Designer |
| Developer documentation | Technical Writer |
| Production incident | Incident Response Commander |
| Mobile app work | Mobile App Builder |
| AI/ML features | AI Engineer |
| Git workflow complexity | Git Workflow Master |
| Accessibility audit | Accessibility Auditor |

### Multi-Agent Orchestration (NEXUS)

For tasks requiring multiple specialists, reference the NEXUS framework:
- **Docs:** `~/.claude/agents/strategy/QUICKSTART.md` (start here)
- **Full doctrine:** `~/.claude/agents/strategy/nexus-strategy.md`
- **Activation prompts:** `~/.claude/agents/strategy/coordination/agent-activation-prompts.md`
- **Runbooks:** `~/.claude/agents/strategy/runbooks/` (MVP, enterprise feature, marketing campaign, incident response)

Modes:
- **NEXUS-Micro** (1-5 days): bug fix, audit, single campaign — 5-10 agents
- **NEXUS-Sprint** (2-6 weeks): feature or MVP — 15-25 agents
- **NEXUS-Full** (12-24 weeks): complete product — all agents

When a task is clearly multi-phase or cross-domain, spawn the **Agents Orchestrator** to coordinate rather than managing agents yourself.

### Domain-Specific Agent Groups

Beyond engineering, remember these specialist clusters exist:
- **Sales:** Discovery Coach, Deal Strategist, Pipeline Analyst, Sales Engineer, Outbound Strategist
- **Marketing:** Platform specialists (TikTok, Instagram, LinkedIn, Reddit, Twitter, etc.), Content Creator, Growth Hacker, SEO Specialist
- **Product:** Product Manager, Sprint Prioritizer, Trend Researcher, Feedback Synthesizer
- **Design:** UX Architect, UI Designer, Brand Guardian, UX Researcher
- **Testing/QA:** Reality Checker (final authority), Evidence Collector, Performance Benchmarker, API Tester
- **Project Management:** Studio Producer, Senior Project Manager, Jira Workflow Steward
- **Spatial Computing:** visionOS Spatial Engineer, macOS Spatial/Metal Engineer, XR agents
- **Game Development:** Unity, Unreal, Godot, Roblox specialists + Narrative/Game/Level designers

## Git Commit Guidelines

When creating git commits:

- **NEVER** add co-author lines (e.g., `Co-Authored-By: ...`)
- **NEVER** add "Generated with Claude Code" or similar attribution phrases
- **NEVER** reference Claude, Claude Code, AI, or any assistant in commit messages
- **NEVER** add links to claude.ai or anthropic.com in commits
- **NEVER** add emoji attributions like 🤖

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat: add user authentication endpoint`
- `fix: resolve memory leak in cache handler`
- `docs: update API documentation`
- `refactor: extract validation logic`
- `test: add unit tests for auth module`
- `chore: update dependencies`

Rules:
- Use lowercase for the type and description
- Keep subject line under 72 characters
- Use imperative mood ("add" not "added")
- No period at end of subject line

## Pull Request Guidelines

When creating pull requests:

- **ALWAYS** open PRs as **drafts** (`gh pr create --draft`) unless the user explicitly asks for a non-draft / ready-for-review PR
- **NEVER** add "Generated with Claude Code" or similar attribution phrases
- **NEVER** reference Claude, Claude Code, AI, or any assistant in PR titles or bodies
- **NEVER** add links to claude.ai or anthropic.com
- **NEVER** add emoji attributions like 🤖

### PR Format

- Title should be a meaningful, human-readable description of the change
- Do NOT use conventional commit prefixes like `feat:`, `fix:`, `chore:` in PR titles
- Write titles that clearly communicate what the PR accomplishes to reviewers
- Link to GitHub issues when applicable using `Closes #123` or `Fixes #456`
- Focus on the **what** and **why**, not the how
- Include a test plan section

Examples of good PR titles:
- "Add user authentication endpoint"
- "Fix memory leak in cache handler"
- "Update API documentation for v2 endpoints"
- "Extract validation logic into shared utility"

Examples of bad PR titles:
- "feat: add user authentication endpoint"
- "chore: update dependencies"
- "fix: bug"

## Branch Workflow

### Protected Branches

- **NEVER** commit directly to `main` or `master`
- **ALWAYS** create a feature branch before making changes
- If already on main/master, create a branch first before any commits

### Branch Naming

Use the format: `Iron-Ham/<description>`

Examples:
- `Iron-Ham/add-user-auth`
- `Iron-Ham/fix-memory-leak`
- `Iron-Ham/refactor-api-client`

For stacked branches, add numbered suffixes:
- `Iron-Ham/auth-1-models`
- `Iron-Ham/auth-2-endpoints`
- `Iron-Ham/auth-3-tests`

### One Commit Per Branch

Prefer working in branches where **each branch contains exactly one commit**. This supports a stacked branch workflow where:

- Each feature branch has a single, well-crafted commit
- When making the **first change** on a branch, **create a new commit**
- When making **additional changes** to a branch, **amend the existing commit** rather than creating new commits
- This makes rebasing stacked branches trivial after parent branches are squash-merged into `main`

When working on a branch:
- Use `git commit` for the initial commit
- Use `git commit --amend` for all subsequent changes
- Use `git push --force-with-lease` when updating remote branches after amending

### Edge Cases

**If branch already has multiple commits:**
- Do NOT squash or rewrite history without explicit user confirmation
- Ask user how they want to proceed

**If working on a shared/collaborative branch:**
- Do NOT force push without explicit user instruction
- Use regular `git push` and handle conflicts normally
- **Assume any branch NOT matching `Iron-Ham/*` is shared/collaborative** (e.g., someone else's PR, a release branch, etc.)

**If branch is stale and needs updating:**
- Use `git pull --rebase` to keep history linear

### Pre-Push / Pre-PR Rebase

Before pushing to remote or opening a pull request, **always** ensure the branch is rebased on the latest base branch (which may be `main`, `master`, or a parent feature branch in a stacked PR workflow):

1. Run `git fetch origin` to get the latest remote state
2. Determine the correct base branch (e.g., `main` for standalone PRs, or the parent branch for stacked PRs)
3. Run `git rebase origin/<base-branch>` to rebase onto the latest base
4. Resolve any conflicts before proceeding
5. Only then push or create the PR

This ensures PRs are always up-to-date and minimizes merge conflicts.

## Testing Requirements

- Write tests for new functionality when a test suite exists in the project
- Run existing tests before committing to ensure no regressions
- If tests fail, fix them before proceeding (unless user explicitly says otherwise)
- Match the testing patterns and frameworks already used in the project

## Documentation Style

- Add inline comments only for complex or non-obvious logic
- Do NOT add comments that merely restate what the code does
- Update existing documentation (README, docstrings) when changing public APIs
- Do NOT create new documentation files unless explicitly requested
- Match the documentation style already present in the project
