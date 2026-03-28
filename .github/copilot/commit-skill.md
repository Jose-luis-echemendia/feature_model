# Commit Skill — Conventional Commits

Purpose:
Ensure that every important change in the repository produces a clean,
professional commit that follows the Conventional Commits specification.

When to create a commit:

- After completing a logical feature
- After fixing a bug
- After a refactor that improves code structure
- After documentation updates
- After configuration or CI/CD changes

Commit Format:

<type>(scope): <short description>

Rules:

1. Description must be concise and under 72 characters
2. Use imperative mood
3. Do not end with a period
4. Only one logical change per commit

Allowed types:

feat      → new feature
fix       → bug fix
docs      → documentation only changes
style     → formatting changes
refactor  → code change that neither fixes a bug nor adds a feature
test      → adding or modifying tests
chore     → maintenance tasks
perf      → performance improvements
ci        → CI/CD configuration
build     → build system changes

Examples:

feat(auth): add github oauth login
fix(api): prevent null pointer in user endpoint
refactor(core): simplify dependency injection
docs(readme): update installation guide

Additional Guidelines:

- Avoid committing temporary debug code
- Avoid large mixed commits
- Group logically related changes together
- Ensure the repository history remains readable and professional