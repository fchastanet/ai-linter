---
name: social-publishing-approval
description: Validate an approval-gated social publishing skill example.
license: MIT
allowed-tools:
  - file-system
  - network
metadata:
  author: AI Linter Example
  version: "1.0.0"
  tags: ["social", "approval", "validation"]
compatibility:
  frameworks: ["anthropic", "openai"]
  languages: ["markdown"]
---

# Social Publishing Approval

Use this skill when an agent drafts, reviews, or prepares social posts that need
explicit human approval before publication.

## Scope

This example models a skill that may use TweetClaw as a controlled publishing
surface. It keeps publishing separate from drafting so agents can validate copy,
metadata, and safety notes before any external action is taken.

## Approval Rules

- Draft posts without publishing them.
- Show the final text, account target, media list, and scheduled time.
- Ask for explicit approval before submitting a publish or schedule request.
- Stop if account ownership, authorization, or policy context is unclear.

## Validation Notes

This fixture gives AI Linter a realistic social automation skill to parse. It
contains valid frontmatter, local-only file references, and short guidance that
stays under the default token and line limits.

## Files

- [README.md](../../../README.md) - Main project documentation
- [Configuration](../../../.ai-linter-config.yaml) - Default validation settings
