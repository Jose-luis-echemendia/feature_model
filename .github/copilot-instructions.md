# Copilot Repository Instructions

This repository follows strict engineering practices to maintain a clean Git history
and professional collaboration workflow.

General rules:

1. Follow Conventional Commits for all commits
2. Ensure commits represent a single logical change
3. Avoid committing debugging statements or temporary code
4. Prefer small atomic commits rather than large ones

Code guidelines:

- Write readable, maintainable code
- Follow language idioms and best practices
- Avoid unnecessary complexity
- Prefer explicitness over magic behavior

Commit behavior:

When a significant change is made, analyze the diff and determine:

1. What type of change occurred
2. The logical scope of the change
3. The most appropriate Conventional Commit type

Then generate a commit message in the format:

<type>(scope): <description>

Examples:

feat(users): add email verification flow
fix(auth): handle expired JWT token
refactor(database): isolate connection logic