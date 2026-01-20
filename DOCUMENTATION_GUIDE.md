# Documentation Guide - Quick Reference

## Where to Find Documentation

All project documentation is in **`/docs`**.

### Main Sections

1. **[docs/README.md](./docs/README.md)** - Documentation hub
2. **[docs/architecture/](./docs/architecture/)** - System architecture
3. **[docs/api/](./docs/api/)** - API reference
4. **[docs/guides/](./docs/guides/)** - Guides
5. **[docs/development/](./docs/development/)** - Developer docs

## Documentation Agent

**Location**: `.claude/agents/documentation-agent.md`

### Commands

```bash
/docs update          # Update all documentation
/docs verify          # Verify accuracy
/docs api Services    # Update API docs
/docs architecture    # Update architecture docs
```

## When to Update

Update documentation when you:
- Add new features/services
- Modify APIs
- Change architecture/patterns
- Update dependencies/configuration
- Fix bugs affecting documented behavior

## Workflow

### Automatic (Recommended)
1. Make code changes
2. Documentation agent auto-detects changes
3. Updates relevant docs
4. Commit code + docs together

### Manual
1. Make code changes
2. Update files in `/docs`
3. Commit together:
   ```bash
   git add bot/services/new_service.py docs/api/services.md
   git commit -m "feat: Add NewService with documentation"
   ```

## Document Structure

```markdown
# Document Title

## Overview
Brief description

## Main Sections
...

## Further Reading
- [Related Document](./related.md)

---

**Last Updated**: YYYY-MM-DD
**Maintained by**: Documentation Agent
```

## Quick Links

| Need | Where |
|------|-------|
| Get Started | [Quick Start](./docs/guides/quickstart.md) |
| Architecture | [System Overview](./docs/architecture/system-overview.md) |
| API Reference | [Services API](./docs/api/services.md) |
| Database | [Database Schema](./docs/architecture/database-schema.md) |
| Documentation Workflow | [Workflow](./docs/development/documentation-workflow.md) |

## Search Documentation

```bash
# All documentation
grep -r "search term" docs/

# Specific category
grep -r "SearchTerm" docs/api/

# List all files
find docs -name "*.md" -type f
```

## Principles

1. **Single Source of Truth** - Everything in `/docs`
2. **Always Current** - Updated with code changes
3. **Comprehensive** - Full coverage
4. **Clear Examples** - Code examples included

## Help

If you can't find what you need:
1. Check [docs/README.md](./docs/README.md)
2. Search: `grep -r "topic" docs/`
3. Ask documentation agent: `/docs find topic`
4. Create GitHub issue

---

**Remember**: Good documentation makes the project accessible to everyone.
