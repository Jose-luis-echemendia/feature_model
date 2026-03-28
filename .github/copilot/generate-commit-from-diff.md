# Generate Commit From Diff

Goal:
Automatically generate a high-quality Conventional Commit message
by analyzing the git diff.

Instructions:

1. Inspect the git diff.
2. Determine the nature of the change:

Feature → feat
Bug fix → fix
Refactor → refactor
Documentation → docs
Tests → test
Maintenance → chore

3. Identify the scope:

Examples:
auth
api
database
ui
core
config
docker
ci

4. Produce a commit message in the format:

<type>(scope): <short description>

5. Optionally include a body if the change is complex.

Example:

feat(auth): implement JWT refresh token system

Body example:

Add refresh token rotation and secure cookie storage
to improve session security and reduce token misuse.

Rules:

- Maximum 72 characters for the title
- Use imperative mood
- Do not include unnecessary words
- Ensure the message clearly explains the change