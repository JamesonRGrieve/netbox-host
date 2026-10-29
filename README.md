# netbox-host

A NetBox 4.6 plugin that holds a host's OS configuration as typed NetBox objects: groups, users,
directories, symlinks, managed files, systemd units and packages. Every object belongs to exactly
one device or virtual machine.

The OpenTofu pipeline reads these objects through the REST API and converges each host to them,
so none of this configuration lives as literals in HCL.

## Models

| Model | REST endpoint | Per-host key |
|---|---|---|
| Host Group | `/api/plugins/host/groups/` | name |
| Host User | `/api/plugins/host/users/` | name |
| Host Directory | `/api/plugins/host/directories/` | path |
| Host Symlink | `/api/plugins/host/symlinks/` | path |
| Host File | `/api/plugins/host/files/` | path |
| Host File Entry | `/api/plugins/host/file-entries/` | file + position |
| Host systemd Unit | `/api/plugins/host/systemd-units/` | name |
| Host Package | `/api/plugins/host/packages/` | manager + name |

A file's entries are ordered by `position`, and a key may repeat (for example systemd
`ExecStartPre`). An entry that needs a secret names its OpenBao path in `openbao_path` and leaves
`value` empty. NetBox never stores the secret.

## Install

```
pip install netbox-host
```

Add `netbox_host` to `PLUGINS` and run `manage.py migrate`. On the Zephyrex fleet the pipeline
does both from `svc_netbox.tf`.

## License

AGPL-3.0-or-later.
