# AI Visual Commerce Platform — Foundation Architecture

**Prepared for:** 3–6 person engineering team
**Goal:** A stable base layer with plug-and-play feature modules, structured so each engineer can build independently with minimal merge conflicts and minimal coordination overhead.

---

## 0. The Mental Model

Treat this repository the way Unreal Engine treats a game project, or VS Code treats extensions: there is one small, boring, rarely-changing **engine** (`core/` + `shared/`), and everything interesting happens in **plugins** (`modules/`) that snap into it through a fixed set of contracts. Nobody touches the engine to ship a feature. Nobody reaches into another plugin's internals. If a plugin is deleted, the engine doesn't notice. If a plugin is rewritten from scratch, nothing else in the repo needs to change as long as the contract stays the same.

Everything below exists to enforce that one rule.

---

## 1. Folder Structure

```
ai-commerce-platform/
├── core/                    # The engine. Infrastructure only, no feature logic.
├── shared/                  # Shared building blocks. No state, no feature logic.
├── modules/                 # Every feature lives here, one folder per feature.
│   ├── vton/
│   ├── catalog/
│   └── _template/           # Copy this to start a new module.
├── frontend/                 # UI. Calls module APIs only, no AI logic.
├── storage/                  # Local dev storage (uploads, outputs, cache, models).
├── database/                  # Migrations, schema definitions, seed scripts.
├── docs/                       # Architecture docs, ADRs, onboarding.
├── .github/                     # CODEOWNERS, PR template, CI workflows.
├── docker-compose.yml
├── requirements-base.txt        # Versions shared by every module (fastapi, pydantic...).
└── README.md
```

Why each folder exists, and what does *not* belong in it:

**`core/`** is the API gateway, auth, request routing, and the storage/config/logging plumbing every module needs to boot. It owns no feature behavior. If you find yourself adding an `if module == "vton"` branch inside `core/`, that's the signal something belongs in `modules/` instead.

**`shared/`** is a toolbox, not a service. It holds schemas, interfaces, image utilities, prompt templates, and constants that multiple modules legitimately need so nobody copy-pastes a resize function six times. The rule that keeps this folder from rotting: shared/ never imports from modules/, and shared/ never holds business logic specific to one feature.

**`modules/`** is where 95% of the team's work happens, and it's the only folder most engineers will ever need to touch. Each subfolder is a self-contained feature with its own API, models, and dependencies.

**`frontend/`** consumes module APIs through the gateway and contains zero AI logic — no prompt construction, no model calls. That keeps frontend and backend release cycles decoupled.

**`storage/`** is for local/dev artifacts only (uploads, generated outputs, model weights cache). In production this maps to S3/GCS, but the folder gives every developer an identical local layout so paths in code never diverge between machines.

**`database/`** holds schema and migrations as the single source of truth for tables like `jobs`, `users`, `catalogs` — not scattered across modules, so a `users` table change isn't five separate PRs.

**`docs/`** is where this file lives, plus architecture decision records (ADRs) for anything that changes `core/` — see Section 8.

---

## 2. Plugin Architecture — Inside a Module

Every module, present or future, has the identical internal shape:

```
modules/<feature_name>/
├── api/
│   └── routes.py        # FastAPI router. The ONLY entry point into this module.
├── services/
│   └── service.py        # Business logic. Implements the shared module interface.
├── models/
│   └── ...                # Model weights loading, inference wrappers.
├── schemas/
│   └── schemas.py          # Pydantic request/response contracts for this module.
├── config/
│   └── config.py             # Module-specific settings (model paths, thresholds).
├── tests/
│   └── test_service.py        # Contract tests — see Section 8.
├── requirements.txt              # This module's own dependencies (e.g. torch, diffusers).
└── README.md                      # Filled from the template in Section 7.
```

**`api/`** is the module's front door. Nothing outside the module calls `services/` directly — everything goes through `api/routes.py`, which the gateway mounts. This is what makes a module "pluggable": delete the folder, and the only thing that breaks is one line in the gateway's router registry.

**`services/`** holds the actual pipeline logic (e.g., VTON's parsing → try-on → identity preservation → cinematic generation chain). This is where most of an engineer's time goes, and it's theirs alone.

**`models/`** isolates anything related to loading and running ML weights, so swapping CatVTON for IDM-VTON, or one diffusion checkpoint for another, never touches `services/` business logic — only this folder and a config value.

**`schemas/`** defines exactly what this module accepts and returns. This is the contract other humans (and the frontend) read first.

**`config/`** keeps module-specific tunables (batch size, model checkpoint path, default style) out of code and out of `core/`'s global config.

**`tests/`** include unit tests but, critically, also a **contract test**: a test that hits the module's API with the schema-defined shape and confirms it returns the schema-defined shape. This is what lets six people merge code into `develop` daily without ever running each other's heavy ML pipelines locally.

**Each module ships its own `requirements.txt`.** VTON's diffusion/torch stack shouldn't bloat Catalog's environment, and a dependency conflict in one module's libraries can never break another's. This also means any module can be lifted into its own container or service later — with zero code changes — once it actually needs to scale independently. That's the deliberate hedge against premature microservices: you get the *option* to split without paying the operational cost until you need it.

`modules/_template/` is a literal copy of this structure with stubbed files and TODO comments. Starting a new feature is "copy folder, rename, fill in three files" — never "figure out the architecture again."

---

## 3. The Base Layer

This is the layer that should change the least over the life of the company, and the layer where any change requires the most scrutiny (see Section 8).

**`core/` owns infrastructure:**
- API Gateway — single entry point; mounts each module's router from a small registry (Section 6 shows exactly what this looks like).
- Auth — token/session validation, shared across every module.
- Request routing & middleware — logging, rate limiting, error formatting.
- Config loading — environment variables, secrets, per-environment settings.
- Storage client — a single abstraction over "save this file / read this file," whether that's local disk today or S3 tomorrow.
- Logging — one structured logger every module imports, so log lines are searchable across the whole system instead of six different formats.

**`shared/` owns toolkit code with no opinions:**
- `schemas/` — base types every module's schema can extend or reference: `ImageReference`, `JobStatus`, `ErrorResponse`. This is what lets the frontend render a generic "job in progress" UI regardless of which module is running.
- `interfaces/` — the abstract contracts modules implement (Section 5).
- `image_utils/` — resize, format conversion, basic preprocessing used by VTON, Catalog, and eventually Saree/Textile alike.
- `prompt_templates/` — reusable prompt scaffolding for any module doing generative image work, versioned so a prompt tweak in one place doesn't require five PRs.
- `constants/` — enums and fixed values (supported image formats, job states).
- `model_loader/` — a generic "load this checkpoint, cache it, return a handle" utility; module-specific model code in `modules/*/models/` builds on top of this rather than reimplementing caching logic six times.

The one rule that makes this layer trustworthy: **`shared/` and `core/` never import anything from `modules/`.** Dependency direction is always modules → shared/core, never the reverse, and never modules → modules.

---

## 4. Team Workflow

**Branches**
- `main` — always deployable. Protected, no direct pushes.
- `develop` — integration branch where finished features land first.
- `feature/<module>-<short-description>` — e.g. `feature/vton-identity-preservation`. One branch per unit of work, scoped to one module's folder (or `shared/`/`core/` for infra work, which follows a stricter process below).

**Ownership via CODEOWNERS**
A `.github/CODEOWNERS` file maps folders to people automatically, so GitHub requests the right reviewer without anyone remembering to tag them:

```
/modules/vton/      @member1
/modules/catalog/   @member2
/modules/saree/      @member3
/shared/                @tech-lead
/core/                   @tech-lead
```

This single file is what guarantees "nobody needs to modify someone else's feature folder" — it's enforced by the platform, not by good intentions.

**Pull requests**
A PR that only touches files inside one module folder needs one reviewer: the module owner reviews for correctness, the tech lead skims for contract compliance (does it still match `schemas/`?). A PR that touches `shared/` or `core/` needs two approvals and a short written justification (what's changing and why it has to live in the shared layer rather than a module) — see the ADR process in Section 8. This asymmetry is intentional: feature work should be fast and low-friction; foundation changes should be slow and deliberate.

**Review checklist (also lives in the PR template):**
1. Does this PR touch only its own module folder (or shared/core with justification)?
2. Do the API request/response shapes match `schemas/`?
3. Do contract tests pass without needing another module's code running?
4. Is the README updated if inputs/outputs/dependencies changed?

**Merge flow**
Feature branch → squash-merge into `develop` once its own module's tests pass in CI. `develop` → `main` on a regular cadence (e.g., weekly, or whenever the team agrees on a release cut), after the full contract-test suite runs across all modules together. This means day-to-day work never blocks on someone else's module being finished — integration is a scheduled, predictable event, not something that happens by accident when two people's branches collide.

---

## 5. Interfaces — How Modules Communicate

There are three layers of contract, from outermost to innermost.

**(a) The HTTP contract.** This is the real boundary. The frontend, and any module that needs to orchestrate another module's output, talks over the API Gateway using the request/response shapes defined in that module's `schemas/`. Catalog never imports VTON's Python code — if Catalog ever needs a try-on image, it calls `POST /vton/generate` like anyone else would.

**(b) The in-process service contract.** Inside the monorepo, before anything is split into a separate deployable service, every module's `services/service.py` implements a shared abstract interface so a future orchestrator (e.g., a "Pipeline Engine" chaining VTON → Enhancement → Video) can call any module the same way without knowing its internals:

```python
# shared/interfaces/module_interface.py
from abc import ABC, abstractmethod
from shared.schemas.base_schemas import JobRequest, JobResponse

class BaseModuleService(ABC):
    @abstractmethod
    def process(self, request: JobRequest) -> JobResponse:
        """Run this module's pipeline and return a standard result shape."""

    @abstractmethod
    def health_check(self) -> bool:
        """Used by the gateway to confirm the module is ready before routing to it."""
```

Every module's `service.py` implements this. The gateway, or any orchestrator, only ever calls `.process()` — never a module-specific method name.

**(c) The schema contract.** Common concepts — an image reference, a job's status, an error — are defined once in `shared/schemas/` and reused, so every module "speaks the same language" for the things they have in common, while still defining their own specific request/response shapes (a `VTONRequest` has `person_image` + `garment_image` + `prompt`; a `CatalogRequest` has `garment_image` + `style`) that extend the shared base types.

This is the literal mechanism behind "Catalog should never depend on VTON internals": Catalog only ever sees `BaseModuleService`, `JobRequest`, `JobResponse`, and VTON's public HTTP contract — never a single line of VTON's pipeline code.

---

## 6. Future Growth — Adding a Module Without Touching Existing Code

Here's the exact sequence to add the Saree Engine (and identically, Textile, Video, Avatar, Enhancement, Recommendation, or Analytics):

1. Copy `modules/_template/` → `modules/saree/`.
2. Fill in `schemas/schemas.py` with `SareeRequest` / `SareeResponse` (extending the shared base types).
3. Implement `services/service.py` as a class implementing `BaseModuleService`.
4. Wire `api/routes.py` to call that service.
5. Add one line to the gateway's module registry in `core/api_gateway/`:
   ```python
   MODULE_REGISTRY = {
       "vton": "modules.vton.api.routes",
       "catalog": "modules.catalog.api.routes",
       "saree": "modules.saree.api.routes",   # ← the only line touching existing infra
   }
   ```
6. Add `/modules/saree/ @whoever-owns-it` to `CODEOWNERS`.
7. Open a PR. It only ever touches files inside `modules/saree/` plus that one registry line — nothing in `vton/`, `catalog/`, or anyone else's code is read, let alone modified.

Two of the future modules deserve a note: **Recommendation Engine** and **Analytics Engine** are not image-generation pipelines — they're data/ML pipelines closer to "query and rank" or "aggregate and report." They'll still follow the same folder shape and the same `BaseModuleService` contract, but when the time comes it's worth defining a second, leaner interface variant for non-generative modules rather than forcing every concept (e.g., "garment image input") onto them. That's a five-minute addition to `shared/interfaces/`, not a redesign.

---

## 7. Starter README Template

Drop this into every module's `README.md` and fill in the blanks — this is also the first thing a reviewer checks a PR against.

```markdown
# Module: <Module Name>

## Purpose
One paragraph: what this module does and why it exists.

## Owner
<Name / handle>

## Inputs
- field_name (type): description
- field_name (type): description

## Outputs
- field_name (type): description

## Dependencies
- shared/: which shared utilities or schemas this module uses
- External services/models: e.g. specific checkpoints, third-party APIs

## API
POST /<module>/generate
Request: <link to schemas/schemas.py>
Response: <link to schemas/schemas.py>

## Future Improvements
- Known limitations or planned upgrades
```

---

## 8. Development Philosophy

**How startups end up with spaghetti code.** It's rarely one bad decision — it's a dozen small, reasonable-feeling ones under deadline pressure: "I'll just import that one function from the other module instead of duplicating it," "I'll just add a special case to the gateway for my feature," "I'll just put this constant in `core/` since it's quicker." Each one is individually harmless. Six months and six engineers later, every module imports two others, nobody can delete or rewrite anything without breaking three unrelated features, and onboarding a new hire takes a week of reading code instead of reading a README.

**How to prevent it, concretely:**

*Contracts over convenience.* If reusing another module's code feels easier than going through its API, that's a sign the shared logic belongs in `shared/`, not a sign the rule should bend. Move it up, don't reach across.

*Folder = ownership = blast radius.* CODEOWNERS isn't bureaucracy, it's what lets six people work without a daily sync meeting. If you can't predict, from the file path alone, who needs to review your change, the structure has failed.

*Every module should be replaceable, not just addable.* The real test of this architecture isn't "can we add Saree Engine" — it's "can we rip out the current VTON model and drop in a better one in a year without anyone else's code noticing." Design every module assuming it will be rewritten at least once.

*Integration is scheduled, not accidental.* The contract tests in Section 4 and the `develop` → `main` cadence exist so that "does everyone's code still work together" is answered by CI on a known schedule, not discovered in production after a silent breaking change.

*Keep the base layer boring on purpose.* The fastest way to wreck this whole structure is letting `core/` or `shared/` accumulate feature-specific logic because it was "just easier." Any PR touching those folders should come with a one-paragraph ADR (architecture decision record, just a short markdown file in `docs/adr/`) answering: what's changing, why it can't live in a module, and what it now makes harder to change later. That friction is deliberate — it's the only thing keeping the engine from growing a hundred special cases.

*Grow horizontally, not vertically.* A new capability is a new module directory, never a new branch of logic bolted onto an existing one. If a feature doesn't fit cleanly into one module's responsibility, that's a sign you need a new module (or a new interface variant), not an exception inside an old one.

This is the whole game: a small, stable, almost boring core; a strict, enforced boundary around it; and a folder-per-feature structure where independence is the default, not something the team has to remember to maintain.
