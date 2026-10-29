# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model invariants against the real test database (no mocks): one host per row, per-host
uniqueness, and the cross-field rules enforced in clean()."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from netbox_host.choices import FileFormatChoices, PackageManagerChoices
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


class HostScopeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vm = make_vm("prod-samba")
        cls.other_vm = make_vm("prod-other")
        cls.device = make_device("backup")

    def test_exactly_one_host_is_enforced_by_the_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            HostDirectory.objects.create(path="/srv/a")
        with self.assertRaises(IntegrityError), transaction.atomic():
            HostDirectory.objects.create(path="/srv/a", device=self.device, virtual_machine=self.vm)

    def test_clean_rejects_no_host_and_two_hosts(self):
        with self.assertRaises(ValidationError):
            HostDirectory(path="/srv/a").full_clean()
        with self.assertRaises(ValidationError):
            HostDirectory(path="/srv/a", device=self.device, virtual_machine=self.vm).full_clean()

    def test_path_is_unique_per_host_not_globally(self):
        HostDirectory.objects.create(virtual_machine=self.vm, path="/srv/samba")
        HostDirectory.objects.create(virtual_machine=self.other_vm, path="/srv/samba")
        HostDirectory.objects.create(device=self.device, path="/srv/samba")
        with self.assertRaises(IntegrityError), transaction.atomic():
            HostDirectory.objects.create(virtual_machine=self.vm, path="/srv/samba")

    def test_host_property_returns_the_scoped_object(self):
        on_vm = HostSymlink.objects.create(virtual_machine=self.vm, path="/a", target="b")
        on_device = HostSymlink.objects.create(device=self.device, path="/a", target="b")
        self.assertEqual(on_vm.host, self.vm)
        self.assertEqual(on_device.host, self.device)

    def test_validators_reject_relative_paths_and_bad_modes(self):
        with self.assertRaises(ValidationError):
            HostDirectory(virtual_machine=self.vm, path="srv/samba").full_clean()
        with self.assertRaises(ValidationError):
            HostDirectory(virtual_machine=self.vm, path="/srv/samba", mode="0899").full_clean()
        HostDirectory(virtual_machine=self.vm, path="/srv/samba", mode="2775").full_clean()

    def test_deleting_the_host_cascades(self):
        vm = make_vm("doomed")
        HostPackage.objects.create(virtual_machine=vm, name="samba")
        vm.delete()
        self.assertFalse(HostPackage.objects.filter(name="samba").exists())


class HostUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vm = make_vm("prod-samba")
        cls.other_vm = make_vm("prod-other")

    def test_user_with_groups_round_trips(self):
        primary = HostGroup.objects.create(virtual_machine=self.vm, name="samba", gid=1000)
        media = HostGroup.objects.create(virtual_machine=self.vm, name="media")
        user = HostUser.objects.create(virtual_machine=self.vm, name="samba", uid=1000, primary_group=primary)
        user.groups.set([media])
        self.assertEqual(list(primary.primary_members.all()), [user])
        self.assertEqual(list(media.members.all()), [user])

    def test_primary_group_must_be_on_the_same_host(self):
        foreign = HostGroup.objects.create(virtual_machine=self.other_vm, name="samba")
        with self.assertRaises(ValidationError):
            HostUser(virtual_machine=self.vm, name="samba", primary_group=foreign).full_clean()

    def test_a_group_in_use_as_primary_cannot_be_deleted(self):
        primary = HostGroup.objects.create(virtual_machine=self.vm, name="vr")
        HostUser.objects.create(virtual_machine=self.vm, name="vr", primary_group=primary)
        with self.assertRaises(ProtectedError), transaction.atomic():
            primary.delete()


class HostFileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vm = make_vm("prod-wp-omg")

    def test_entries_are_ordered_and_keys_may_repeat(self):
        f = HostFile.objects.create(
            virtual_machine=self.vm, path="/etc/rsyncd-wp-omg.conf", format=FileFormatChoices.INI
        )
        HostFileEntry.objects.create(file=f, position=20, section="wp-omg-docroot", key="exclude", value="cache")
        HostFileEntry.objects.create(
            file=f, position=10, section="wp-omg-docroot", key="exclude", value="wp-config.php"
        )
        self.assertEqual([e.value for e in f.entries.all()], ["wp-config.php", "cache"])

    def test_position_is_unique_within_a_file(self):
        f = HostFile.objects.create(virtual_machine=self.vm, path="/etc/x.conf", format=FileFormatChoices.ENV)
        HostFileEntry.objects.create(file=f, position=1, key="A", value="1")
        with self.assertRaises(IntegrityError), transaction.atomic():
            HostFileEntry.objects.create(file=f, position=1, key="B", value="2")

    def test_key_value_format_needs_a_separator(self):
        with self.assertRaises(ValidationError):
            HostFile(virtual_machine=self.vm, path="/etc/x.conf", format=FileFormatChoices.KEY_VALUE).full_clean()
        HostFile(
            virtual_machine=self.vm,
            path="/etc/x.conf",
            format=FileFormatChoices.KEY_VALUE,
            separator=" = ",
        ).full_clean()

    def test_a_secret_entry_carries_a_path_never_a_value(self):
        f = HostFile.objects.create(virtual_machine=self.vm, path="/etc/x.env", format=FileFormatChoices.ENV)
        with self.assertRaises(ValidationError):
            HostFileEntry(
                file=f, position=1, key="DB_PASSWORD", value="hunter2", openbao_path="secret/x#pw"
            ).full_clean()
        HostFileEntry(file=f, position=1, key="DB_PASSWORD", openbao_path="secret/x#pw").full_clean()

    def test_deleting_a_file_deletes_its_entries(self):
        f = HostFile.objects.create(virtual_machine=self.vm, path="/etc/y.env", format=FileFormatChoices.ENV)
        HostFileEntry.objects.create(file=f, position=1, key="A", value="1")
        f.delete()
        self.assertFalse(HostFileEntry.objects.exists())


class HostSystemdUnitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vm = make_vm("prod-wp-omg")

    def test_unit_definition_must_be_a_systemd_file(self):
        env = HostFile.objects.create(virtual_machine=self.vm, path="/etc/x.env", format=FileFormatChoices.ENV)
        with self.assertRaises(ValidationError):
            HostSystemdUnit(virtual_machine=self.vm, name="x.service", file=env).full_clean()

    def test_package_shipped_unit_has_no_file(self):
        HostSystemdUnit(virtual_machine=self.vm, name="smbd.service").full_clean()

    def test_a_unit_protects_its_definition_file(self):
        f = HostFile.objects.create(
            virtual_machine=self.vm,
            path="/etc/systemd/system/rsyncd.service",
            format=FileFormatChoices.SYSTEMD,
        )
        HostSystemdUnit.objects.create(virtual_machine=self.vm, name="rsyncd.service", file=f)
        with self.assertRaises(ProtectedError), transaction.atomic():
            f.delete()


class HostPackageTest(TestCase):
    def test_name_is_unique_per_manager_per_host(self):
        vm = make_vm("prod-penguin")
        HostPackage.objects.create(virtual_machine=vm, manager=PackageManagerChoices.APT, name="git")
        HostPackage.objects.create(virtual_machine=vm, manager=PackageManagerChoices.UV, name="git")
        with self.assertRaises(IntegrityError), transaction.atomic():
            HostPackage.objects.create(virtual_machine=vm, manager=PackageManagerChoices.APT, name="git")
