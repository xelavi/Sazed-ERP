from django.conf import settings
from django.db import migrations, models

import accounting_sync.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0005_systemsettings'),
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OdooConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('base_url', models.URLField(default='http://localhost:8069')),
                ('database', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=200)),
                ('password', accounting_sync.fields.EncryptedTextField()),
                ('is_active', models.BooleanField(default=True)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('last_sync_status', models.CharField(
                    choices=[('ok', 'OK'), ('error', 'Error'), ('never', 'Nunca ejecutada')],
                    default='never', max_length=10,
                )),
                ('last_sync_error', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.OneToOneField(
                    on_delete=models.deletion.CASCADE,
                    related_name='odoo_connection',
                    to='accounts.company',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=models.deletion.SET_NULL,
                    related_name='odoo_connections_created',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Conexión Odoo',
                'verbose_name_plural': 'Conexiones Odoo',
            },
        ),
        migrations.CreateModel(
            name='OdooTaxMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('direction', models.CharField(
                    choices=[('sale', 'Venta'), ('purchase', 'Compra')], max_length=10,
                )),
                ('odoo_tax_id', models.PositiveIntegerField()),
                ('odoo_tax_name', models.CharField(blank=True, default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='odoo_tax_mappings',
                    to='accounts.company',
                )),
                ('tax_rate', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='odoo_mappings',
                    to='core.taxrate',
                )),
            ],
            options={
                'verbose_name': 'Mapeo de impuesto Odoo',
                'verbose_name_plural': 'Mapeos de impuestos Odoo',
            },
        ),
        migrations.AddConstraint(
            model_name='odootaxmapping',
            constraint=models.UniqueConstraint(
                fields=('company', 'tax_rate', 'direction'),
                name='unique_tax_mapping_per_company_direction',
            ),
        ),
        migrations.CreateModel(
            name='SyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('entity_type', models.CharField(max_length=50)),
                ('entity_id', models.CharField(blank=True, default='', max_length=64)),
                ('odoo_id', models.PositiveIntegerField(blank=True, null=True)),
                ('operation', models.CharField(
                    choices=[('PUSH', 'Push (ERP → Odoo)'), ('PULL', 'Pull (Odoo → ERP)')],
                    max_length=10,
                )),
                ('odoo_method', models.CharField(max_length=50)),
                ('success', models.BooleanField(default=False)),
                ('request_payload_hash', models.CharField(blank=True, default='', max_length=64)),
                ('response_excerpt', models.TextField(blank=True, default='')),
                ('error_message', models.TextField(blank=True, default='')),
                ('duration_ms', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='odoo_sync_logs',
                    to='accounts.company',
                )),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=models.deletion.SET_NULL,
                    related_name='odoo_sync_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Log de sincronización Odoo',
                'verbose_name_plural': 'Logs de sincronización Odoo',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(
                        fields=['company', 'entity_type', '-created_at'],
                        name='synclog_co_entity_created_idx',
                    ),
                ],
            },
        ),
    ]
