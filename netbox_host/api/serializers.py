# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.api.serializers import DeviceSerializer
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from virtualization.api.serializers import VirtualMachineSerializer

from ..spec import PLUGIN_FKS, SPECS, WHITESPACE_FIELDS, ModelSpec

COMMON_TAIL = ("tags", "custom_fields", "created", "last_updated")
HOST_FIELDS = ("device", "virtual_machine")

#: model -> serializer class, filled in SPECS order so a plugin FK's target is built first.
SERIALIZERS: dict[type, type[NetBoxModelSerializer]] = {}


def _build(spec: ModelSpec) -> type[NetBoxModelSerializer]:
    name = spec.model._meta.model_name
    attrs: dict[str, object] = {
        "url": serializers.HyperlinkedIdentityField(view_name=f"plugins-api:netbox_host-api:{name}-detail"),
    }
    host = HOST_FIELDS if spec.host_scoped else ()
    if spec.host_scoped:
        attrs["device"] = DeviceSerializer(nested=True, required=False, allow_null=True)
        attrs["virtual_machine"] = VirtualMachineSerializer(nested=True, required=False, allow_null=True)
    for field in spec.fields:
        if field in PLUGIN_FKS:
            target = SERIALIZERS[PLUGIN_FKS[field]]
            model_field = spec.model._meta.get_field(field)
            if model_field.many_to_many:
                attrs[field] = SerializedPKRelatedField(
                    queryset=PLUGIN_FKS[field].objects.all(),
                    serializer=target,
                    nested=True,
                    many=True,
                    required=False,
                )
            else:
                attrs[field] = target(nested=True, required=not model_field.null, allow_null=model_field.null)
    for field in WHITESPACE_FIELDS.intersection(spec.fields):
        model_field = spec.model._meta.get_field(field)
        attrs[field] = serializers.CharField(
            trim_whitespace=False,
            allow_blank=True,
            required=False,
            max_length=model_field.max_length,
        )
    attrs["Meta"] = type(
        "Meta",
        (),
        {
            "model": spec.model,
            "fields": ("id", "url", "display", *host, *spec.fields, *COMMON_TAIL),
            "brief_fields": ("id", "url", "display", *host, *spec.brief),
        },
    )
    return type(f"{spec.model.__name__}Serializer", (NetBoxModelSerializer,), attrs)


for _spec in SPECS:
    SERIALIZERS[_spec.model] = _build(_spec)
    globals()[SERIALIZERS[_spec.model].__name__] = SERIALIZERS[_spec.model]
