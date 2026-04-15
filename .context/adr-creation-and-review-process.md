# ADR Creation and Review Process

## Purpose

Architecture Decision Records (ADRs) capture significant design decisions made during the development of this system. They document not just what was decided, but why — including the context that drove the decision, the alternatives that were considered, and the consequences of the choice. ADRs serve as the authoritative historical record of architectural intent and enable future contributors to understand why the system is built the way it is.

An ADR is warranted when a decision:
- Affects more than one component or service
- Has non-obvious trade-offs
- Would be difficult or costly to reverse
- Reflects a constraint, policy, or organizational requirement
- Could be misunderstood or re-litigated without written context

---

## Storage and Naming Conventions

**Location:** `.context/decisions/`

**File naming:** `ADR-XXXXX-{kebab-case-topic}.md`
- The number is zero-padded to 5 digits: `ADR-00001`, `ADR-00002`, etc.
- Numbers are assigned sequentially. Never reuse a number, even if an ADR is deprecated.
- The topic slug describes the subject concisely in kebab-case (e.g., `per-user-token-storage`, `envelope-encryption`)

**Examples:**
- `ADR-00001-per-user-token-storage-firestore-vs-secret-manager.md`
- `ADR-00007-token-cache-eviction-strategy.md`

---

## ADR Template

Every ADR must use the following structure exactly. Do not add or remove sections. Do not rename sections.

```markdown
# ADR-XXXXX: {Topic Title}

## Status
{One of: Proposed | Under Review | Accepted | Deprecated | Superseded by ADR-XXXXX}

## Context
[Full description of the problem or scenario requiring a decision. Include:
- The technical or business need driving the decision
- Relevant constraints (cost, quota, security, operational complexity)
- All options that were considered
Do NOT state the decision here.]

## ADR Review Discussion
[Full thread of the review process: questions raised, concerns, counter-arguments, and how they were resolved. This section is present only while the ADR is in Proposed or Under Review status. It MUST be removed once the ADR reaches Accepted status and the Decision section is finalized.]

## Decision
[Specific description of what was decided and why, grounded in the ADR Review Discussion. Written in the past tense. This section is populated only when status moves to Accepted.]

## Consequences
[The impact of this decision on:
- Development workflow (what becomes easier, what becomes harder)
- Operational complexity (new infrastructure, monitoring requirements)
- Supportability (how future engineers will maintain or change this)
- Any known risks or limitations introduced by this choice]

## Alternatives Considered
[Each rejected option, with a brief explanation of why it was not chosen. Be specific — "too complex" is not sufficient; name the specific cost or risk that disqualified it.]
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `Proposed` | ADR has been drafted and is open for discussion. No decision has been made yet. |
| `Under Review` | ADR is actively being reviewed by stakeholders. Discussion is ongoing in the ADR Review Discussion section. |
| `Accepted` | Decision has been finalized. ADR Review Discussion section has been removed. Decision section is populated. |
| `Deprecated` | The decision is no longer applicable (e.g., the component was removed). The ADR is retained for historical reference. |
| `Superseded by ADR-XXXXX` | A newer ADR has replaced this decision. Link to the superseding ADR. The original ADR is retained for historical reference. |

---

## Creation Process

Follow these steps to create a new ADR:

1. **Identify the decision.** Confirm the decision is significant enough to warrant an ADR (see Purpose above).

2. **Assign the next sequential number.** Check `.context/decisions/` for the highest existing number and increment by one.

3. **Create the file** at `.context/decisions/ADR-XXXXX-{kebab-case-topic}.md`.

4. **Populate the template:**
   - Set **Status** to `Proposed`
   - Write a thorough **Context** section — include the full scenario, all constraints, and all options being considered
   - Leave **ADR Review Discussion** empty (or write `[Discussion pending]`)
   - Leave **Decision** empty (or write `[Pending review]`)
   - Write **Consequences** and **Alternatives Considered** based on your current understanding — these will be refined during review

5. **Notify reviewers.** Share the ADR with relevant stakeholders for feedback.

6. **Update Status** to `Under Review` once review has begun.

---

## Review Process

The ADR Review Discussion section is a living thread. Update it throughout the review:

- **Format:** Each entry is a timestamped, attributed comment:
  ```
  **[YYYY-MM-DD] [Author Name/Role]:** Comment text.
  ```
- **What to capture:** Questions raised, concerns about trade-offs, alternative suggestions, responses to concerns, and any new information that changes the analysis.
- **Who participates:** Any engineer or stakeholder with relevant expertise or accountability for the affected components.
- **How to reach consensus:** The decision owner (typically the author) is responsible for synthesizing discussion into a final decision. Consensus is preferred; if contested, the decision owner or tech lead makes the final call and documents the reasoning.

---

## Finalization Process

Once a decision has been reached:

1. **Populate the Decision section** with a clear, specific description of what was decided and why, drawing directly from the ADR Review Discussion.

2. **Remove the ADR Review Discussion section entirely.** The decision captures the conclusion; the discussion thread is not needed in the final record.

3. **Update Status** to `Accepted`.

4. **Refine Consequences and Alternatives Considered** if the review surfaced new information.

5. **Commit the finalized ADR** to version control with a commit message like:
   ```
   Accept ADR-XXXXX: {topic}
   ```

---

## Superseding and Deprecating ADRs

**To supersede an ADR:**
1. Create a new ADR with a new number covering the revised decision.
2. Update the old ADR's Status to `Superseded by ADR-XXXXX` (using the new number).
3. In the new ADR's Context section, reference the superseded ADR and explain what changed.

**To deprecate an ADR:**
1. Update the ADR's Status to `Deprecated`.
2. Add a note in the Context section explaining why the decision no longer applies (e.g., "Component X was removed in Q3 2025").

Never delete ADR files. They are permanent historical records.
