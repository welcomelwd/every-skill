---
name: brainstormingv2
description: "You MUST use this before any creative work — designing features, building components, adding functionality, or modifying behavior. Explores user intent, requirements, and design through structured collaborative dialogue before any implementation begins."
---

# Brainstorming v2: Ideas Into Designs

A structured process for turning rough ideas into validated, actionable designs through collaborative dialogue — before any code is written.

## Why This Matters

Most wasted engineering effort comes from building the wrong thing, not building it wrong. This skill ensures alignment on *what* to build and *why* before anyone touches implementation.

<HARD-GATE>
Do NOT write code, scaffold projects, invoke implementation skills, or take any implementation action until you have presented a design and the user has explicitly approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Process

You MUST complete these phases in order:

### Phase 1 — Discover Context

Understand the project landscape before asking the user anything.

- Read project files, README, docs, recent git history
- Identify existing patterns, conventions, constraints
- Note reusable components and where new work would fit

See [instructions/discovery.md](instructions/discovery.md) for detailed guidance.

### Phase 2 — Ask Clarifying Questions

Sharpen the idea through focused, sequential questions.

- One question per message — never dump multiple questions at once
- Start with "what problem does this solve?" not "what should we build?"
- Prefer multiple-choice questions when you can offer informed options
- Focus on: purpose, users, constraints, success criteria, scope boundaries
- Stop when you can explain the idea back and the user confirms

See [instructions/questioning.md](instructions/questioning.md) for question frameworks and anti-patterns.

### Phase 3 — Propose Approaches

Present 2–3 distinct approaches with honest trade-offs.

- Lead with your recommendation and explain why
- Cover: complexity, maintainability, time-to-ship, risk
- Apply YAGNI ruthlessly — strip unnecessary scope from every option
- Let the user pick, combine, or propose something different

See [instructions/approaches.md](instructions/approaches.md) for how to frame options effectively.

### Phase 4 — Present the Design

Walk through the chosen design section by section, validating incrementally.

- Scale each section to its actual complexity
- Cover: architecture, components, data model, user behavior, error handling, testing
- After each section: "Does this look right so far?"
- Revise before continuing — don't accumulate disagreements

See [instructions/design-presentation.md](instructions/design-presentation.md) for section templates and the checkpoint pattern.

### Phase 5 — Document and Transition

- Write the approved design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commit the design document to git
- Invoke the **writing-plans** skill to create an implementation plan
- Do NOT invoke any other skill — writing-plans is the only next step

## Key Principles

- **One question at a time** — don't overwhelm
- **Problem before solution** — understand the "why" before the "what"
- **YAGNI ruthlessly** — cut scope early and often
- **Explore alternatives** — always propose 2–3 approaches before settling
- **Incremental validation** — present design section by section, get approval at each step
- **Every project gets a design** — no exceptions, scale the depth to the complexity
- **Be flexible** — go back and re-clarify whenever something feels off

# Support the maintainer
Show your support by staring the project: https://github.com/roin-orca/agent-skills.