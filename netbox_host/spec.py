# SPDX-License-Identifier: AGPL-3.0-or-later
"""One field spec per model, shared by the serializers, filtersets, forms, tables and views so a
field is declared once. ``fields`` are the model's own editable fields in display order;
``brief`` is the REST brief representation; ``search`` the free-text search fields."""

from dataclasses import dataclass

from . import models


@dataclass(frozen=True)
class ModelSpec:
    model: type
    slug: str
    fields: tuple[str, ...]
    brief: tuple[str, ...]
    search: tuple[str, ...]
    host_scoped: bool = True


SPECS: tuple[ModelSpec, ...] = (
    ModelSpec(models.HostGroup, "groups", ("name", "gid", "system"), ("name",), ("name",)),
    ModelSpec(
        models.HostUser,
        "users",
        ("name", "uid", "primary_group", "groups", "home", "shell", "system", "create_home"),
        ("name",),
        ("name", "home"),
    ),
    ModelSpec(models.HostDirectory, "directories", ("path", "owner", "group", "mode"), ("path",), ("path",)),
    ModelSpec(
        models.HostSymlink, "symlinks", ("path", "target", "owner", "group"), ("path", "target"), ("path", "target")
    ),
    ModelSpec(
        models.HostFile,
        "files",
        ("path", "owner", "group", "mode", "format", "separator", "indent", "header", "description"),
        ("path", "format"),
        ("path", "description"),
    ),
    ModelSpec(
        models.HostFileEntry,
        "file-entries",
        ("file", "position", "section", "key", "value", "openbao_path"),
        ("file", "position", "key"),
        ("section", "key", "value"),
        host_scoped=False,
    ),
    ModelSpec(
        models.HostSystemdUnit,
        "systemd-units",
        ("name", "file", "enabled", "started", "restart_on_change"),
        ("name",),
        ("name",),
    ),
    ModelSpec(
        models.HostPackage,
        "packages",
        ("manager", "name", "version", "state"),
        ("manager", "name"),
        ("name", "version"),
    ),
)

#: Foreign keys to other plugin models, by field name: the model they point at.
PLUGIN_FKS: dict[str, type] = {
    "primary_group": models.HostGroup,
    "groups": models.HostGroup,
    "file": models.HostFile,
}

#: Fields whose leading/trailing whitespace is meaningful (a " = " separator, an indented value).
WHITESPACE_FIELDS = frozenset({"separator", "indent", "value"})
