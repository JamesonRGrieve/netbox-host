# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-host: the NetBox-native source of truth for host and container **OS configuration**.

Everything on a host that is configuration rather than app data, secrets or runtime state is
modelled here as typed rows scoped to one ``dcim.Device`` or ``virtualization.VirtualMachine``:
OS groups and users, directories, symlinks, managed files with ordered key/value entries,
systemd units and packages. The pipeline's ``host``/``apt`` providers read these rows instead of
literals in HCL (Zephyrex SOP -> Control Plane & Pipeline -> NetBox Modelling).

SECRET POLICY: no secret is ever a value here. A file entry that needs one names its OpenBao path
(``HostFileEntry.openbao_path``); the provider resolves it at apply time.
"""

from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxHostConfig(PluginConfig):
    name = "netbox_host"
    verbose_name = "NetBox Host"
    description = (
        "Native SoT for host/container OS config: users, groups, directories, symlinks, files, units, packages"
    )
    version = __version__
    author = "Jameson"
    base_url = "host"
    # Tracks the in-house plugin fleet / prod NetBox; bump in lockstep when prod upgrades.
    min_version = "4.6.0"
    max_version = "4.6.99"


config = NetBoxHostConfig
