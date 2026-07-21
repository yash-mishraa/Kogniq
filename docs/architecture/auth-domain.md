# Authentication Domain Architecture

Kogniq handles authentication by strictly separating identity resolution from domain logic, using an abstraction over authentication providers (like Better Auth). This design ensures that the application domain is never tightly coupled to specific authentication systems, HTTP logic, or JWT tokens.

## Architecture Pattern

```mermaid
sequenceDiagram
    participant Router as API Router
    participant Service as AuthenticationService
    participant Provider as AbstractAuthenticationProvider
    participant Repo as AbstractUserRepository
    
    Router->>Service: authenticate(request)
    Service->>Provider: authenticate(request)
    Provider->>Repo: get_user_by_email()
    Repo-->>Provider: User
    Provider-->>Service: AuthenticationResult
    Service-->>Router: Result (User + Session)
```

## Bounded Context (`kogniq-auth`)

The `kogniq-auth` package contains:
- **Models**: Immutable structures (`User`, `Identity`, `Session`, `AuthenticationResult`).
- **Interfaces**: `AbstractAuthenticationProvider`, `AbstractUserRepository`.
- **Adapters**: `MemoryAuthenticationProvider`, `MemoryUserRepository` (for testing).

### Why Abstract Providers?
By routing authentication through `AbstractAuthenticationProvider`, we guarantee that if we switch from Better Auth to Clerk or Auth0, the `AuthenticationService` and backend routes never need to change. The implementation detail (how a session is generated, how cookies are parsed, how OAuth exchanges work) is encapsulated inside the concrete provider implementation.

## Models and Identities
A `User` represents a person in our system.
An `Identity` maps a third-party login (e.g. Google, GitHub) to a `User`. This supports users logging in via multiple providers seamlessly into the same `User` account.

```mermaid
erDiagram
    USER ||--o{ IDENTITY : "has many"
    USER ||--o{ SESSION : "owns"
    
    USER {
        string user_id
        string email
    }
    
    IDENTITY {
        string identity_id
        string provider
        string provider_user_id
    }
    
    SESSION {
        string session_id
        datetime expires_at
        boolean is_active
    }
```
