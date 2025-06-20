# ADR-001: Adopt Clean Architecture for V2

## Status
Accepted

## Date
2025-01-14

## Context
The current XWE codebase has grown organically over time, resulting in:
- Circular dependencies between modules
- Business logic mixed with infrastructure concerns
- Difficult to test components in isolation
- Hard to understand module boundaries
- Challenge in adding new features without breaking existing ones

We need a more structured approach to manage complexity as the project grows.

## Decision
We will adopt Clean Architecture principles for the V2 rewrite, with the following layers:

1. **Domain Layer**: Core business entities and logic with zero external dependencies
2. **Application Layer**: Use cases and business orchestration
3. **Infrastructure Layer**: External concerns (database, files, APIs)
4. **Presentation Layer**: User interfaces (CLI, Web, API)

Dependencies flow inward only: Presentation → Application → Domain ← Infrastructure

## Consequences

### Positive
- Clear separation of concerns and dependencies
- Easier to test business logic in isolation
- Can swap infrastructure without changing business logic
- Better understanding of system boundaries
- Supports gradual migration via Strangler Fig pattern

### Negative
- More boilerplate code initially
- Learning curve for team members
- Need to maintain two systems during migration
- Potential performance overhead from abstraction layers

### Neutral
- Requires discipline to maintain architectural boundaries
- Need tooling to enforce dependency rules
- Documentation becomes critical for onboarding

## Implementation
1. Create parallel `xwe_v2/` structure following clean architecture
2. Use mypy strict mode to enforce type safety
3. Implement feature flags for gradual rollout
4. Create import adapters for backward compatibility
5. Archive legacy code systematically

## References
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Implementing Clean Architecture](https://docs.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures#clean-architecture)
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
