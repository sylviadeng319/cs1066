---
name: summarize-changes
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Instructions

Run `git diff HEAD && git status --short` to see the uncommitted changes in the current repository. Then, summarize the changes in two or three bullet points and list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
