# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import include, path
from utilities.urls import get_model_urls

from . import views  # noqa: F401  (registers the model views)
from .spec import SPECS

urlpatterns = []
for _spec in SPECS:
    name = _spec.model._meta.model_name
    urlpatterns += [
        path(f"{_spec.slug}/", include(get_model_urls("netbox_host", name, detail=False))),
        path(f"{_spec.slug}/<int:pk>/", include(get_model_urls("netbox_host", name))),
    ]
