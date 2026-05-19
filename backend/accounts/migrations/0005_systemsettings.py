from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_socialaccount'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=100, unique=True)),
                ('value', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'System Setting',
                'verbose_name_plural': 'System Settings',
                'ordering': ['key'],
            },
        ),
    ]
