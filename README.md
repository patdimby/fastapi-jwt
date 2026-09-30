# FastAPI JWT Mini Blog

A compact Python API demonstrating account registration, password hashing, signed JWT authentication, and protected post creation. It is designed to be easy to read, run, and test.

**FastAPI · Pydantic 2 · PyJWT · PBKDF2 · Pytest · GitHub Actions**

## Features

- Public post listing and lookup, with three example posts.
- Account signup and login using email/password.
- Salted PBKDF2 password hashes; plaintext passwords are never stored.
- One-hour HS256 JWTs, with signature and required-claim validation.
- Authenticated post creation and a user directory that excludes credentials.
- Request validation, meaningful HTTP errors, isolated HTTP tests and CI.

Users and posts live in process memory. They reset on restart and are not shared across worker processes. There is no database, frontend, post update/delete, ownership model, refresh token, or email-verification workflow.

## Quick start

Use Python 3.12 for the verified workflow.

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp .env.example .env
# Windows PowerShell: Copy-Item .env.example .env
python secret_generator.py
```

Copy the generated random secret into the `secret` value of `.env`, then run:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** for interactive OpenAPI documentation. Start commands from the project root so the optional `.env` file resolves consistently.

## Configuration

| Setting | Requirement | Purpose |
| --- | --- | --- |
| `secret` | Required; at least 32 UTF-8 bytes | HS256 signing key |
| `algorithm` | `HS256` | Explicit signing/verification algorithm |

`python-decouple` reads configuration from environment variables or `.env`. Environment variables take precedence. Invalid signing configuration fails at import/startup. Never commit `.env`.

## API

| Method | Route | Behavior | Access |
| --- | --- | --- | --- |
| GET | `/` | Welcome message | Public |
| GET | `/posts` | All shared posts | Public |
| GET | `/posts/{id}` | One post; missing ID returns `404` | Public |
| POST | `/posts` | Create a post | Bearer JWT |
| POST | `/users/signup` | Create account and return token | Public |
| POST | `/users/login` | Return token for valid credentials | Public |
| GET | `/users` | Names/emails only | Bearer JWT |

Signup body:

```json
{"fullname":"Ada Lovelace","email":"ada@example.com","password":"example-password"}
```

Login body:

```json
{"email":"ada@example.com","password":"example-password"}
```

For compatibility, the response retains the original key **`access token`**, including its space:

```json
{"access token":"YOUR_JWT"}
```

Use it as `Authorization: Bearer YOUR_JWT`. Post creation accepts:

```json
{"title":"A useful article","content":"Article text"}
```

The server assigns the post ID and returns a success message. Signup requires a nonempty name, valid email, and password of at least eight characters. Duplicate email returns `409`; invalid fields return `422`; bad login or missing/invalid bearer credentials return `401`.

All authenticated users share the same post collection and user directory. The JWT contains an email identity but the bearer guard does not check whether the account still exists. Tokens have no server-side revocation.

## Tests

```bash
pytest --cov=app --cov=main --cov-report=term-missing
```

**Verified:** 19 tests passed; statement coverage is 99% (97 of 98 statements). Tests isolate the mutable stores, use a test-only signing secret, and exercise actual HTTP routes with FastAPI's test client.

See [TESTING.md](TESTING.md) for scope and limitations. GitHub Actions runs the suite on Python 3.12.

## Layout

```text
main.py                 HTTP routes and temporary stores
app/model.py            Pydantic request schemas
app/auth/jwt_handler.py  Token creation and verification
app/auth/jwt_bearer.py   Protected-route dependency
app/auth/passwords.py    Salted password hashing
secret_generator.py     Random local secret generation
tests/                  HTTP and authentication tests
.github/workflows/      CI
```

Read [ARCHITECTURE.md](ARCHITECTURE.md) for request flow and design limits. [GITHUB_DESCRIPTION.md](GITHUB_DESCRIPTION.md) contains a ready-to-use repository description.

## Deployment and contribution

This is a single-process demonstration. Add persistent storage, transaction-safe identifiers, rate limiting, account lifecycle controls and a deliberate authorization model before using it as a shared service. Use HTTPS outside local development. Test changes with the supplied suite and keep credentials out of commits.

No project license file was included in the original archive; choose a license before advertising reuse terms.
