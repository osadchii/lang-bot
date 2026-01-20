# Project Agents

This directory contains specialized agent configurations for maintaining and working with this project.

## Available Agents

### Documentation Agent

**File**: `documentation-agent.md`

**Purpose**: Maintains comprehensive, up-to-date documentation in the `/docs` directory.

**Responsibilities**:
- Keep documentation synchronized with codebase
- Update docs automatically when code changes
- Ensure all examples and code snippets are working
- Verify API references match actual implementations
- Maintain documentation structure and quality

**Usage**:
```bash
# In Claude Code
/docs update           # Update all documentation
/docs verify          # Verify documentation accuracy
/docs api ServiceName # Update specific API docs

# Mention in conversation
"documentation agent, please update the architecture docs"
```

**Triggers**:
- Automatic: Code changes in `bot/` directory
- Manual: `/docs` command or explicit mention
- On demand: Pull request reviews

## How Agents Work

Agents are specialized AI assistants with specific roles and responsibilities. They have:

1. **Clear Role**: Defined purpose and scope
2. **Specific Tools**: Access to relevant tools (Read, Write, Edit, etc.)
3. **Best Practices**: Guidelines for their work
4. **Triggers**: When they automatically activate

## Adding New Agents

To add a new agent:

1. Create `agent-name.md` in this directory
2. Define role, responsibilities, and tools
3. Document usage and triggers
4. Update this README
5. Configure in Claude Code settings (if needed)

## Integration with Development

Agents work alongside developers:

- **Documentation Agent**: Keeps docs current as you code
- **Review Agent** (future): Automated code review
- **Testing Agent** (future): Test generation and validation
- **Migration Agent** (future): Database migration assistance

## Further Reading

- [Documentation Workflow](../docs/development/documentation-workflow.md)
- [Claude Code Agents Documentation](https://docs.anthropic.com/claude/docs)

---

**Note**: Agent configurations in this folder are version-controlled and shared across the team.
