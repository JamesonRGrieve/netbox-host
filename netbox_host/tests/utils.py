# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared fixtures: a real core VM and a real core Device, the two kinds of host every row needs."""

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from virtualization.models import Cluster, ClusterType, VirtualMachine


def make_vm(name: str) -> VirtualMachine:
    ctype, _ = ClusterType.objects.get_or_create(name="PVE", slug="pve")
    cluster, _ = Cluster.objects.get_or_create(name="core", type=ctype)
    return VirtualMachine.objects.create(name=name, cluster=cluster)


def make_device(name: str) -> Device:
    site, _ = Site.objects.get_or_create(name="house", slug="house")
    maker, _ = Manufacturer.objects.get_or_create(name="Generic", slug="generic")
    dtype, _ = DeviceType.objects.get_or_create(manufacturer=maker, model="Server", slug="server")
    role, _ = DeviceRole.objects.get_or_create(name="Hypervisor", slug="hypervisor")
    return Device.objects.create(name=name, site=site, device_type=dtype, role=role)
