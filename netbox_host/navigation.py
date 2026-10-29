# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

from .spec import SPECS

menu = PluginMenu(
    label="Host",
    icon_class="mdi mdi-server",
    groups=(
        (
            "Host OS",
            tuple(
                PluginMenuItem(
                    link=f"plugins:netbox_host:{s.model._meta.model_name}_list",
                    link_text=str(s.model._meta.verbose_name_plural).title(),
                    buttons=[
                        PluginMenuButton(
                            f"plugins:netbox_host:{s.model._meta.model_name}_add", "Add", "mdi mdi-plus-thick"
                        ),
                    ],
                )
                for s in SPECS
            ),
        ),
    ),
)
