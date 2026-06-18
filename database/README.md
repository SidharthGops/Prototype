# Database

Single source of truth for schema and migrations — not scattered across
modules. Suggested initial tables: users, jobs, history, catalogs, products.

A `jobs` table should track job_id, module_name, status, created_at,
metadata — generic enough that any module can write to it through the
core storage/job layer without the table needing per-module columns.
