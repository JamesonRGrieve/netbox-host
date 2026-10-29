# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .spec import PLUGIN_FKS, SPECS, ModelSpec

#: model -> table class.
TABLES: dict[type, type[NetBoxTable]] = {}


def _build(spec: ModelSpec) -> type[NetBoxTable]:
    name = spec.model._meta.model_name
    attrs: dict[str, object] = {
        spec.fields[0]: tables.Column(linkify=True),
        "tags": columns.TagColumn(url_name=f"plugins:netbox_host:{name}_list"),
    }
    host = ("device", "virtual_machine") if spec.host_scoped else ()
    if spec.host_scoped:
        attrs["device"] = tables.Column(linkify=True)
        attrs["virtual_machine"] = tables.Column(linkify=True)
    for field in spec.fields[1:]:
        model_field = spec.model._meta.get_field(field)
        if field in PLUGIN_FKS and not model_field.many_to_many:
            attrs[field] = tables.Column(linkify=True)
        elif model_field.get_internal_type() == "BooleanField":
            attrs[field] = columns.BooleanColumn()
        elif model_field.choices:
            attrs[field] = columns.ChoiceFieldColumn()
    attrs["Meta"] = type(
        "Meta",
        (NetBoxTable.Meta,),
        {
            "model": spec.model,
            "fields": ("pk", "id", *host, *spec.fields, "tags", "created", "last_updated"),
            "default_columns": (*host, *spec.fields[:5]),
        },
    )
    return type(f"{spec.model.__name__}Table", (NetBoxTable,), attrs)


for _spec in SPECS:
    TABLES[_spec.model] = _build(_spec)
