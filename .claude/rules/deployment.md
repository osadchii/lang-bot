# Deployment Rules

## Database Migrations

### ALWAYS

- Create migration after model changes: `alembic revision --autogenerate -m "description"`
- Review generated migration before applying
- Test migrations on development database first
- Use `alembic upgrade head` for production

### NEVER

- Modify models without migration
- Manually alter production schema
- Apply untested migrations to production
- Skip migration versioning

## Deployment Checklist

1. All tests pass (`pytest --cov=bot --cov-fail-under=80`)
2. Code formatted (`black --check bot/`)
3. No lint errors (`ruff check bot/`)
4. Migrations reviewed and tested
5. Documentation updated
6. Environment variables configured
7. Code reviewed and approved

## Environment Variables

Required in `.env`:
```
TELEGRAM_BOT_TOKEN
DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY
```

## Migration Strategy

1. Backup database
2. Apply migrations (`alembic upgrade head`)
3. Restart application
4. Verify functionality
5. Monitor logs

## Rollback Procedure

1. Stop application
2. Rollback migration (`alembic downgrade -1`)
3. Restore code to previous version
4. Restart application
5. Verify rollback success

## Production Safeguards

- NEVER use `alembic downgrade` without backup
- NEVER push directly to main branch
- NEVER deploy without code review
- NEVER skip testing phase
- ALWAYS use pull requests
- ALWAYS review migration SQL
- ALWAYS have rollback plan

## CI/CD Pipeline

1. Run tests
2. Check formatting
3. Run linting
4. Check coverage threshold
5. Build Docker image (if applicable)
6. Deploy to staging
7. Run smoke tests
8. Deploy to production (manual approval)

## Monitoring

- Check application logs after deployment
- Monitor error rates
- Verify database connections
- Check API response times
- Monitor SRS algorithm performance
