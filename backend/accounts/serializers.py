"""
Serializers for accounts app.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import (
    User, Company, Membership, Notification, Message, Invitation,
    Role, MODULE_KEYS, PERMISSION_LEVELS, normalize_permissions,
)


# ── Auth ───────────────────────────────────────────────


class RegisterSerializer(serializers.Serializer):
    """Register a new user. Company creation is optional (handled separately via onboarding)."""

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, default='')
    company_name = serializers.CharField(max_length=200, required=False, default='')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ya existe una cuenta con este email.')
        return value.lower()

    def create(self, validated_data):
        company_name = validated_data.pop('company_name', '').strip()
        password = validated_data.pop('password')

        # Create user
        user = User.objects.create_user(
            password=password, **validated_data,
        )

        # Optionally create first company
        if company_name:
            from django.utils.text import slugify
            slug = slugify(company_name)
            base_slug = slug
            counter = 1
            while Company.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            company = Company.objects.create(
                name=company_name,
                slug=slug,
                created_by=user,
            )

            Membership.objects.create(
                user=user,
                company=company,
                role='owner',
                is_default=True,
            )

            # Create default warehouse
            from core.models import Warehouse
            Warehouse.objects.create(
                company=company,
                name='Main Warehouse',
                address='',
            )

            # Create default invoice series
            from invoices.models import InvoiceSeries
            InvoiceSeries.objects.create(
                company=company,
                name='Facturas generales',
                prefix='FAC',
                pattern='{PREFIX}-{YEAR}-{SEQ:4}',
                is_default=True,
            )

        return user


class LoginSerializer(serializers.Serializer):
    """Validate email + password and return user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data['email'].lower(),
            password=data['password'],
        )
        if not user:
            raise serializers.ValidationError('Credenciales incorrectas.')
        if not user.is_active:
            raise serializers.ValidationError('Cuenta desactivada.')
        data['user'] = user
        return data


# ── User ───────────────────────────────────────────────


class UserSerializer(serializers.ModelSerializer):
    """Public user profile."""

    full_name = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'full_name', 'initials', 'avatar', 'date_joined', 'is_staff',
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'is_staff']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update own profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']


class ChangePasswordSerializer(serializers.Serializer):
    """Change own password."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta.')
        return value


# ── Company ────────────────────────────────────────────


class CompanySerializer(serializers.ModelSerializer):
    """Full company detail."""

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'tax_id', 'legal_name',
            'email', 'phone', 'website',
            'address', 'city', 'province', 'postal_code', 'country',
            'logo', 'primary_color',
            'plan', 'currency', 'fiscal_year_start', 'invoice_prefix',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'plan', 'created_at', 'updated_at']


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Create a new company (adds user as owner)."""

    class Meta:
        model = Company
        fields = ['id', 'name', 'tax_id', 'legal_name', 'email', 'currency']
        read_only_fields = ['id']

    def create(self, validated_data):
        from django.utils.text import slugify
        user = self.context['request'].user

        slug = slugify(validated_data['name'])
        base_slug = slug
        counter = 1
        while Company.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        company = Company.objects.create(slug=slug, created_by=user, **validated_data)
        Membership.objects.create(
            user=user,
            company=company,
            role='owner',
            is_default=False,
        )

        # Create default warehouse
        from core.models import Warehouse
        Warehouse.objects.create(
            company=company,
            name='Main Warehouse',
            address='',
        )

        # Create default invoice series
        from invoices.models import InvoiceSeries
        InvoiceSeries.objects.create(
            company=company,
            name='Facturas generales',
            prefix='FAC',
            pattern='{PREFIX}-{YEAR}-{SEQ:4}',
            is_default=True,
        )

        # Encolar provisioning automático de BD Odoo (~2 min en background).
        # Lo procesa el management command `process_odoo_provisioning`.
        try:
            from accounting_sync.provisioning_service import enqueue_for_company
            enqueue_for_company(company)
        except Exception:  # noqa: BLE001
            # Nunca bloqueamos la creación de Company por un fallo de provisioning.
            import logging
            logging.getLogger(__name__).exception(
                'No se pudo encolar el provisioning Odoo para company=%s', company.pk,
            )

        return company


# ── Membership ─────────────────────────────────────────


class RoleSerializer(serializers.ModelSerializer):
    """Read/write a company-defined role with its permission matrix."""

    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'permissions', 'members_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_members_count(self, obj):
        return obj.memberships.count()

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El nombre es obligatorio.')
        return value

    def validate_permissions(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Formato de permisos no válido.')
        for key, level in value.items():
            if key not in MODULE_KEYS:
                raise serializers.ValidationError(f'Módulo desconocido: {key}')
            if level not in PERMISSION_LEVELS:
                raise serializers.ValidationError(
                    f'Nivel de permiso no válido: {level}',
                )
        return normalize_permissions(value)


class MembershipSerializer(serializers.ModelSerializer):
    """Read membership with user details."""

    user = UserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)
    role_label = serializers.ReadOnlyField()
    permissions = serializers.ReadOnlyField(source='effective_permissions')

    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'company', 'company_name', 'company_slug',
            'role', 'role_label', 'custom_role', 'permissions',
            'is_default', 'joined_at',
        ]
        read_only_fields = ['id', 'user', 'company', 'joined_at']


class InviteMemberSerializer(serializers.Serializer):
    """Invite a user to a company by email."""

    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=Membership.Role.choices, default='editor',
    )
    custom_role = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        return value.lower()


class SwitchCompanySerializer(serializers.Serializer):
    """Switch the user's active/default company."""

    company_id = serializers.IntegerField()

    def validate_company_id(self, value):
        user = self.context['request'].user
        if not Membership.objects.filter(user=user, company_id=value).exists():
            raise serializers.ValidationError('No perteneces a esta empresa.')
        return value


# ── Inbox: user lookup ─────────────────────────────────


class UserLiteSerializer(serializers.ModelSerializer):
    """Minimal user info for search results / message previews."""

    full_name = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'initials', 'avatar']


# ── Inbox: Notifications ───────────────────────────────


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'kind', 'title', 'body', 'link', 'read', 'created_at']
        read_only_fields = fields


# ── Inbox: Messages ────────────────────────────────────


class MessageSerializer(serializers.ModelSerializer):
    sender = UserLiteSerializer(read_only=True)
    recipient = UserLiteSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'company',
            'subject', 'body', 'parent', 'read', 'created_at',
        ]
        read_only_fields = fields


class MessageCreateSerializer(serializers.ModelSerializer):
    recipient_id = serializers.IntegerField(write_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Message
        fields = ['recipient_id', 'subject', 'body', 'parent']

    def validate(self, attrs):
        request = self.context['request']
        sender = request.user

        # When replying, inherit the company from the parent message so the
        # reply lands in the same company regardless of the user's active company.
        parent = attrs.get('parent')
        if parent:
            company_id = parent.company_id
        else:
            company_id = request.headers.get('X-Company') or request.META.get('HTTP_X_COMPANY')

        if not company_id:
            raise serializers.ValidationError('Falta el contexto de empresa.')

        # Sender must belong to company
        if not Membership.objects.filter(user=sender, company_id=company_id).exists():
            raise serializers.ValidationError('No perteneces a esta empresa.')

        recipient_id = attrs['recipient_id']
        if recipient_id == sender.id:
            raise serializers.ValidationError('No puedes enviarte un mensaje a ti mismo.')

        # Recipient must belong to the same company
        if not Membership.objects.filter(
            user_id=recipient_id, company_id=company_id,
        ).exists():
            raise serializers.ValidationError(
                'El destinatario no pertenece a esta empresa.',
            )

        attrs['_sender'] = sender
        attrs['_company_id'] = int(company_id)
        return attrs

    def create(self, validated_data):
        sender = validated_data.pop('_sender')
        company_id = validated_data.pop('_company_id')
        recipient_id = validated_data.pop('recipient_id')

        return Message.objects.create(
            sender=sender,
            recipient_id=recipient_id,
            company_id=company_id,
            subject=validated_data['subject'],
            body=validated_data['body'],
            parent=validated_data.get('parent'),
        )


# ── Inbox: Invitations ─────────────────────────────────


class InvitationSerializer(serializers.ModelSerializer):
    inviter = UserLiteSerializer(read_only=True)
    invitee = UserLiteSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.SerializerMethodField()
    role_label = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            'id', 'company', 'company_name', 'company_logo',
            'inviter', 'invitee', 'role', 'custom_role', 'role_label',
            'status', 'created_at', 'responded_at',
        ]
        read_only_fields = fields

    def get_company_logo(self, obj):
        if obj.company.logo:
            return obj.company.logo.url
        return None

    def get_role_label(self, obj):
        if obj.custom_role_id:
            return obj.custom_role.name
        return obj.get_role_display()


class InvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=Membership.Role.choices, default='editor',
    )
    custom_role = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        return value.lower()
