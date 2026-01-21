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

1. ALWAYS use code-reviewer after changes
2. Use system-architect for complex features first
3. Use refactor-cleaner for complex implementations
4. Auto-trigger documentation-agent on API/feature changes
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

## Never

- Skip code-reviewer for significant changes
- Delegate simple tasks to system-architect
- Ignore agent feedback
- Commit without review
