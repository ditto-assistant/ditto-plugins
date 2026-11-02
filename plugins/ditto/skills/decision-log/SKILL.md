---
name: decision-log
description: Record decisions with rationale and owner in Ditto, shared with the team, and answer why they were made.
---

# Decision log

Teams forget why they decided things, then re-argue them. Record each decision
once, with enough context that someone who was not in the room can understand
it, and make it findable when the question comes back.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.

## Record a decision

Capture these fields from the conversation, asking only for what is missing:

- **Decision:** one sentence, stated as what we will do.
- **Context:** the problem and the constraints at the time.
- **Alternatives:** what else was considered and why it lost.
- **Owner and date:** who decided, and when it takes effect.
- **Revisit when:** the condition that would reopen it, if any.

Keep proposals and decisions distinct: if it is not decided yet, record it as an
open question with an owner, not as a decision.

Before saving, search Ditto for earlier decisions on the same topic. If this one
replaces an earlier decision, say so in the new record and update the old one to
point at it rather than leaving two live answers.

## Where it goes

A personal decision goes to the user's main memory. A team decision belongs in
the team's or company's Ditto space, so teammates' agents can recall it. Write to
a shared space only when the user asks for it and their access allows it; never
widen who can see a record without saying so first. Check the save receipt and
give the user the reference.

## Answer "why did we...?"

Search the decision records and related memories, fetch the full records, and
answer with the decision, its rationale and its date, citing the records. If the
records disagree, show both and their dates. If there is no record, say so
rather than reconstructing a rationale.
