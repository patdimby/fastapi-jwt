# Testing — FastAPI JWT Mini Blog

Verified on 2026-09-30 with Python 3.12.14: **19 tests passed**, **99% statement coverage** (97/98 statements). The untested statement is the invalid signing-configuration startup guard.

```bash
pip install -r requirements-dev.txt
pytest --cov=app --cov=main --cov-report=term-missing
```

Coverage includes `main.py` and all modules under `app`. Tests set a test-only signing secret before importing the application and restore posts/clear accounts around each case.

The suite exercises public reads, missing posts, signup, duplicate email, second-account login, bad credentials, schema validation, protected creation, server-assigned IDs, safe user-directory output, password salts/verification and JWT lifetime. Invalid bearer cases include absent credentials, malformed tokens, expiry, wrong signature, and missing identity/expiration claims.

The delivery fixes mismatched expiry claims/algorithm parameters, truthy JWT error results, early-return user lookup, optional-but-required schema fields, plaintext password storage and credential exposure. Tokens and response contracts are documented in README.

Tests are HTTP/component-level rather than browser, load, concurrency or persistent-storage tests. The project has no database. GitHub Actions was added but not executed remotely. A harmless Starlette/AnyIO deprecation warning appears in the verified local environment.
