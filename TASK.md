# Current Task

## Phase 14 – Authentication & RBAC

### Objective

Implement a production-quality authentication and authorization layer for the Threat Intelligence Platform.

This phase must follow security best practices.

Do not implement custom cryptography or homemade authentication mechanisms.

---

## Authentication

Implement:

- User model
- User CRUD (admin only where applicable)
- Login
- JWT Access Tokens
- JWT Refresh Tokens
- Password hashing

Use:

- passlib (bcrypt)
- python-jose (JWT)

Do not store plaintext passwords.

---

## Authorization

Implement Role-Based Access Control (RBAC).

Roles:

- admin
- analyst
- viewer

Permissions:

Admin:
- Full access

Analyst:
- Read
- Create
- Update
- Investigations
- Watchlists
- Enrichment

Viewer:
- Read-only

Authorization must be reusable through dependencies.

Do not duplicate permission checks in routers.

---

## User Model

Include:

- id
- username
- email
- password_hash
- role
- is_active
- created_at
- updated_at
- last_login

---

## Service Layer

Create AuthService.

Responsibilities:

- login
- password verification
- token generation
- token refresh
- current user lookup

Business logic belongs here.

---

## Security

Passwords:

- bcrypt
- configurable work factor

JWT:

- signed
- expiration
- refresh token support

Never log:

- passwords
- password hashes
- JWTs

---

## API

Implement:

POST /auth/login

POST /auth/refresh

GET /auth/me

POST /users

GET /users

GET /users/{id}

PATCH /users/{id}

DELETE /users/{id}

---

## Dependencies

Provide reusable dependencies:

- get_current_user
- require_admin
- require_analyst
- require_viewer

Existing routers should be protected using these dependencies where appropriate.

Do not duplicate authorization logic.

---

## Database

Create proper Alembic migrations.

Seed one initial admin account if required by the specification.

Do not hardcode credentials.

---

## Logging

Log:

- successful login
- failed login
- refresh events
- authorization failures

Never log secrets.

---

## Error Handling

401

- invalid credentials
- invalid token
- expired token

403

- insufficient permissions

404

- missing user

422

- validation failures

---

## Non Goals

Do not implement:

- OAuth
- SAML
- LDAP
- MFA
- API Keys
- Session authentication

---

## Deliverables

- `[x]` User model
- `[x]` AuthService
- `[x]` JWT authentication
- `[x]` RBAC
- `[x]` Protected routes
- `[x]` Alembic migration
- `[x]` IMPLEMENTATION_CONTEXT.md update