# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter

from ..spec import SPECS
from .views import VIEWSETS

app_name = "netbox_host"

router = NetBoxRouter()
for _spec in SPECS:
    router.register(_spec.slug, VIEWSETS[_spec.model])

urlpatterns = router.urls
