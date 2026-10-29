# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.models import Device
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from virtualization.models import VirtualMachine

from .spec import PLUGIN_FKS, SPECS, WHITESPACE_FIELDS, ModelSpec

#: model -> (edit form, filter form).
FORMS: dict[type, tuple[type[NetBoxModelForm], type[NetBoxModelFilterSetForm]]] = {}


def _build(spec: ModelSpec) -> tuple[type[NetBoxModelForm], type[NetBoxModelFilterSetForm]]:
    edit: dict[str, object] = {}
    host = ("device", "virtual_machine") if spec.host_scoped else ()
    if spec.host_scoped:
        edit["device"] = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
        edit["virtual_machine"] = DynamicModelChoiceField(queryset=VirtualMachine.objects.all(), required=False)
    for field in spec.fields:
        if field in PLUGIN_FKS:
            model_field = spec.model._meta.get_field(field)
            cls = DynamicModelMultipleChoiceField if model_field.many_to_many else DynamicModelChoiceField
            edit[field] = cls(
                queryset=PLUGIN_FKS[field].objects.all(),
                required=model_field.blank is False and not model_field.many_to_many,
            )
    for field in WHITESPACE_FIELDS.intersection(spec.fields):
        model_field = spec.model._meta.get_field(field)
        widget = forms.Textarea if model_field.get_internal_type() == "TextField" else forms.TextInput
        edit[field] = forms.CharField(strip=False, required=False, max_length=model_field.max_length, widget=widget)
    label = spec.model._meta.verbose_name
    edit["fieldsets"] = (FieldSet(*host, *spec.fields, name=label),)
    edit["Meta"] = type("Meta", (), {"model": spec.model, "fields": (*host, *spec.fields, "tags")})
    edit_form = type(f"{spec.model.__name__}Form", (NetBoxModelForm,), edit)

    filt: dict[str, object] = {"model": spec.model, "tag": TagFilterField(spec.model)}
    if spec.host_scoped:
        filt["device_id"] = DynamicModelMultipleChoiceField(
            queryset=Device.objects.all(), required=False, label="Device"
        )
        filt["virtual_machine_id"] = DynamicModelMultipleChoiceField(
            queryset=VirtualMachine.objects.all(),
            required=False,
            label="Virtual machine",
        )
    filter_form = type(f"{spec.model.__name__}FilterForm", (NetBoxModelFilterSetForm,), filt)
    return edit_form, filter_form


for _spec in SPECS:
    FORMS[_spec.model] = _build(_spec)
