# Greek Language Learning Bot - Documentation

Welcome to the comprehensive documentation for the Greek Language Learning Telegram Bot.

**Target Audience**: Russian-speaking users learning Greek.

## Documentation Structure

This documentation is organized into the following sections:

### [Architecture](./architecture/)
Technical architecture, design patterns, and system design decisions.

- [System Overview](./architecture/system-overview.md) - High-level architecture
- [Database Schema](./architecture/database-schema.md) - Database models and relationships
- [Middleware Chain](./architecture/middleware-chain.md) - Request processing pipeline
- [Service Layer](./architecture/service-layer.md) - Business logic organization

### [API Reference](./api/)
Detailed API documentation for all components.

- [Services API](./api/services.md) - Service layer methods (AIService, ConversationService, TranslationService, etc.)
- [Repositories API](./api/repositories.md) - Data access layer
- [Telegram Handlers](./api/handlers.md) - Bot command handlers
- [Utilities](./api/utilities.md) - Helper functions and utilities

### [Guides](./guides/)
Step-by-step guides for common tasks.

- [Quick Start](./guides/quickstart.md) - Get up and running quickly
- [Setup Guide](./guides/setup.md) - Complete installation instructions
- [Deployment Guide](./guides/deployment.md) - Production deployment
- [Contributing Guide](./guides/contributing.md) - How to contribute

### [Development](./development/)
Information for developers working on the project.

- [Development Setup](./development/setup.md) - Local development environment
- [Code Review Standards](./development/code-review.md) - Quality standards
- [Testing Guide](./development/testing.md) - Writing and running tests
- [Migration Guide](./development/migrations.md) - Database migrations
- [Documentation Workflow](./development/documentation-workflow.md) - How to update docs

### [Deployment](./deployment/)
Production deployment and CI/CD setup.

- [CI/CD Setup](./deployment/ci-cd-setup.md) - GitHub Actions, Docker, secrets management

## Quick Links

- **Getting Started**: Start with [Quick Start Guide](./guides/quickstart.md)
- **For Developers**: Read [Development Setup](./development/setup.md)
- **Architecture Overview**: See [System Overview](./architecture/system-overview.md)
- **API Reference**: Check [Services API](./api/services.md)

## Key Features

- **AI-Powered Message Handling**: Send any text - the bot categorizes your intent (translation, question, etc.)
- **Smart Translation**: Translates words, checks existing cards, suggests appropriate decks
- **Vocabulary Extraction**: Extracts learnable words from translated phrases, filters function words, and offers to add new vocabulary to your decks
- **Conversation History**: AI remembers context for more natural interactions
- **Spaced Repetition**: SM-2 algorithm for optimal card scheduling
- **Grammar Exercises**: Practice verb conjugations, tenses, and noun cases

## Documentation Maintenance

This documentation is maintained by the **Documentation Agent** and follows these principles:

1. **Single Source of Truth** - All project documentation lives here
2. **Always Up-to-Date** - Updated automatically when code changes
3. **Comprehensive** - Covers architecture, APIs, guides, and development
4. **Clear and Concise** - Easy to understand for all skill levels

## Last Updated

This documentation is automatically maintained. For the latest updates, check the git commit history:

```bash
git log docs/
```

## Contributing to Documentation

If you notice outdated or incorrect documentation:

1. Create an issue describing the problem
2. Submit a pull request with corrections
3. Contact the documentation agent for major updates

---

**Note**: This documentation is generated and maintained automatically. For code-specific documentation, see inline comments and docstrings in the source code.

**Last Updated**: 2026-01-22
