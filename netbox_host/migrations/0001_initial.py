# SPDX-License-Identifier: AGPL-3.0-or-later
# Initial netbox-host schema (generated against NetBox 4.6.1, reviewed by hand).

import django.core.validators
import django.db.models.deletion
import netbox.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0234_cablepath_nodes_index'),
        ('extras', '0138_customfieldchoiceset_choice_colors'),
        ('virtualization', '0056_virtualmachine_render_config_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('path', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator('^/', 'An absolute path.')])),
                ('owner', models.CharField(default='root', max_length=64)),
                ('group', models.CharField(default='root', max_length=64)),
                ('mode', models.CharField(default='0644', max_length=4, validators=[django.core.validators.RegexValidator('^[0-7]{3,4}$', 'An octal file mode such as 0644 or 755.')])),
                ('format', models.CharField(max_length=16)),
                ('separator', models.CharField(blank=True, max_length=8)),
                ('header', models.CharField(blank=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host File',
                'ordering': ('device', 'virtual_machine', 'path'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostFileEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('position', models.PositiveIntegerField()),
                ('section', models.CharField(blank=True, max_length=255)),
                ('key', models.CharField(blank=True, max_length=255)),
                ('value', models.TextField(blank=True)),
                ('openbao_path', models.CharField(blank=True, max_length=255)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='netbox_host.hostfile')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Host File Entry',
                'verbose_name_plural': 'Host File Entries',
                'ordering': ('file', 'position'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=64)),
                ('gid', models.PositiveIntegerField(blank=True, null=True)),
                ('system', models.BooleanField(default=False)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host Group',
                'ordering': ('device', 'virtual_machine', 'name'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('manager', models.CharField(default='apt', max_length=8)),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(blank=True, max_length=128)),
                ('state', models.CharField(default='present', max_length=8)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host Package',
                'ordering': ('device', 'virtual_machine', 'manager', 'name'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostSymlink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('path', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator('^/', 'An absolute path.')])),
                ('owner', models.CharField(default='root', max_length=64)),
                ('group', models.CharField(default='root', max_length=64)),
                ('target', models.CharField(max_length=1024)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host Symlink',
                'ordering': ('device', 'virtual_machine', 'path'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostSystemdUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=255)),
                ('enabled', models.BooleanField(default=True)),
                ('started', models.BooleanField(default=True)),
                ('restart_on_change', models.BooleanField(default=True)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('file', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='systemd_unit', to='netbox_host.hostfile')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host systemd Unit',
                'ordering': ('device', 'virtual_machine', 'name'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=64)),
                ('uid', models.PositiveIntegerField(blank=True, null=True)),
                ('home', models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator('^/', 'An absolute path.')])),
                ('shell', models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator('^/', 'An absolute path.')])),
                ('system', models.BooleanField(default=False)),
                ('create_home', models.BooleanField(default=False)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('groups', models.ManyToManyField(blank=True, related_name='members', to='netbox_host.hostgroup')),
                ('primary_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='primary_members', to='netbox_host.hostgroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host User',
                'ordering': ('device', 'virtual_machine', 'name'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HostDirectory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('path', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator('^/', 'An absolute path.')])),
                ('owner', models.CharField(default='root', max_length=64)),
                ('group', models.CharField(default='root', max_length=64)),
                ('mode', models.CharField(default='0755', max_length=4, validators=[django.core.validators.RegexValidator('^[0-7]{3,4}$', 'An octal file mode such as 0644 or 755.')])),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Host Directory',
                'verbose_name_plural': 'Host Directories',
                'ordering': ('device', 'virtual_machine', 'path'),
                'constraints': [models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostdirectory_one_host'), models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'path'), name='netbox_host_hostdirectory_unique_device'), models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'path'), name='netbox_host_hostdirectory_unique_vm')],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddConstraint(
            model_name='hostfile',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostfile_one_host'),
        ),
        migrations.AddConstraint(
            model_name='hostfile',
            constraint=models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'path'), name='netbox_host_hostfile_unique_device'),
        ),
        migrations.AddConstraint(
            model_name='hostfile',
            constraint=models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'path'), name='netbox_host_hostfile_unique_vm'),
        ),
        migrations.AddConstraint(
            model_name='hostfileentry',
            constraint=models.UniqueConstraint(fields=('file', 'position'), name='netbox_host_hostfileentry_unique_position'),
        ),
        migrations.AddConstraint(
            model_name='hostgroup',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostgroup_one_host'),
        ),
        migrations.AddConstraint(
            model_name='hostgroup',
            constraint=models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'name'), name='netbox_host_hostgroup_unique_device'),
        ),
        migrations.AddConstraint(
            model_name='hostgroup',
            constraint=models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'name'), name='netbox_host_hostgroup_unique_vm'),
        ),
        migrations.AddConstraint(
            model_name='hostpackage',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostpackage_one_host'),
        ),
        migrations.AddConstraint(
            model_name='hostpackage',
            constraint=models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'manager', 'name'), name='netbox_host_hostpackage_unique_device'),
        ),
        migrations.AddConstraint(
            model_name='hostpackage',
            constraint=models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'manager', 'name'), name='netbox_host_hostpackage_unique_vm'),
        ),
        migrations.AddConstraint(
            model_name='hostsymlink',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostsymlink_one_host'),
        ),
        migrations.AddConstraint(
            model_name='hostsymlink',
            constraint=models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'path'), name='netbox_host_hostsymlink_unique_device'),
        ),
        migrations.AddConstraint(
            model_name='hostsymlink',
            constraint=models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'path'), name='netbox_host_hostsymlink_unique_vm'),
        ),
        migrations.AddConstraint(
            model_name='hostsystemdunit',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostsystemdunit_one_host'),
        ),
        migrations.AddConstraint(
            model_name='hostsystemdunit',
            constraint=models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'name'), name='netbox_host_hostsystemdunit_unique_device'),
        ),
        migrations.AddConstraint(
            model_name='hostsystemdunit',
            constraint=models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'name'), name='netbox_host_hostsystemdunit_unique_vm'),
        ),
        migrations.AddConstraint(
            model_name='hostuser',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('device__isnull', False), ('virtual_machine__isnull', True)), models.Q(('device__isnull', True), ('virtual_machine__isnull', False)), _connector='OR'), name='netbox_host_hostuser_one_host'),
        ),
        migrations.AddConstraint(
            model_name='hostuser',
            constraint=models.UniqueConstraint(condition=models.Q(('device__isnull', False)), fields=('device', 'name'), name='netbox_host_hostuser_unique_device'),
        ),
        migrations.AddConstraint(
            model_name='hostuser',
            constraint=models.UniqueConstraint(condition=models.Q(('virtual_machine__isnull', False)), fields=('virtual_machine', 'name'), name='netbox_host_hostuser_unique_vm'),
        ),
    ]
