# SPDX-License-Identifier: AGPL-3.0-or-later
import operator
from functools import reduce

import django_filters
from dcim.models import Device
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from virtualization.models import VirtualMachine

from .spec import PLUGIN_FKS, SPECS, ModelSpec

#: model -> filterset class.
FILTERSETS: dict[type, type[NetBoxModelFilterSet]] = {}


def _fk_filters(field: str, queryset, natural: str | None) -> dict[str, django_filters.Filter]:
    """NetBox's `<fk>_id` (by PK) plus `<fk>` (by natural key) pair; django-filter derives neither."""
    filters = {
        f"{field}_id": django_filters.ModelMultipleChoiceFilter(field_name=field, queryset=queryset),
    }
    if natural:
        filters[field] = django_filters.ModelMultipleChoiceFilter(
            field_name=f"{field}__{natural}",
            to_field_name=natural,
            queryset=queryset,
        )
    return filters


def _build(spec: ModelSpec) -> type[NetBoxModelFilterSet]:
    attrs: dict[str, object] = {}
    plain = []
    if spec.host_scoped:
        attrs.update(_fk_filters("device", Device.objects.all(), "name"))
        attrs.update(_fk_filters("virtual_machine", VirtualMachine.objects.all(), "name"))
    for field in spec.fields:
        if field in PLUGIN_FKS:
            attrs.update(_fk_filters(field, PLUGIN_FKS[field].objects.all(), None))
        elif spec.model._meta.get_field(field).get_internal_type() != "TextField":
            plain.append(field)

    search_fields = spec.search

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(reduce(operator.or_, (Q(**{f"{f}__icontains": value}) for f in search_fields)))

    attrs["search"] = search
    attrs["Meta"] = type("Meta", (), {"model": spec.model, "fields": ("id", *plain)})
    return type(f"{spec.model.__name__}FilterSet", (NetBoxModelFilterSet,), attrs)


for _spec in SPECS:
    FILTERSETS[_spec.model] = _build(_spec)
    globals()[FILTERSETS[_spec.model].__name__] = FILTERSETS[_spec.model]
