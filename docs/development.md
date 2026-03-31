---
title: Development 
summary: How to develop Click Docs. 
date: 2026-03-29T12:43:32.559666+00:00
---

# Installing from source for development

`uv` is recommended. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/).


Clone the repo:

```shell
$ git clone https://github.com/callowayproject/click-docs
```

Setup the environment.

```shell
$ cd click-docs
$ uv sync --upgrade --all-groups
```

Run Click Docs's tests from the source tree on your machine:

```shell
$ uv run pytest
```

## Development Flow

This project uses the [GitHubFlow](https://docs.github.com/en/get-started/quickstart/github-flow) workflow.

Rationale:

* The primary branch is always releasable.
* Lightweight.
* Single long-lived branch. Less maintenance overhead, faster iterations.
* Simple for one person projects, as well as collaboration.

Put simply:

1. Anything in the primary branch is deployable
2. To work on something new, create a descriptively named branch off the primary branch (ie: new-oauth2-scopes)
3. Commit to that branch locally and regularly push your work to the same named branch on GitHub
4. When you need feedback or help, or you think the branch is ready for merging, open a pull request
5. After someone else has reviewed and signed off on the feature, you can merge it into the primary branch
6. Once it is merged and pushed to the primary branch, you can and should deploy immediately

**Merging**

Merges are done via Pull Requests. 


**Tags**

Tags are used to denote releases.
