# AI Visual Commerce Platform

A modular monorepo: a small, stable base layer (`core/` + `shared/`) with
feature modules (`modules/`) that plug into it independently.

Read **docs/ARCHITECTURE.md** first — it explains the full design,
team workflow, and the rules that keep modules independent.

## Quick start for a new feature module
1. Copy `modules/_template/` to `modules/<your_feature>/`
2. Fill in `schemas/schemas.py`, `services/service.py`, `api/routes.py`
3. Add one line to `core/api_gateway/router.py`'s `MODULE_REGISTRY`
4. Add an entry to `.github/CODEOWNERS`
5. Open a PR — it should only touch your module folder + that one registry line
