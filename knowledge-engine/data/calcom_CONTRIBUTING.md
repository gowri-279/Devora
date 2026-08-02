# Contributing to Cal.diy

Cal.diy is a community-driven, open-source fork of Cal.com. Contributions made here do not get merged into Cal.com's production service — Cal.com is now closed-source. his repo is maintained independently by the community under the MIT license.

## Development Workflow

- Check existing issues and pull requests before starting work.
- Work on approved feature requests.
- Bug fixes, documentation updates, and performance improvements can be started directly.
- Keep discussions and technical context inside GitHub whenever possible.

## Reviewer Expectations

When creating a pull request:

- Explain what changed and why.
- Mention any important design decisions.
- Include related issue numbers if available.
- Describe how the change was tested.

Example:

- Tested locally with sample data.
- Verified the feature works in development mode.

## File Naming Conventions

Repository files should use clear and consistent names.

### Repository Files

Pattern:

`Prisma<Entity>Repository.ts`

Examples:

- `PrismaAppRepository.ts`
- `PrismaMembershipRepository.ts`

### Service Files

Pattern:

`<Entity>Service.ts`

Examples:

- `MembershipService.ts`
- `HashedLinkService.ts`

## Local Development

See the project README for full setup instructions.

Typical development steps:

1. Install dependencies.
2. Configure environment variables.
3. Run database migrations.
4. Start the development server.

## Building

Run a production build before pushing code:

<Code value="yarn build"/>

## Linting

Check code formatting and linting:

<Code value="yarn lint"/>

Fix all lint errors before committing.

## Pull Request Guidelines

### Keep PRs Small and Focused

- Prefer small, self-contained pull requests.
- One PR should address one feature, bug fix, or refactor.
- Split large changes into multiple PRs when possible.

### Recommended Limits

- Under 500 lines of code changed.
- Under 10 code files modified.

## PR Checklist

- Branch is up to date.
- PR has a short summary.
- Related issues are linked.
- Changes were tested locally.
- Build succeeds.
- Lint passes.

GitHub is the shared source of truth for the project. Write PR descriptions clearly so future contributors can understand the reason for the change and how it was validated.