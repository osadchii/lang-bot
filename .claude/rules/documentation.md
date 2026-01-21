# Documentation Rules

## Structure

```
docs/
├── README.md              # Hub
├── architecture/          # System design
├── api/                   # API reference
├── guides/                # User guides
└── development/           # Developer docs
```

## Update Triggers

- New features/services
- API modifications
- Architecture changes
- Configuration updates
- Behavior-affecting bug fixes

## Documentation Agent

```bash
/docs update          # Update all
/docs verify          # Verify accuracy
/docs api Services    # Update service APIs
```

## Principles

- Single source of truth in `/docs`
- Always keep current with code
- Comprehensive coverage
- English language only

## Requirements

- Document all public service methods
- Document all handlers/commands
- Document model relationships
- Document configuration options
- Document deployment procedures

## Never

- Leave outdated documentation
- Document in README.md (use /docs)
- Mix languages (English only)
- Skip documentation for new features
