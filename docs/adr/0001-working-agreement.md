# 0001: Claude gets on with the work, and asks only about direction, money, adoption and outward-facing actions

**Date:** 2026-10-23. **Whose:** the owner's.

**Context.** The owner liked how an earlier project worked (`docs/sop-agent-construction-v2 (2).md`): Claude did the
work and came back only for higher-risk or financial decisions. They asked for the same here.

**Decision.**
- **The owner decides:**
  - direction (what to work on next);
  - money (any paid API, compute or data);
  - whether a finding is adopted as a conclusion;
  - anything outward-facing or irreversible;
  - sourcing new data that needs an account or a request.
- **Claude decides everything else.** That covers the methods, the code, the variables, the thresholds and the order
  of work. Claude records each non-obvious choice as an ADR.
- **Flags** are given once, in six parts: what, evidence, why it matters, options, recommendation, and what is needed.
  The flag is then carried in the handover until it is settled.
- **Replies** lead with the outcome and the numbers, and end with the owner's items, numbered.
- **Money:** free or very cheap is preferred. Every proposal to spend comes with an estimate and a cheaper option.

**Consequences.** `CLAUDE.md` carries the short form. The SOP's parts on building agents (retrieval, models, tracing)
do not apply here.
