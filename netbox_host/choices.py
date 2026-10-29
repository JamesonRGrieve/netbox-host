# SPDX-License-Identifier: AGPL-3.0-or-later
from utilities.choices import ChoiceSet


class FileFormatChoices(ChoiceSet):
    """How a managed file's entries render. The provider owns the exact syntax per format."""

    INI = "ini"
    ENV = "env"
    KEY_VALUE = "key_value"
    SYSTEMD = "systemd"
    LINES = "lines"

    CHOICES = (
        (INI, "INI ([section] key = value)"),
        (ENV, "Environment (KEY=value)"),
        (KEY_VALUE, "Key/value (key value, with the file's separator)"),
        (SYSTEMD, "systemd unit ([Section] Key=value, repeatable keys)"),
        (LINES, "Lines (value only, one per entry)"),
    )


class PackageManagerChoices(ChoiceSet):
    APT = "apt"
    UV = "uv"
    PNPM = "pnpm"
    NPM = "npm"

    CHOICES = (
        (APT, "apt"),
        (UV, "uv"),
        (PNPM, "pnpm"),
        (NPM, "npm"),
    )


class PackageStateChoices(ChoiceSet):
    PRESENT = "present"
    ABSENT = "absent"

    CHOICES = (
        (PRESENT, "Present", "green"),
        (ABSENT, "Absent", "red"),
    )
