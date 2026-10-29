# netbox-host — Agent Operating Guide

Cross-repo standards live in the Zephyrex SOP collective (read over the `nextcloud` MCP):
*Stack Standards → Python*, *Control Plane & Pipeline → NetBox Modelling* and
*NetBox Plugins (install & enable)*. This file adds repo specifics.

## What this is

The NetBox 4.6 plugin for host and container OS configuration: groups, users, directories,
symlinks, managed files (with ordered entries), systemd units and packages. Every row is scoped
to exactly one `dcim.Device` or `virtualization.VirtualMachine`, enforced by a check constraint
and `clean()`. Per-host uniqueness is a pair of conditional unique constraints.

## Layout

- `models.py` holds the models and `host_constraints()`.
- `spec.py` declares each model's fields once. The serializers, filtersets, forms, tables, views
  and URLs are all generated from it, so a new field goes into the model and `spec.py` only.
- `migrations/` are generated with `makemigrations` against NetBox 4.6.1 and reviewed by hand.

## Rules

- No secret is ever a value. A file entry that needs one sets `openbao_path` and leaves `value`
  empty; `clean()` rejects both together.
- `separator` and `value` keep leading and trailing whitespace (`WHITESPACE_FIELDS`); never let a
  form or serializer strip them.
- Tests use the real database and API client, no mocks.

## Gate

On an ephemeral NetBox at prod's release tag (see the SOP page *NetBox Plugins → Running a suite
on an ephemeral NetBox*):

```
manage.py makemigrations netbox_host --check --dry-run
manage.py test netbox_host --noinput --parallel 4
uvx ruff format --check . && uvx ruff check .
```
