# Capstone Vulnerable Spring Test App

A deliberately vulnerable Spring Boot application used to develop and validate the
[Capstone vulnerability scanner](https://github.com/vurs/capstone-vulnerability-scanner).
It provides predictable browser and API findings for Dynamic Application Security
Testing (DAST).

> [!CAUTION]
> This application is vulnerable by design. Run it only locally or behind the
> repository's restricted AWS deployment. Never expose it to the public internet
> or use it with real data or credentials.

The local stack uses Java 17, Spring Boot 4.0.3, Thymeleaf, PostgreSQL 15,
Keycloak 26.6.1, and Docker Compose.

## Quick start

### Prerequisites

- Git
- Docker Desktop with Docker Compose

### 1. Clone and initialize

```bash
git clone https://github.com/vurs/capstone-test-website-spring.git
cd capstone-test-website-spring
```

Run the one-time development setup:

```powershell
# Windows PowerShell
.\dev_scripts\setup_dev.ps1
```

```bash
# macOS or Linux
./dev_scripts/setup_dev.sh
```

This installs the repository's Git commit hook and creates the `.dev-env-stamp`
files required at startup.

### 2. Start the stack

```bash
docker compose up --build
```

The app container waits 30 seconds before starting Spring Boot. When it is ready:

| Service | URL |
|---|---|
| Vulnerable application | <http://localhost:8081> |
| Browser login | <http://localhost:8081/login> |
| OpenAPI specification | <http://localhost:8081/v3/api-docs> (requires authenticated session) |
| Keycloak administration | <http://localhost:8080> |

Use `testuser` / `password` for the test account. The local Keycloak administrator
is `admin` / `admin`.

All application routes require authentication except `/login`, the OAuth2 callbacks,
`/api/auth/login`, `/api/session/me`, and `/error`. Visiting the app redirects
anonymous browsers to Keycloak. `/login` starts the Keycloak flow directly.
Requesting `/v3/api-docs` without a session also redirects to login.
**Logout** clears both the application session and the Keycloak SSO session, then
returns to `/login` so the next sign-in prompts for credentials again.

### 3. Stop or reset

Use `docker compose down` to preserve PostgreSQL data or
`docker compose down -v` for a clean reset.

## Vulnerability test surface

These routes are intentionally unsafe so the scanner can test stable, known
findings. Unless noted below, they require an authenticated session (Keycloak
browser login or `POST /api/auth/login`).

| Finding | Routes | Intentional behavior |
|---|---|---|
| Cross-site scripting | `/new`, `/post-list`, `/post/{id}` | Blog content is rendered without normal output escaping |
| SQL injection | `/users/search?username=...` | Input is concatenated into a SQL query |
| Broken access control (IDOR) | `/users/profile?userId=...` | Profiles are available by numeric ID without authorization |
| Command injection | `/network/ping?host=...` | Input is concatenated into a shell command |
| Missing anti-CSRF protection | `/csrf-demo`, `/unsafe-forms/**` | Forms omit tokens and their endpoints skip CSRF validation |
| Clickjacking and missing headers | `/clickjacking-demo` | Spring Security header writers are disabled |
| Error exposure | `/error/python-stack`, `/error/java-stack`, `/error/php-error`, `/error/database-error`, `/api/error/users`, and related `/error/*` fixtures | Responses contain stack traces, framework errors, and database errors |
| Exposed resources | `/admin`, `/backup`, `/uploads`, `/config`, `/debug-info`, `/.env`, `/config.yml`, backup-like files, and `/.git/config` | Predictable sensitive resources are readable when authenticated |
| Data masking | `/masking-demo`, `/masking-samples`, `/masking-samples.txt`, and selected error routes | Responses contain fake passwords, tokens, API keys, session IDs, cookies, and authorization headers |

Useful combined error-exposure and masking fixtures (also linked from `/masking-demo`):

```text
/error/php-error?session_id=php-url-session-mask-test&api_key=php-url-api-key-mask-test&token=php-url-token-mask-test
/api/error/users?session_id=api-url-session-mask-test&api_key=api-url-api-key-mask-test&token=api-url-token-mask-test
```

All secret-like values returned by this application are fake test fixtures.

## Scanner testing

The OpenAPI specification and injectable endpoints are available on port `8081`;
no separate API server is required.

| Method | Route | Input | Test case |
|---|---|---|---|
| `GET` | `/users/search` | `username` | SQL injection |
| `GET` | `/users/profile` | `userId` | Broken access control |
| `GET` | `/network/ping` | `host` | Command injection |

These endpoints require authentication. Use Keycloak for browser scans or
`POST /api/auth/login` for scanner-managed API sessions.

### Scanner-managed authentication

The application provides a JSON login that is separate from Keycloak:

```http
POST /api/auth/login
Content-Type: application/json

{"username":"testuser","password":"password"}
```

A successful login sets a session cookie. `GET /api/session/me` returns the
username for an active session or HTTP `401` when logged out.

Run an authenticated API-only scan with:

```bash
python main.py http://127.0.0.1:8081 \
  --scan-profile api \
  --openapi-url /v3/api-docs \
  --auth-api-url /api/auth/login \
  --auth-field username=testuser \
  --auth-field password=password \
  --auth-session-probe-url /api/session/me \
  --auth-session-probe-json-field username
```

For authenticated web scans, use `/login` as the login page URL with the same JSON
API login so the scanner does not need to drive the Keycloak UI directly:

```bash
python main.py http://127.0.0.1:8081 http://127.0.0.1:8081/login \
  --auth-api-url /api/auth/login \
  --auth-field username=testuser \
  --auth-field password=password \
  --auth-session-probe-url /api/session/me \
  --auth-session-probe-json-field username
```

Run these commands from the [Capstone vulnerability scanner](https://github.com/vurs/capstone-vulnerability-scanner)
repository. See its README for scanner profiles, crawl modes, and CI integration.

## Development

### Build and test

Using JDK 17 and Maven 3.9 or newer:

```bash
cd app
mvn test
```

To verify the application image:

```bash
docker compose build app
```

The setup script configures a commit hook that requires a Jira ID in the branch
name, such as `SCRUM-123-short-description`. Commit messages are automatically
prefixed with that ID.

## AWS deployment

GitHub Actions can provision the app on a restricted EC2 instance using Terraform
and Ansible, then temporarily allowlist a scanner runner and publish scan results.
Deployment details are stored in private AWS Systems Manager parameters instead
of public workflow logs.

See [infra/README.md](infra/README.md) for required secrets, IAM configuration,
cost guidance, deployment, teardown, and operator access.

## Troubleshooting

- **Missing `.dev-env-stamp`:** rerun the appropriate setup script from the
  repository root.
- **App not ready:** allow for the 30-second startup delay and run
  `docker compose logs -f app`.
- **Keycloak login fails to resolve `host.docker.internal`:** add
  `127.0.0.1 host.docker.internal` to the host machine's hosts file.
- **Port conflict:** the stack requires host ports `5432`, `8080`, and `8081`.
  Stop the conflicting service or change the mappings in `docker-compose.yml`.

## Related links

- [Capstone vulnerability scanner](https://github.com/vurs/capstone-vulnerability-scanner)
- [AWS deployment guide](infra/README.md)
- [Team Jira board](https://sheridan-cyber-capstone-2026.atlassian.net/jira/software/projects/SCRUM/boards/1)
