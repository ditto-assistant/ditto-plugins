---
name: write-spec
description: Turn a conversation or rough idea into a one-page spec and shippable tickets, grounded in Ditto memory.
---

# Write a spec and tickets

Turn what was discussed into something a person or agent can build without the
conversation: a short spec, then tickets that each deliver one testable outcome.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.

## Gather

Search Ditto for the project's goals, users, constraints, earlier decisions and
related specs. Read the current conversation and any linked documents or code.
If key facts are missing (who it is for, what done looks like, hard
constraints), ask for them, up to three questions at a time. Use the `grill-me`
skill when the plan itself is still unsettled.

## The spec

Keep it to one page where possible:

- **Problem:** who has it and how we know.
- **Outcome:** what is true for the user when this ships.
- **Scope:** what is included, and what is explicitly excluded.
- **Design:** the approach and the main alternatives considered, with the reason
  for the choice.
- **Risks and open questions:** each with an owner.
- **Acceptance:** observable checks that prove the outcome.

Mark assumptions as assumptions. Do not invent requirements to fill a heading.

## The tickets

Split the work into tickets that each ship and can be verified on their own.
Each ticket has a title stating the outcome, context linking to the spec,
acceptance criteria and its dependencies. Order them so the riskiest unknown is
resolved first. Prefer vertical slices (a thin path through every layer) over
layer-by-layer tickets.

## Deliver

Show the spec and tickets in the conversation. Create tickets in a tracker only
through a connected tool and only when the user asks. Offer to save the spec to
Ditto, in the project's or team's space when there is one, so later
conversations build from it.
