"""
Serializers for accounts app.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User, Company, Membership


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
            'id', 'email', 'first_name', 'last_name',
            'full_name', 'initials', 'avatar', 'date_joined',
        ]
        read_only_fields = ['id', 'email', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update own profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar']


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
        fields = ['name', 'tax_id', 'legal_name', 'email', 'currency']

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

        return company


# ── Membership ─────────────────────────────────────────


class MembershipSerializer(serializers.ModelSerializer):
    """Read membership with user details."""

    user = UserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'company', 'company_name', 'company_slug',
            'role', 'is_default', 'joined_at',
        ]
        read_only_fields = ['id', 'user', 'company', 'joined_at']


class InviteMemberSerializer(serializers.Serializer):
    """Invite a user to a company by email."""

    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=Membership.Role.choices, default='editor',
    )

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
