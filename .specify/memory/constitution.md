<!--
SYNC IMPACT REPORT:
Version: 0.0.0 → 1.0.0
Modified Principles: Initial creation - all principles established from README.md
Added Sections: All sections (Core Principles, Technology Stack, Development Methodology, Governance)
Removed Sections: None
Templates Status:
  ✅ plan-template.md: Constitution Check section aligns with 8 core principles
  ✅ spec-template.md: User Scenarios & Testing aligns with TDD/SDD methodology
  ✅ tasks-template.md: Test-first workflow aligns with TDD principle
Follow-up TODOs: None - all placeholders filled
-->

# NotebookUM Constitution

## Core Principles

### I. KISS (Keep It Simple, Stupid)
Simplicity is paramount in all design and implementation decisions. Solutions MUST be as simple as possible but no simpler. Complex solutions require explicit justification and simpler alternatives must be documented as rejected.

**Rationale**: Complexity increases maintenance burden, introduces bugs, and reduces team velocity. Simple code is easier to test, debug, and extend.

### II. DRY (Don't Repeat Yourself)
Every piece of knowledge MUST have a single, unambiguous, authoritative representation within the system. Code duplication is prohibited except when abstraction would introduce inappropriate coupling.

**Rationale**: Duplication leads to inconsistency, increases maintenance cost, and creates opportunities for bugs when logic needs to change.

### III. YAGNI (You Aren't Gonna Need It)
Features and abstractions MUST NOT be implemented until they are actually needed. Speculative generality is prohibited. Build for current requirements, not hypothetical future needs.

**Rationale**: Premature optimization and over-engineering waste resources and add complexity that may never be used.

### IV. SOLID Principles
All object-oriented code MUST adhere to SOLID principles:
- **Single Responsibility**: Each class/module has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Clients should not depend on interfaces they don't use
- **Dependency Inversion**: Depend on abstractions, not concretions

**Rationale**: SOLID principles create maintainable, flexible, and testable code architectures that scale with complexity.

### V. Test-Driven Development (NON-NEGOTIABLE)
TDD is mandatory for all production code. The red-green-refactor cycle MUST be followed:
1. Write failing test first
2. Write minimal code to make test pass
3. Refactor while keeping tests green

No production code may be written without a failing test that requires it.

**Rationale**: TDD ensures testability, drives better design, provides living documentation, and creates a safety net for refactoring.

### VI. Specification-Driven Development
All features MUST begin with a written specification before implementation. Specifications define user scenarios, acceptance criteria, and success metrics. Implementation cannot begin until specification is approved.

**Rationale**: Clear specifications prevent misunderstandings, enable better estimation, and provide measurable success criteria.

### VII. PEP 8 Compliance (Python Code Style)
All Python code MUST conform to PEP 8 style guidelines. Code formatting and style checks MUST pass before code review. Use automated tools (black, flake8, pylint) to enforce compliance.

**Rationale**: Consistent code style improves readability, reduces cognitive load, and facilitates collaboration across the team.

### VIII. 12-Factor App Methodology (First Six Factors)
The application MUST adhere to the first six factors of the 12-Factor App methodology:
- **I. Codebase**: One codebase tracked in version control, many deploys
- **II. Dependencies**: Explicitly declare and isolate dependencies (using uv)
- **III. Config**: Store config in environment variables
- **IV. Backing Services**: Treat backing services as attached resources (MySQL)
- **V. Build, Release, Run**: Strictly separate build and run stages
- **VI. Processes**: Execute the app as one or more stateless processes

**Rationale**: 12-Factor principles create portable, scalable applications suitable for modern deployment platforms.

## Technology Stack

### Required Technologies
- **Language**: Python (PEP 8 compliant)
- **Framework**: Flask for web API
- **Dependency Management**: uv for package and environment management
- **Database**: MySQL for persistent storage
- **Document Processing**: Docling library for text extraction from files
- **AI Model**: Nemotron-3 nano 30B for text summarization

### Technology Constraints
- All Python code MUST follow PEP 8 style guidelines
- Dependencies MUST be managed through uv (not pip alone)
- Database interactions MUST use parameterized queries to prevent SQL injection
- API endpoints MUST follow RESTful conventions
- Environment-specific configuration MUST use environment variables (12-Factor Config)

## Development Methodology

### Project Management
- **Methodology**: SCRUM framework for iterative development
- Sprints, daily standups, sprint planning, and retrospectives MUST be followed
- User stories MUST be prioritized and independently testable
- Work-in-progress MUST be visible and tracked

### Development Workflow
1. **Specification**: Create spec.md with user scenarios and acceptance criteria
2. **Planning**: Generate implementation plan with technical design
3. **Test Design**: Write failing tests (TDD red phase)
4. **Implementation**: Write minimal code to pass tests (green phase)
5. **Refactoring**: Improve code while maintaining test coverage (refactor phase)
6. **Review**: Code review verifies compliance with constitution
7. **Integration**: Merge only after tests pass and review approves

### Quality Gates
- All tests MUST pass before merge
- Code coverage MUST be maintained or improved
- PEP 8 compliance MUST be verified
- Constitution compliance MUST be checked
- No commented-out code in production branches
- No hardcoded credentials or configuration

## Governance

This constitution supersedes all other development practices and preferences. All code reviews, design decisions, and implementations MUST verify compliance with these principles.

### Amendment Process
- Amendments require documentation of rationale and affected systems
- Version number MUST be incremented according to semantic versioning
- Breaking changes require MAJOR version bump
- New principles require MINOR version bump
- Clarifications require PATCH version bump
- All team members MUST be notified of amendments

### Compliance
- All PRs MUST include constitution compliance verification
- Violations MUST be justified in writing with rejected simpler alternatives
- Repeated violations require architectural review
- Constitution review required quarterly or when principles conflict

### Version Control
- This constitution is version controlled alongside code
- Changes follow standard PR process with enhanced review requirements
- Historical versions preserved for reference

**Version**: 1.0.0 | **Ratified**: 2026-03-31 | **Last Amended**: 2026-03-31
