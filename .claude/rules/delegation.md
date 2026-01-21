# Delegation Rules

## Agents

### system-architect
**Use for:** Complex feature planning, architecture decisions, major refactoring design
**Triggers:** Multi-file changes, new subsystems, schema changes

### code-reviewer (MANDATORY)
**Use for:** ALWAYS after code changes, before committing
**Checks:** Style, no dead code, patterns, error handling, tests, docs

### refactor-cleaner
**Use for:** After complex implementations, simplifying logic, cleanup
**Triggers:** Functions >50 lines, nested conditionals >3 levels, duplicate code

### devops-engineer
**Use for:** Deployment config, CI/CD, Docker, production migrations

### documentation-agent (AUTOMATIC)
**Triggers:** New features, API changes, architecture changes, behavior fixes
**Manual:** `/docs update`, `/docs verify`, `/docs api Services`

## Workflows

### Feature
```
system-architect (if complex) → Implementation → code-reviewer → refactor-cleaner (if needed) → code-reviewer → documentation-agent → Commit
```

### Bug Fix
```
Investigation → Fix → code-reviewer → documentation-agent (if behavior changes) → Commit
```

### Refactoring
```
system-architect (if major) → refactor-cleaner → code-reviewer → documentation-agent (if APIs change) → Commit
```

## Rules

### MANDATORY BEFORE PUSH (NON-NEGOTIABLE)
1. **code-reviewer** - Run for ANY code change, no exceptions
2. **documentation-agent** - Run for ANY feature/behavior change

### General
3. Use system-architect for complex features first
4. Use refactor-cleaner for complex implementations
5. Use devops-engineer for deployment tasks

## Handoff Requirements

When delegating, provide:
1. What was done
2. Why
3. Files affected
4. Task for agent
5. Special considerations

## Escalate to User

- Architectural decisions (multiple valid approaches)
- Ambiguous requirements
- Breaking changes
- Security trade-offs
- Performance vs complexity

## Skip Delegation

- Trivial changes (typo fixes, log additions)
- Simple CRUD following existing patterns
- Documentation-only changes
- Configuration updates

## Pre-Push Checklist

Before EVERY push, complete these steps IN ORDER:
1. [ ] Run `make verify` (lint, format, types, tests)
2. [ ] Run **code-reviewer** agent
3. [ ] Run **documentation-agent** (if feature/behavior changed)
4. [ ] Address any feedback from agents
5. [ ] Commit and push

## Never

- Push without running code-reviewer
- Push feature changes without documentation-agent
- Delegate simple tasks to system-architect
- Ignore agent feedback
- Skip the pre-push checklist
