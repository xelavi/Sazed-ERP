from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('system', 'Sistema'), ('alert', 'Aviso'), ('activity', 'Actividad')], default='system', max_length=10)),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField(blank=True)),
                ('link', models.CharField(blank=True, default='', max_length=300)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='messages', to='accounts.company')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='replies', to='accounts.message')),
                ('recipient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'Propietario'), ('admin', 'Administrador'), ('editor', 'Editor'), ('viewer', 'Solo lectura')], default='editor', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('accepted', 'Aceptada'), ('rejected', 'Rechazada')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='invitations', to='accounts.company')),
                ('inviter', models.ForeignKey(null=True, on_delete=models.deletion.SET_NULL, related_name='sent_company_invitations', to=settings.AUTH_USER_MODEL)),
                ('invitee', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='received_invitations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='invitation',
            constraint=models.UniqueConstraint(
                condition=models.Q(('status', 'pending')),
                fields=('company', 'invitee'),
                name='unique_pending_invitation',
            ),
        ),
    ]
