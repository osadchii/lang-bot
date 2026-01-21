# Development Rules

This directory contains all development rules and guidelines for the project.

## Files

### [constraints.md](./constraints.md)
**NON-NEGOTIABLE** constraints that must never be violated:
- Architecture layer separation
- Database session management
- SRS field modifications
- Async requirements
- Code style standards

### [architecture.md](./architecture.md)
Architecture patterns and structure:
- Layer responsibilities
- Middleware chain
- FSM patterns
- SRS integration
- Router registration

### [development.md](./development.md)
Development guidelines:
- Code style (Black, Ruff)
- Async patterns
- Error handling
- HTML formatting
- Database patterns

### [testing.md](./testing.md)
Testing requirements:
- Coverage targets
- Test structure
- Fixtures
- Patterns
- CI requirements

### [delegation.md](./delegation.md)
Agent delegation rules:
- When to use each agent
- Delegation workflows
- Handoff requirements
- Escalation rules

### [documentation.md](./documentation.md)
Documentation maintenance:
- Structure
- Update triggers
- Documentation agent usage
- Principles

### [deployment.md](./deployment.md)
Deployment procedures:
- Migration requirements
- Deployment checklist
- Environment variables
- Rollback procedures

## Usage

**Before making changes**, read relevant rule files:
- New feature → Read all files
- Bug fix → constraints.md, development.md
- Refactoring → constraints.md, architecture.md
- Deployment → deployment.md

## Enforcement

Rules in **constraints.md** are NON-NEGOTIABLE. Other files provide guidelines and best practices.

All agents must follow these rules when working on the project.
