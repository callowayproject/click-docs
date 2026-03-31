# Changelog

## 0.2.0 (2026-03-31)

[Compare the full difference.](https://github.com/callowayproject/click-docs/compare/0.1.0...0.2.0)

### New

- Add test fixture to prevent tests from using real pyproject.toml config. [08bd180](https://github.com/callowayproject/click-docs/commit/08bd180b2599cbbd3c2ab60521bb44a4e2e96e90)

- Add GitHub Actions workflow for deploying documentation and initial setup for project documentation site. [46b8fa0](https://github.com/callowayproject/click-docs/commit/46b8fa09ef2dbb3451cad71a9dfe489c5bd63915)

  - Add `docs.yml` workflow for deploying docs to GitHub Pages.
  - Introduce Zensical configuration (`zensical.toml`) for site customization and structure.
  - Add CLI reference documentation and API reference files for core modules.
  - Include custom CSS files for enhanced documentation styling.
  - Update `README.md` with installation, usage, and contribution guidelines.
  - Add a placeholder image directory and empty `.gitkeep` file.

- Add test fixtures for verifying relative import support in command loader. [3a88d77](https://github.com/callowayproject/click-docs/commit/3a88d7778aa334a7bc1b93cef78e07b00b016461)

- Add support for loading modules with relative imports in `load_command`. [6a1f555](https://github.com/callowayproject/click-docs/commit/6a1f555bf0a34432ba4697dcdbe44b2fcbe777cd)

- Add support for configuration via pyproject.toml, enabling auto-applied CLI defaults for header depth, style, exclusion, and more. [7df0d9e](https://github.com/callowayproject/click-docs/commit/7df0d9ef53aa8452499d80e1a3eb6abaa8309057)

- Add support for nested command documentation with configurable depth, exclusion, hidden commands/options, TOC generation, and ASCII art removal. [7b85735](https://github.com/callowayproject/click-docs/commit/7b857356994bcfef6278b261c98276a49c8042b0)

- Add support for customizable Markdown output: header depth, option styles (plain/table), and program name override. [f8eefba](https://github.com/callowayproject/click-docs/commit/f8eefba0672dd2a4f9853db6de6e4e9b8f497ebe)

- Add CLI tool for generating Markdown documentation for Click apps. [54270cb](https://github.com/callowayproject/click-docs/commit/54270cb9902ebac0cd8b5231c262dc2fb41268f3)

### Other

- Normalize end-of-file newlines across repository files. [d51148b](https://github.com/callowayproject/click-docs/commit/d51148b0cefc0574e8b69b6b71ad49c9dcbca3f5)

- Simplify `uv.lock` by consolidating Python version resolution markers and removing unused package entries. [445d352](https://github.com/callowayproject/click-docs/commit/445d3521b06a467f487f9809084273eee81024ad)

- Bump the github-actions group with 9 updates. [c11c953](https://github.com/callowayproject/click-docs/commit/c11c953b4b0cc454eecc3205a8f1d24ad27c728c)

  Bumps the github-actions group with 9 updates:

  | Package | From | To |
  | --- | --- | --- |
  | [actions/checkout](https://github.com/actions/checkout) | `4` | `6` |
  | [actions/download-artifact](https://github.com/actions/download-artifact) | `4` | `8` |
  | [actions/setup-python](https://github.com/actions/setup-python) | `5` | `6` |
  | [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) | `5` | `7` |
  | [github/codeql-action](https://github.com/github/codeql-action) | `3` | `4` |
  | [docker/login-action](https://github.com/docker/login-action) | `3` | `4` |
  | [docker/metadata-action](https://github.com/docker/metadata-action) | `5` | `6` |
  | [docker/build-push-action](https://github.com/docker/build-push-action) | `6` | `7` |
  | [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance) | `2` | `4` |

  Updates `actions/checkout` from 4 to 6

  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v4...v6)

  Updates `actions/download-artifact` from 4 to 8

  - [Release notes](https://github.com/actions/download-artifact/releases)
  - [Commits](https://github.com/actions/download-artifact/compare/v4...v8)

  Updates `actions/setup-python` from 5 to 6

  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v5...v6)

  Updates `astral-sh/setup-uv` from 5 to 7

  - [Release notes](https://github.com/astral-sh/setup-uv/releases)
  - [Commits](https://github.com/astral-sh/setup-uv/compare/v5...v7)

  Updates `github/codeql-action` from 3 to 4

  - [Release notes](https://github.com/github/codeql-action/releases)
  - [Changelog](https://github.com/github/codeql-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/github/codeql-action/compare/v3...v4)

  Updates `docker/login-action` from 3 to 4

  - [Release notes](https://github.com/docker/login-action/releases)
  - [Commits](https://github.com/docker/login-action/compare/v3...v4)

  Updates `docker/metadata-action` from 5 to 6

  - [Release notes](https://github.com/docker/metadata-action/releases)
  - [Commits](https://github.com/docker/metadata-action/compare/v5...v6)

  Updates `docker/build-push-action` from 6 to 7

  - [Release notes](https://github.com/docker/build-push-action/releases)
  - [Commits](https://github.com/docker/build-push-action/compare/v6...v7)

  Updates `actions/attest-build-provenance` from 2 to 4

  - [Release notes](https://github.com/actions/attest-build-provenance/releases)
  - [Changelog](https://github.com/actions/attest-build-provenance/blob/main/RELEASE.md)
  - [Commits](https://github.com/actions/attest-build-provenance/compare/v2...v4)

  ______________________________________________________________________

  **updated-dependencies:** - dependency-name: actions/checkout
  dependency-version: '6'
  dependency-type: direct:production
  update-type: version-update:semver-major
  dependency-group: github-actions

  **signed-off-by:** dependabot[bot] <support@github.com>

### Updates

- Update GitHub Actions workflows: consolidate, improve Python compatibility, and adopt Zensical for docs building. [b0c9f57](https://github.com/callowayproject/click-docs/commit/b0c9f57d4d0d529828418f61fd6776134d0d11f4)

- Update Python version compatibility and switch license to Apache 2.0. [35ba94e](https://github.com/callowayproject/click-docs/commit/35ba94e3a9477fde338d14ebce9842e70164fd54)

- Refactor CLI tool for improved readability, error handling, and modularity. [281d552](https://github.com/callowayproject/click-docs/commit/281d552acfc3cd7f60add79e32918c100c085f80)

## 0.1.0 (2026-03-29)

- Initial creation
