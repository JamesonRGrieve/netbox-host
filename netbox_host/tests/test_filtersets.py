# SPDX-License-Identifier: AGPL-3.0-or-later
"""Filterset behaviour on real rows: host filters by id and by name, plugin FK filters, plain
field filters and free-text search."""

from django.test import TestCase

from netbox_host.choices import FileFormatChoices
from netbox_host.filtersets import FILTERSETS
from netbox_host.models import HostDirectory, HostFile, HostFileEntry, HostGroup, HostUser

from .utils import make_device, make_vm


class FilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vm = make_vm("prod-samba")
        cls.device = make_device("backup")
        HostDirectory.objects.create(virtual_machine=cls.vm, path="/srv/samba/nimble", mode="0775")
        HostDirectory.objects.create(virtual_machine=cls.vm, path="/srv/samba/roms")
        HostDirectory.objects.create(device=cls.device, path="/pool_3tb/downloads")
        cls.file = HostFile.objects.create(
            virtual_machine=cls.vm, path="/etc/samba/smb.conf", format=FileFormatChoices.INI
        )
        HostFileEntry.objects.create(file=cls.file, position=1, section="global", key="workgroup", value="ZEPHYREX")
        cls.group = HostGroup.objects.create(virtual_machine=cls.vm, name="media")
        user = HostUser.objects.create(virtual_machine=cls.vm, name="samba")
        user.groups.set([cls.group])
        HostUser.objects.create(virtual_machine=cls.vm, name="vr")

    def _qs(self, model, params):
        return FILTERSETS[model](params, model.objects.all()).qs

    def test_host_filters_by_id_and_name(self):
        self.assertEqual(self._qs(HostDirectory, {"virtual_machine_id": [self.vm.pk]}).count(), 2)
        self.assertEqual(self._qs(HostDirectory, {"virtual_machine": ["prod-samba"]}).count(), 2)
        self.assertEqual(self._qs(HostDirectory, {"device": ["backup"]}).count(), 1)

    def test_plain_field_filter(self):
        self.assertEqual(self._qs(HostDirectory, {"mode": ["0775"]}).count(), 1)

    def test_search_matches_the_spec_fields(self):
        self.assertEqual(self._qs(HostDirectory, {"q": "roms"}).count(), 1)
        self.assertEqual(self._qs(HostFileEntry, {"q": "ZEPHYREX"}).count(), 1)

    def test_plugin_fk_filters(self):
        self.assertEqual(self._qs(HostFileEntry, {"file_id": [self.file.pk]}).count(), 1)
        self.assertEqual(self._qs(HostUser, {"groups_id": [self.group.pk]}).count(), 1)
