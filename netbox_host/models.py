# SPDX-License-Identifier: AGPL-3.0-or-later
"""Host OS configuration, one row per declared object, scoped to exactly one host.

A *host* is a ``dcim.Device`` (a hypervisor or appliance) or a ``virtualization.VirtualMachine``
(an LXC container or KVM guest). Every model here carries both FKs and a check constraint that
exactly one is set, so the pipeline reads "everything declared on host X" with one filter.

* :class:`HostGroup` / :class:`HostUser` -- OS accounts.
* :class:`HostDirectory` / :class:`HostSymlink` -- filesystem layout.
* :class:`HostFile` + :class:`HostFileEntry` -- a managed file and its ordered entries.
* :class:`HostSystemdUnit` -- a unit's desired state; its definition is a :class:`HostFile`.
* :class:`HostPackage` -- an OS or language package.

Owners and groups are names, not FKs: many are created by packages (``www-data``), not declared.
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from netbox.models import NetBoxModel

from .choices import FileFormatChoices, PackageManagerChoices, PackageStateChoices

MODE_VALIDATOR = RegexValidator(r"^[0-7]{3,4}$", "An octal file mode such as 0644 or 755.")
PATH_VALIDATOR = RegexValidator(r"^/", "An absolute path.")
NAME_MAX = 64
PATH_MAX = 1024


def host_constraints(label: str, *fields: str) -> list[models.BaseConstraint]:
    """The exactly-one-host check plus a per-host unique constraint on ``fields``."""
    return [
        models.CheckConstraint(
            condition=(
                Q(device__isnull=False, virtual_machine__isnull=True)
                | Q(device__isnull=True, virtual_machine__isnull=False)
            ),
            name=f"netbox_host_{label}_one_host",
        ),
        models.UniqueConstraint(
            fields=["device", *fields],
            condition=Q(device__isnull=False),
            name=f"netbox_host_{label}_unique_device",
        ),
        models.UniqueConstraint(
            fields=["virtual_machine", *fields],
            condition=Q(virtual_machine__isnull=False),
            name=f"netbox_host_{label}_unique_vm",
        ),
    ]


class HostScopedModel(NetBoxModel):
    """Exactly one of ``device`` / ``virtual_machine`` names the host the row is declared on."""

    device = models.ForeignKey(
        "dcim.Device",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )
    virtual_machine = models.ForeignKey(
        "virtualization.VirtualMachine",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True

    @property
    def host(self):
        return self.device or self.virtual_machine

    def clean(self):
        super().clean()
        if bool(self.device_id) == bool(self.virtual_machine_id):
            raise ValidationError("Set exactly one of device or virtual machine.")

    def get_absolute_url(self):
        return reverse(f"plugins:netbox_host:{self._meta.model_name}", args=[self.pk])


class HostGroup(HostScopedModel):
    name = models.CharField(max_length=NAME_MAX)
    gid = models.PositiveIntegerField(null=True, blank=True, help_text="Empty lets the OS allocate one.")
    system = models.BooleanField(default=False, help_text="A system group (groupadd --system).")

    class Meta:
        ordering = ("device", "virtual_machine", "name")
        verbose_name = "Host Group"
        constraints = host_constraints("hostgroup", "name")

    def __str__(self):
        return f"{self.host}: {self.name}"


class HostUser(HostScopedModel):
    name = models.CharField(max_length=NAME_MAX)
    uid = models.PositiveIntegerField(null=True, blank=True, help_text="Empty lets the OS allocate one.")
    primary_group = models.ForeignKey(
        HostGroup,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="primary_members",
        help_text="Empty uses the user's own same-named group.",
    )
    groups = models.ManyToManyField(HostGroup, blank=True, related_name="members")
    home = models.CharField(max_length=PATH_MAX, blank=True, validators=[PATH_VALIDATOR])
    shell = models.CharField(max_length=PATH_MAX, blank=True, validators=[PATH_VALIDATOR])
    system = models.BooleanField(default=False, help_text="A system account (useradd --system).")
    create_home = models.BooleanField(default=False)

    class Meta:
        ordering = ("device", "virtual_machine", "name")
        verbose_name = "Host User"
        constraints = host_constraints("hostuser", "name")

    def __str__(self):
        return f"{self.host}: {self.name}"

    def clean(self):
        super().clean()
        if self.primary_group_id and (self.primary_group.device_id, self.primary_group.virtual_machine_id) != (
            self.device_id,
            self.virtual_machine_id,
        ):
            raise ValidationError({"primary_group": "The primary group must be declared on the same host."})


class _OwnedPath(HostScopedModel):
    path = models.CharField(max_length=PATH_MAX, validators=[PATH_VALIDATOR])
    owner = models.CharField(max_length=NAME_MAX, default="root")
    group = models.CharField(max_length=NAME_MAX, default="root")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.host}: {self.path}"


class HostDirectory(_OwnedPath):
    mode = models.CharField(max_length=4, default="0755", validators=[MODE_VALIDATOR])

    class Meta:
        ordering = ("device", "virtual_machine", "path")
        verbose_name = "Host Directory"
        verbose_name_plural = "Host Directories"
        constraints = host_constraints("hostdirectory", "path")


class HostSymlink(_OwnedPath):
    target = models.CharField(
        max_length=PATH_MAX,
        help_text="What the link points at; may be relative to the link's directory.",
    )

    class Meta:
        ordering = ("device", "virtual_machine", "path")
        verbose_name = "Host Symlink"
        constraints = host_constraints("hostsymlink", "path")


class HostFile(_OwnedPath):
    mode = models.CharField(max_length=4, default="0644", validators=[MODE_VALIDATOR])
    format = models.CharField(max_length=16, choices=FileFormatChoices)
    separator = models.CharField(
        max_length=8,
        blank=True,
        help_text="Key/value separator for the key_value format (e.g. ' = ' or ' ').",
    )
    indent = models.CharField(
        max_length=16,
        blank=True,
        help_text="Leading whitespace for key entries inside a section (ini/systemd).",
    )
    header = models.CharField(max_length=255, blank=True, help_text="A comment line written at the top.")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("device", "virtual_machine", "path")
        verbose_name = "Host File"
        constraints = host_constraints("hostfile", "path")

    def clean(self):
        super().clean()
        if self.format == FileFormatChoices.KEY_VALUE and not self.separator:
            raise ValidationError({"separator": "The key_value format needs a separator."})


class HostFileEntry(NetBoxModel):
    """One ordered line of a managed file. ``position`` orders the file; a key may repeat (systemd
    ``ExecStartPre``, rsync ``exclude``), so the unique identity is the position, not the key."""

    file = models.ForeignKey(HostFile, on_delete=models.CASCADE, related_name="entries")
    position = models.PositiveIntegerField()
    section = models.CharField(max_length=255, blank=True, help_text="INI/systemd section; empty for flat formats.")
    key = models.CharField(max_length=255, blank=True, help_text="Empty for the lines format.")
    value = models.TextField(blank=True)
    openbao_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secret value: the OpenBao path#key the provider resolves. Never store the secret in value.",
    )

    class Meta:
        ordering = ("file", "position")
        verbose_name = "Host File Entry"
        verbose_name_plural = "Host File Entries"
        constraints = (
            models.UniqueConstraint(fields=["file", "position"], name="netbox_host_hostfileentry_unique_position"),
        )

    def __str__(self):
        return f"{self.file.path}#{self.position}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_host:hostfileentry", args=[self.pk])

    def clean(self):
        super().clean()
        if self.value and self.openbao_path:
            raise ValidationError("A secret entry names its openbao_path and leaves value empty.")


class HostSystemdUnit(HostScopedModel):
    name = models.CharField(max_length=255, help_text="The unit name, e.g. rsyncd-wp-omg.service.")
    file = models.OneToOneField(
        HostFile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="systemd_unit",
        help_text="The unit definition; empty for a unit a package ships.",
    )
    enabled = models.BooleanField(default=True)
    started = models.BooleanField(default=True)
    restart_on_change = models.BooleanField(default=True)

    class Meta:
        ordering = ("device", "virtual_machine", "name")
        verbose_name = "Host systemd Unit"
        constraints = host_constraints("hostsystemdunit", "name")

    def __str__(self):
        return f"{self.host}: {self.name}"

    def clean(self):
        super().clean()
        if self.file_id and self.file.format != FileFormatChoices.SYSTEMD:
            raise ValidationError({"file": "A unit's definition file uses the systemd format."})


class HostPackage(HostScopedModel):
    manager = models.CharField(max_length=8, choices=PackageManagerChoices, default=PackageManagerChoices.APT)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=128, blank=True, help_text="Empty accepts any version.")
    state = models.CharField(max_length=8, choices=PackageStateChoices, default=PackageStateChoices.PRESENT)

    class Meta:
        ordering = ("device", "virtual_machine", "manager", "name")
        verbose_name = "Host Package"
        constraints = host_constraints("hostpackage", "manager", "name")

    def __str__(self):
        return f"{self.host}: {self.manager}:{self.name}"
