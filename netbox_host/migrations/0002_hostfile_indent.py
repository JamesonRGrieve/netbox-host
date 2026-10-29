# SPDX-License-Identifier: AGPL-3.0-or-later
# HostFile.indent: leading whitespace for key entries inside a section.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_host', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostfile',
            name='indent',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]
