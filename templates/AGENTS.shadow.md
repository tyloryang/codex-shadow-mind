## Shadow audit protocol

For tasks that create or materially modify code, use the two persistent audit
agents below as independent reviewers:

- After a coherent implementation milestone, delegate one bounded review to
  `code_auditor`. Ask it to inspect only the changed scope and report at most
  one high-confidence, actionable problem. Skip this for trivial edits or when
  no relevant custom agent is available.
- Before claiming the user's coding task is complete, delegate one bounded
  acceptance review to `goal_auditor`. Give it the user's current requirements,
  the changed scope, and verification evidence. Address any confirmed MUST-level
  gap before finishing.

The auditors are advisory and read-only. Do not let an audit replace normal
implementation or testing, and do not repeatedly re-run an auditor when no new
relevant evidence exists.
