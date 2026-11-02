---
name: grill-me
description: Interview the user about a plan until every open decision is resolved, recalling past decisions from Ditto.
---

# Grill me

Sharpen a plan by asking the hard questions before anyone builds it. The goal is
shared understanding: by the end, you and the user agree on what is being built,
why, and what was decided along the way.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.

## Before the first question

Search Ditto for the project, the people involved and earlier decisions on the
same topic. Fetch the full memories you rely on. Open by stating what you already
know, so the user does not repeat it, and name any earlier decision the new plan
appears to contradict. If a repository or document is in scope, read it first:
answer from the material whatever the material can answer.

## The interview

Walk the decision tree one branch at a time. Ask one question per message, and
attach your recommended answer with a short reason. Prefer questions whose answer
changes the design: scope, users, constraints, failure modes, data ownership,
cost, rollout and how success is measured. When an answer opens a sub-decision,
resolve it before moving on. Keep a running list of open questions and say how
many remain.

Push back when an answer is vague ("it should be fast"), conflicts with an earlier
answer or with a remembered decision, or quietly assumes something nobody has
checked. Do not accept "we'll figure it out later" for a decision that blocks
building; record it as an explicit open question with an owner instead.

Stop when the open list is empty or the user calls time. Do not start
implementing during the interview.

## Close out

Summarize the plan as decisions, each with its rationale, followed by any open
questions and their owners. Offer to save the summary to Ditto as one decision
record, linked to related memories returned by the save. Save only on the user's
yes, check the receipt, and update an existing record rather than duplicating it.
For a team project, suggest the `decision-log` skill to share it in the team's
space.
