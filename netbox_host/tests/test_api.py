# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests (real DB + real API client, no mocks), one test class per model."""

from typing import ClassVar

from utilities.testing import APIViewTestCases

from netbox_host.choices import FileFormatChoices
from netbox_host.models import (
    HostDirectory,
    HostFile,
    HostFileEntry,
    HostGroup,
    HostPackage,
    HostSymlink,
    HostSystemdUnit,
    HostUser,
)

from .utils import make_device, make_vm


class _PluginAPI:
    """Plugin API views live under the `plugins-api:` namespace. A plain mixin, not a TestCase."""

    view_namespace = "plugins-api:netbox_host"


_CRUD = (
    _PluginAPI,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
)


class HostGroupAPITest(*_CRUD):
    model = HostGroup
    brief_fields: ClassVar[list[str]] = ["device", "display", "id", "name", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"system": True}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        HostGroup.objects.bulk_create([HostGroup(virtual_machine=vm, name=n) for n in ("a", "b", "c")])
        cls.create_data = [
            {"virtual_machine": vm.pk, "name": "samba", "gid": 1000},
            {"virtual_machine": vm.pk, "name": "media", "system": True},
            {"device": make_device("api-dev").pk, "name": "samba"},
        ]


class HostUserAPITest(*_CRUD):
    model = HostUser
    brief_fields: ClassVar[list[str]] = ["device", "display", "id", "name", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"shell": "/bin/bash"}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        group = HostGroup.objects.create(virtual_machine=vm, name="media")
        HostUser.objects.bulk_create([HostUser(virtual_machine=vm, name=n) for n in ("a", "b", "c")])
        cls.create_data = [
            {"virtual_machine": vm.pk, "name": "samba", "uid": 1000, "primary_group": group.pk, "groups": [group.pk]},
            {"virtual_machine": vm.pk, "name": "vr", "home": "/home/vr", "create_home": True},
            {"virtual_machine": vm.pk, "name": "deck", "system": True},
        ]


class HostDirectoryAPITest(*_CRUD):
    model = HostDirectory
    brief_fields: ClassVar[list[str]] = ["device", "display", "id", "path", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"mode": "0750"}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        HostDirectory.objects.bulk_create([HostDirectory(virtual_machine=vm, path=f"/srv/{n}") for n in "abc"])
        cls.create_data = [
            {"virtual_machine": vm.pk, "path": "/srv/samba", "owner": "samba", "group": "samba", "mode": "0775"},
            {"virtual_machine": vm.pk, "path": "/srv/samba/roms"},
            {"device": make_device("api-dev").pk, "path": "/pool_3tb/downloads"},
        ]


class HostSymlinkAPITest(*_CRUD):
    model = HostSymlink
    brief_fields: ClassVar[list[str]] = ["device", "display", "id", "path", "target", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"owner": "samba"}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        HostSymlink.objects.bulk_create([HostSymlink(virtual_machine=vm, path=f"/l/{n}", target="t") for n in "abc"])
        cls.create_data = [
            {"virtual_machine": vm.pk, "path": "/srv/.es-de/snes", "target": "../Nintendo SNES/Roms"},
            {"virtual_machine": vm.pk, "path": "/srv/.es-de/gba", "target": "../Nintendo Gameboy Advance/Roms"},
            {"virtual_machine": vm.pk, "path": "/srv/.es-de/c64", "target": "../Commodore 64/Roms"},
        ]


class HostFileAPITest(*_CRUD):
    model = HostFile
    brief_fields: ClassVar[list[str]] = ["device", "display", "format", "id", "path", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"description": "managed"}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        HostFile.objects.bulk_create(
            [HostFile(virtual_machine=vm, path=f"/etc/{n}.env", format=FileFormatChoices.ENV) for n in "abc"]
        )
        cls.create_data = [
            {"virtual_machine": vm.pk, "path": "/etc/samba/smb.conf", "format": "ini"},
            {"virtual_machine": vm.pk, "path": "/etc/foo.conf", "format": "key_value", "separator": " = "},
            {"virtual_machine": vm.pk, "path": "/etc/systemd/system/x.service", "format": "systemd", "mode": "0600"},
        ]


class HostFileEntryAPITest(*_CRUD):
    model = HostFileEntry
    brief_fields: ClassVar[list[str]] = ["display", "file", "id", "key", "position", "url"]
    bulk_update_data: ClassVar[dict[str, object]] = {"section": "global"}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        f = HostFile.objects.create(virtual_machine=vm, path="/etc/samba/smb.conf", format=FileFormatChoices.INI)
        HostFileEntry.objects.bulk_create([HostFileEntry(file=f, position=p, key="k", value="v") for p in (1, 2, 3)])
        cls.create_data = [
            {"file": f.pk, "position": 10, "section": "global", "key": "workgroup", "value": "ZEPHYREX"},
            {"file": f.pk, "position": 11, "section": "roms", "key": "wide links", "value": "yes"},
            {"file": f.pk, "position": 12, "section": "global", "key": "password", "openbao_path": "secret/x#pw"},
        ]


class HostSystemdUnitAPITest(*_CRUD):
    model = HostSystemdUnit
    brief_fields: ClassVar[list[str]] = ["device", "display", "id", "name", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"started": False}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        unit_file = HostFile.objects.create(
            virtual_machine=vm,
            path="/etc/systemd/system/rsyncd.service",
            format=FileFormatChoices.SYSTEMD,
        )
        HostSystemdUnit.objects.bulk_create([HostSystemdUnit(virtual_machine=vm, name=f"{n}.service") for n in "abc"])
        cls.create_data = [
            {"virtual_machine": vm.pk, "name": "rsyncd.service", "file": unit_file.pk},
            {"virtual_machine": vm.pk, "name": "smbd.service", "enabled": True, "started": True},
            {"virtual_machine": vm.pk, "name": "nmbd.service", "enabled": False, "started": False},
        ]


class HostPackageAPITest(*_CRUD):
    model = HostPackage
    brief_fields: ClassVar[list[str]] = ["device", "display", "id", "manager", "name", "url", "virtual_machine"]
    bulk_update_data: ClassVar[dict[str, object]] = {"version": "4.19"}

    @classmethod
    def setUpTestData(cls):
        vm = make_vm("api-vm")
        HostPackage.objects.bulk_create([HostPackage(virtual_machine=vm, name=n) for n in ("a", "b", "c")])
        cls.create_data = [
            {"virtual_machine": vm.pk, "name": "samba"},
            {"virtual_machine": vm.pk, "manager": "uv", "name": "jupyterlab", "version": "4.2.5"},
            {"virtual_machine": vm.pk, "name": "nginx", "state": "absent"},
        ]
