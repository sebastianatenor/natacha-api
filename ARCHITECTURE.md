# Natacha Architecture — Cognitive Authority Model (B12)

## Core Principle (Canonical Rule)

**The TIMELINE is the single source of cognitive truth.**

Runtime state (processes, env vars, loaders) is observational and non-authoritative.

---

## Cognitive Authority Hierarchy

1. **Capability Manifest**
   - Declares which capabilities are considered implemented and sealed.
   - Versioned (B9, B11, B12…).

2. **Timeline (Historical Memory)**
   - Records achieved cognitive states.
   - If the timeline says a capability is loaded, it is considered loaded.
   - Immutable history, append-only.

3. **Runtime / Perception**
   - Reflects current execution state.
   - May be degraded, restarting, or disabled without invalidating cognition.

---

## Semantic Engine Policy

- Semantic engine loading at runtime is **instrumental**.
- Cognitive state is determined by:
  - Timeline events
  - Checkpoints
  - Snapshots

Runtime loaders must NEVER downgrade cognitive state.

---

## Self-Repair Policy

Self-repair is strictly infrastructural.

It may:
- Detect drift between timeline and runtime
- Propose repair actions
- Execute repairs only if armed and allowed

It must NEVER:
- Modify cognitive truth
- Invalidate achieved capabilities

---

## Full Status Endpoint

`/ops/system/full_status` reports:

- Canonical cognitive state (from timeline)
- Runtime execution state (observational)
- Explicit source attribution

Example:

```json
"semantic": {
  "loaded": true,
  "mode": "canonical",
  "source": "timeline"
}
