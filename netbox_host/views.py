# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from utilities.views import register_model_view

from .filtersets import FILTERSETS
from .forms import FORMS
from .spec import SPECS, ModelSpec
from .tables import TABLES

OBJECT_TEMPLATE = "netbox_host/object.html"


def _register(spec: ModelSpec) -> None:
    model = spec.model
    edit_form, filter_form = FORMS[model]
    queryset = model.objects.all()

    class ObjectView(generic.ObjectView):
        template_name = OBJECT_TEMPLATE

        def get_extra_context(self, request, instance):
            host = ("device", "virtual_machine") if spec.host_scoped else ()
            rows = []
            for field in (*host, *spec.fields):
                model_field = model._meta.get_field(field)
                value = getattr(instance, field)
                if model_field.many_to_many:
                    value = ", ".join(str(v) for v in value.all())
                elif model_field.choices:
                    value = getattr(instance, f"get_{field}_display")()
                rows.append((model_field.verbose_name, value))
            return {"rows": rows}

    # (view name, base view, class attrs, register_model_view kwargs), as NetBox's own apps register them.
    views = (
        ("", ObjectView, {}, {}),
        (
            "list",
            generic.ObjectListView,
            {"table": TABLES[model], "filterset": FILTERSETS[model], "filterset_form": filter_form},
            {"path": "", "detail": False},
        ),
        ("add", generic.ObjectEditView, {"form": edit_form}, {"detail": False}),
        ("edit", generic.ObjectEditView, {"form": edit_form}, {}),
        ("delete", generic.ObjectDeleteView, {}, {}),
        (
            "bulk_delete",
            generic.BulkDeleteView,
            {"table": TABLES[model], "filterset": FILTERSETS[model]},
            {"path": "delete", "detail": False},
        ),
    )
    for name, base, attrs, register in views:
        cls = type(f"{model.__name__}{name.title().replace('_', '')}View", (base,), {"queryset": queryset, **attrs})
        register_model_view(model, name, **register)(cls)


for _spec in SPECS:
    _register(_spec)
