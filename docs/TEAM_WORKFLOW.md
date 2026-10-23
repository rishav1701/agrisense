# Team Workflow — AgriSense

> How we work: task ownership, review, and explicit sequential handoffs for a three-member team.

This document defines the day-to-day engineering workflow for the AgriSense team — three students building a satellite-based crop monitoring system alongside their regular studies. The rules here aren't bureaucracy for the sake of it; they exist so we don't step on each other's code, lose work, or merge something broken at 2 AM before a review.

Read this once, bookmark it, and refer back when unsure.

---

## 1. Task ID Convention

**Team role mapping:** Member A — Peter Livins (weather, water-balance support, geospatial); Member B — Rishav Raj (satellite data, ML, scientific modelling); Member C — Ashwanth C (application, dashboard, integration).

Every piece of work gets a task ID so we can trace commits, PRs, and discussions back to a specific goal.

**Format:** `T-PX-NNN` where:
- `P` followed by a number = phase (e.g., `P2`)
- `XX` = module code
- `NNN` = three-digit sequence number within that module/phase

**Module Codes:**

| Code | Module | Typical Owner |
|------|--------|---------------|
| `DE` | Data Engineering (satellite and weather ingestion, assembly) | Member A / Member B by task register |
| `SC` | Scientific Models (classification, phenology, stress, water balance) | Member B / Member A for water balance |
| `AP` | Application (responsive dashboard, Python API, visualization) | Member C |
| `SH` | Shared (contracts, schemas, utilities used by multiple modules) | Any / All |
| `IN` | Integration (cross-module wiring, end-to-end tests) | Member C (coordinator) |

**Examples:**
- `T-P2-DE-001` — Phase 2, Data Engineering, task 1 (e.g., "Set up GEE Sentinel-2 ingestion")
- `T-P2-SC-003` — Phase 2, Scientific Models, task 3 (e.g., "Implement NDVI/EVI index calculator")
- `T-P3-IN-002` — Phase 3, Integration, task 2 (e.g., "Wire stress output to dashboard map layer")

Task IDs are assigned in [`docs/TASK_ASSIGNMENTS.md`](TASK_ASSIGNMENTS.md) and referenced everywhere: commits, PRs, status updates.

---

## 2. Branch Naming Convention

We use a simple prefix system so anyone can glance at a branch name and know what it's for.

| Prefix | Use | Example |
|--------|-----|---------|
| `feat/` | New feature or capability | `feat/T-P2-DE-001-gee-sentinel2-ingestion` |
| `fix/` | Bug fix | `fix/T-P2-SC-003-ndvi-nan-handling` |
| `docs/` | Documentation only | `docs/update-api-contracts-phase2` |
| `integration/` | Cross-module integration work | `integration/P3-data-to-dashboard` |

**Rules:**
- Always include the task ID in feature and fix branches.
- Keep descriptions short but meaningful (lowercase, hyphens, no spaces).
- `main` is the protected branch — nobody pushes directly to it.

---

## 3. Commit Guidelines

Good commits make debugging and code review much easier. A week from now, you'll thank yourself.

### Keep Commits Small and Focused
- One logical change per commit. "Add NDVI calculator" is good. "Add NDVI calculator, fix dashboard bug, update README" is three commits.

### Use Conventional Commit Messages

```
type(scope): short description

Longer explanation if needed.

Task: T-P2-DE-001
```

**Types:**

| Type | When to Use |
|------|-------------|
| `feat` | New feature or functionality |
| `fix` | Bug fix |
| `docs` | Documentation changes only |
| `test` | Adding or updating tests |
| `refactor` | Code restructuring without behavior change |
| `chore` | Build scripts, CI config, dependency updates |

**Examples:**
```
feat(data): add Sentinel-2 NDVI composite function

Computes 16-day NDVI composites from cloud-masked S2 imagery
using the median reducer in GEE.

Task: T-P2-DE-003
```

```
fix(models): handle NaN pixels in VCI calculation

VCI was returning NaN for pixels where NDVI_min == NDVI_max.
Added a guard to return 0.0 in that case.

Task: T-P2-SC-005
```

### What NOT to Commit
- **Large binary files** (GeoTIFFs, model pickles, satellite images). Use `.gitignore`.
- **Credentials or secrets** (GEE keys, API tokens, `.env` files). Ever.
- **Generated outputs** (compiled files, `__pycache__`, `.pyc`).
- **Notebook outputs** if using Jupyter — clear outputs before committing or use a pre-commit hook.

---

## 4. Pull Request and Review Rules

Every change to `main` goes through a Pull Request. No exceptions, no "quick fixes."

### PR Requirements
1. **Title** includes the task ID: `[T-P2-DE-001] Add GEE Sentinel-2 ingestion pipeline`
2. **Description** explains what changed and why
3. **At least one reviewer** must approve before merge
4. **Tests must pass**

### Who Reviews What

| Type of Change | Minimum Reviewers |
|---|---|
| Regular code changes | 1 other member |
| Scientific logic (models, thresholds, FAO-56) | At least 1 other member (ideally both) |
| Shared contract changes (`docs/API_CONTRACTS.md`, `src/contracts/`) | **All 3 members** |
| Documentation | 1 other member |

### PR Checklist

Every PR description should include this checklist (copy-paste it):

```markdown
## PR Checklist
- [ ] Task ID referenced in title and description
- [ ] Tests pass locally
- [ ] No credentials, secrets, or `.env` values committed
- [ ] Documentation updated if behavior changed
- [ ] Contract changes approved by all members (if applicable)
- [ ] Large files excluded (no GeoTIFFs, pickles, or raw data)
```

### Review Expectations
- Review within 24 hours when possible (we all have classes — just don't let PRs rot for a week).
- Be constructive. "This could break if X happens" is helpful. "This is wrong" without explanation is not.
- If you approve with minor comments, say so. Don't block on typos.

---

## 5. Task Ownership and File Restrictions

Each member owns the files listed for their task. Work follows sequential handoffs; owning a later task does not require tracking another member’s daily progress.

> [!IMPORTANT]
> This table uses a **provisional directory structure**. Actual paths will be finalized when the architecture is approved in Phase 1. The ownership principle stays the same regardless of exact paths.

| Directory / File | Primary Owner | Others May Edit? |
|---|---|---|
| `src/data/sentinel1.py`, `sentinel2.py`, `preprocessing.py` | Member B (Rishav) | No — PR required |
| `src/data/gee_auth.py`, `era5land.py`, `observation_assembly.py`, `cache.py` | Member A (Peter) | No — PR required |
| `src/data/` satellite task tests | Member B (Rishav) | No — PR required |
| `src/data/` weather/assembly tests | Member A (Peter) | No — PR required |
| `src/models/classifier.py`, `phenology.py`, `stress.py` | Member B (Rishav) | No — PR required |
| `src/models/water_balance.py` | Member A (Peter) | No — PR required; Member B reviews scientific assumptions |
| `frontend/`, `src/api/`, `src/dashboard/` | Member C (Ashwanth C) | No — PR required after DEC-01 finalizes paths and tools |
| `src/contracts/` | Member C (Ashwanth C; coordinator) | Only via approved PR by **all** members |
| `src/spatial/` | Member A (Peter) | No — PR required; Member C reviews at handoff |
| `src/evaluation/` | Member B (Rishav) | No — PR required |
| Satellite tests in `tests/data/` | Member B (Rishav) | No |
| Weather/assembly tests in `tests/data/` | Member A (Peter) | No |
| Classifier/phenology/stress tests | Member B (Rishav) | No |
| Water-balance tests | Member A (Peter) | No |
| `tests/dashboard/` | Member C (Ashwanth C) | No |
| `tests/contracts/` | Member C (Ashwanth C) | Shared schema tests require Member A (Peter) and Member B (Rishav) review |
| `tests/integration/` | Member C (Ashwanth C; coordinator) | Any member may add tests |
| `tests/spatial/` | Member A (Peter) | Member C (Ashwanth C) reviews at handoff |
| `tests/evaluation/` | Member B (Rishav) | Member C (Ashwanth C) reviews integration |
| `docs/` | Any member (for their area) | Shared docs need review |
| `scripts/` | Owner of the related module | PR required |
| `.env.example` | Member A | PR required |
| `README.md` | Any member | PR required |

**What "Primary Owner" means:**
- You're responsible for the quality and correctness of code in your area.
- Others should not directly edit your files — they open a PR and you review it.
- If you're stuck or unavailable, coordinate before someone else jumps in.

---

## 6. Shared Contract Approval Process

Contracts define handoff formats and interfaces. The team works in sequence; a shared contract change still requires unanimous approval before implementation.

### Process for Contract Changes

1. **Propose:** Any member creates a PR with the `contract-change` label and a clear explanation of what's changing and why.
2. **Review:** All three members must review the proposed change. No shortcuts.
3. **Approve:** All three members must explicitly approve the PR.
4. **Merge:** Only after all three approvals.
5. **Implement:** Members update their own code to match the new contract.

### Rules
- No implementation code may depend on a contract change that hasn't been approved and merged yet. (You can write code locally, but don't open a PR that assumes an unapproved contract.)
- Member C coordinates contract consistency but does **not** have unilateral approval power.
- **Emergency fixes:** If something is broken in production/demo and a contract fix is urgent, one member can merge the fix — but all members must review and approve post-hoc within 48 hours.

---

## 7. Testing Requirements

### What Needs Tests
- All non-trivial functions (if it has logic, it needs a test).
- Module boundary interfaces (does the output of the data pipeline actually match what the model expects?).
- Edge cases in scientific calculations (NaN handling, empty geometries, division by zero in indices).

### Types of Tests

| Test Type | Location | Purpose |
|---|---|---|
| Unit tests | `tests/data/`, `tests/models/`, `tests/app/` | Test individual functions in isolation |
| Integration tests | `tests/integration/` | Test that modules work together correctly |
| Scientific validation | Documented separately | Compare model outputs against ground truth or known values |

### Test Data Rules
- Use **synthetic or sample data** for automated tests. Never fabricate scientific results to make tests pass.
- If using real satellite data snippets, label them clearly as sample data with source and date.
- Keep test data small. Don't commit 500 MB GeoTIFFs to the repo.

### Before Merging
- All tests must pass. If a test is legitimately broken by your change, fix the test and explain why in the PR.
- Clearly distinguish between **software tests** (does the code work?) and **scientific validation** (are the results accurate?). Both matter, but they're tracked differently.

---

## 8. Integration Checkpoints

The project owner prefers non-overlapping stages and no day-to-day dependency monitoring. For each handoff, the outgoing owner provides the artifacts, provenance, schema/version, known gaps, and acceptance evidence listed in the task. The reviewer records accept/reject and any blocking defects. Only after acceptance does the next dependent owner begin. This task-level handoff does not itself close a phase gate.

Handoffs are the integration checkpoints. The next dependent stage starts only after the current owner’s deliverables and acceptance criteria are reviewed.

| When | What | Who |
|---|---|---|
| **Task handoff** | Record named artifacts and reviewer acceptance before the dependent stage begins | Task owner + independent reviewer |
| **End of phase** | Integration review: merge all module branches, run integration tests, verify outputs match contracts | All 3 members |
| **Phase 3** | Dedicated integration phase: full end-to-end testing, dashboard wiring, bug fixes | All 3 members |

### Handoff Record
Record the task ID, outgoing artifacts, contract version, provenance, known gaps, acceptance evidence, reviewer decision, and any unresolved blocker in the task PR or status checkpoint. This task handoff is separate from formal phase gates.

### End-of-Phase Integration Review
- All members pull `main`, run the full test suite, and try the end-to-end flow.
- File issues for anything broken. Fix before moving to the next phase.
- Update `docs/STATUS.md` with the integration outcome.

---

## 9. Conflict Resolution

Disagreements happen. Here's how we handle them without wasting time.

### Technical Disagreements
1. Discuss the options openly (in person, PR comments, or chat).
2. Each person states their case with reasoning.
3. Decide and **document the decision** in [`docs/DECISIONS.md`](DECISIONS.md) with the rationale.
4. Move on. Don't relitigate decided issues.

### If No Consensus
- Escalate to our guide, **Dr. Muthuraja S**, for a tiebreaker or guidance.
- Document the escalation and outcome in `docs/DECISIONS.md`.

### Merge Conflicts
- The **owner of the file** resolves merge conflicts in their area.
- For shared files (contracts, README, docs): coordinate on a call or in person. Don't just force-push.

### Contract Disputes
- These require all-member agreement by definition (Section 6). No majority-rules shortcuts.

---

## 10. Environment and Secret Management

> [!CAUTION]
> **Never commit `.env` files, API keys, GEE credentials, or any secrets to Git.** Not even "temporarily." Not even in a "test branch." Git history is forever.

### Setup
- `.env` — your local environment variables. Listed in `.gitignore`.
- `.env.example` — checked into Git. Contains every required variable with placeholder values and descriptions.

**Example `.env.example`:**
```bash
# Google Earth Engine
GEE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GEE_KEY_FILE_PATH=path/to/your/key.json

# Study Area (WKT or GeoJSON path)
STUDY_AREA_PATH=data/boundaries/study_area.geojson

# ERA5 / CDS API
CDS_API_KEY=your-cds-api-key-here
```

### GEE Authentication
- Each member uses their own Google account for GEE access.
- Follow the GEE Python API authentication guide to set up locally.
- Don't share service account keys over chat. Use secure channels if needed.

### Adding New Environment Variables
- Add the variable to `.env.example` with a description.
- Tell the team (in a PR comment or sync) so they can update their local `.env`.

---

## 11. Working with AI Coding Agents

AI tools (GitHub Copilot, Gemini, ChatGPT, etc.) can help write code faster. Here's how to use them responsibly on this project.

### Rules
1. **AI agents are tools, not team members.** They don't get review votes. They don't approve contracts. They don't make scientific decisions.
2. **AI agents must follow [`AGENTS.md`](../AGENTS.md).** If an AI agent is helping you, point it to the AGENTS.md file for project-specific rules and constraints.
3. **All AI-generated code requires human review.** You are responsible for anything you commit, regardless of who (or what) wrote it. Read it, understand it, test it.
4. **Scientific logic is human-only.** AI can help with boilerplate, data wrangling, and plumbing code. It should not decide thresholds, validate models, or choose scientific methods without your explicit judgment.
5. **Reference task IDs in agent sessions.** If you're using an AI agent for `T-P2-SC-003`, tell it the task ID and point it to the relevant docs. This keeps the work focused.

### What AI Agents Should Read
When starting a session with an AI coding agent, have it read:
- `AGENTS.md` (always, first)
- The specific task from `docs/TASK_ASSIGNMENTS.md`
- Relevant contracts from `docs/API_CONTRACTS.md`
- `docs/STATUS.md` for current project state

---

## 12. Recovery from Interrupted Sessions

Real life happens — you get pulled into an exam week, your laptop dies, or you just haven't touched the project in a few days. Here's how to get back up to speed quickly.

### The Source of Truth

[`docs/STATUS.md`](STATUS.md) is the single source of truth for what's done, what's in progress, and what's blocked. **Update it at meaningful checkpoints** (not every commit, but every significant milestone or blocker).

### Getting Back In (Human or AI Agent)

Follow this sequence:

```
1. Read AGENTS.md                          ← Project rules and constraints
2. Read docs/STATUS.md                     ← Where are we right now?
3. Read docs/TASK_ASSIGNMENTS.md           ← What's my specific task?
4. Read docs/API_CONTRACTS.md              ← What are the interfaces I need to respect?
5. Read docs/DECISIONS.md                  ← Were any relevant decisions made while I was away?
6. Check Git log for recent changes        ← What changed since I last worked?
7. Start working on the assigned task      ← Now you have full context
```

### Updating STATUS.md
When you finish a work session:
- Note what you completed.
- Note what's in progress and where you left off.
- Note any blockers or questions.
- Commit the STATUS.md update.

---

## 13. Communication Guidelines

We're three students at VIT, not a distributed enterprise team. Keep communication lightweight but reliable.

### Where to Discuss What

| Topic | Where |
|---|---|
| Code-specific feedback | GitHub PR comments |
| Bug reports or feature requests | GitHub Issues |
| Major technical decisions | `docs/DECISIONS.md` (documented) |
| Quick questions, scheduling | WhatsApp / in person |
| Blockers | Communicate immediately (don't wait for sync) |

### Status and Handoff Updates
- Update `docs/STATUS.md` at meaningful checkpoints and when blockers or formal gate decisions change.
- Follow the task register and explicit reviewer handoffs. Daily cross-member progress monitoring is not required.

### Academic Schedule
- We all have exams, labs, and assignments. That's expected.
- If you know you'll be unavailable (CATs, FATs, project deadlines for other courses), **communicate early**.
- Don't silently disappear — even a "hey, I'm swamped this week, will pick back up Monday" is fine.

---

## 14. Coordinating Shared Interfaces

Shared interfaces define the handoffs: Member B’s satellite package is assembled with Member A’s weather data, feeds Member B’s models, then Member A’s water-balance/geospatial outputs feed Member C’s dashboard.

### Where Interfaces Are Defined
- All shared interfaces live in [`docs/API_CONTRACTS.md`](API_CONTRACTS.md).
- Any changes follow the process in [Section 6](#6-shared-contract-approval-process).

### Sequential Handoff Strategy
Since each member starts a dependent stage after a reviewed handoff:

1. **Define the contract first.** Before writing implementation code, agree on the interface (what data goes in, what comes out, what format).
2. **Write interface tests early.** Test that your module's output conforms to the contract. Test that your module can consume the expected input.
3. Use synthetic data only in clearly labelled software tests. Downstream scientific modules wait for the accepted data handoff; synthetic fixtures are not a substitute for observed inputs or scientific validation.
4. **Validate at integration checkpoints.** When real data replaces mocks, run integration tests to catch mismatches.

### Member C's Coordinator Role
- Member C maintains `docs/API_CONTRACTS.md` and ensures consistency across contracts. Any shared-contract change requires documented approval from all three human team members before implementation.
- Member C does **not** have unilateral approval power — all contract changes require all-member agreement.
- Member C raises flags if contracts seem inconsistent or incomplete.

---

## Quick Reference Card

For day-to-day use, here's the essentials on one screen:

| Item | Rule |
|---|---|
| Task ID format | `T-PX-XX-NNN` (e.g., `T-P2-DE-001`) |
| Branch naming | `feat/T-P2-DE-001-short-description` |
| Commit message | `feat(data): add sentinel-2 compositor` + Task ID in body |
| PR to `main` | At least 1 reviewer; tests pass; checklist complete |
| Contract change | All 3 members must approve |
| Secrets | Never in Git. Use `.env` + `.env.example` |
| AI code | Must be human-reviewed before merge |
| Getting back in | Read: AGENTS.md → STATUS.md → TASK_ASSIGNMENTS.md → API_CONTRACTS.md |
| Blocked? | Say so immediately. Notify the relevant task reviewer and record blockers at the next meaningful checkpoint. |
