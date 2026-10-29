# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets import FILTERSETS
from ..spec import PLUGIN_FKS, SPECS, ModelSpec
from .serializers import SERIALIZERS

#: model -> viewset class.
VIEWSETS: dict[type, type[NetBoxModelViewSet]] = {}


def _build(spec: ModelSpec) -> type[NetBoxModelViewSet]:
    related = [f for f in spec.fields if f in PLUGIN_FKS]
    if spec.host_scoped:
        related = ["device", "virtual_machine", *related]
    return type(
        f"{spec.model.__name__}ViewSet",
        (NetBoxModelViewSet,),
        {
            "queryset": spec.model.objects.prefetch_related(*related, "tags"),
            "serializer_class": SERIALIZERS[spec.model],
            "filterset_class": FILTERSETS[spec.model],
        },
    )


for _spec in SPECS:
    VIEWSETS[_spec.model] = _build(_spec)
