from rest_framework import serializers

from core.models import Tag
from core.serializers import TagSerializer
from .models import Customer, CustomerNote, CustomerActivity, Quote


class CustomerNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNote
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class CustomerActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerActivity
        fields = ['id', 'activity_type', 'date', 'subject', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = [
            'id', 'number', 'concept', 'amount', 'date',
            'valid_days', 'notes', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerListSerializer(serializers.ModelSerializer):
    """Serializer para la tabla/listado de clientes."""

    linked = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_type', 'email', 'city', 'status',
            'vat_id', 'avatar_color', 'initials', 'linked',
            'is_customer', 'is_supplier', 'created_at', 'updated_at',
        ]

    def get_linked(self, obj):
        return list(obj.linked_contacts.values_list('name', flat=True))


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Serializer para el detalle completo de un cliente."""

    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=Tag.objects.all(),
        required=False,
    )
    linked = serializers.SerializerMethodField()
    linked_contact_ids = serializers.PrimaryKeyRelatedField(
        source='linked_contacts', many=True, write_only=True,
        queryset=Customer.objects.all(), required=False,
    )
    notes = CustomerNoteSerializer(many=True, read_only=True)
    activities = CustomerActivitySerializer(many=True, read_only=True)
    quotes = QuoteSerializer(many=True, read_only=True)

    # Campos calculados
    total_invoiced = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )
    pending_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )
    total_documents = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_type', 'email', 'phone', 'website',
            'status', 'vat_id', 'legal_name',
            'address', 'city', 'province', 'postal_code', 'country',
            'payment_method', 'bank_account', 'is_customer', 'is_supplier',
            'avatar_color', 'initials', 'internal_notes',
            'tags', 'tag_ids', 'linked', 'linked_contact_ids',
            'notes', 'activities', 'quotes',
            'total_invoiced', 'pending_balance', 'total_documents',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_linked(self, obj):
        return list(obj.linked_contacts.values_list('name', flat=True))


class CustomerWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar clientes."""

    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=Tag.objects.all(),
        required=False,
    )
    linked_contact_ids = serializers.PrimaryKeyRelatedField(
        source='linked_contacts', many=True, write_only=True,
        queryset=Customer.objects.all(), required=False,
    )

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_type', 'email', 'phone', 'website',
            'status', 'vat_id', 'legal_name',
            'address', 'city', 'province', 'postal_code', 'country',
            'payment_method', 'bank_account', 'is_customer', 'is_supplier',
            'avatar_color', 'initials', 'internal_notes',
            'tag_ids', 'linked_contact_ids',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        linked = validated_data.pop('linked_contacts', [])
        customer = Customer.objects.create(**validated_data)
        if tags:
            customer.tags.set(tags)
        if linked:
            customer.linked_contacts.set(linked)
        return customer

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        linked = validated_data.pop('linked_contacts', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if linked is not None:
            instance.linked_contacts.set(linked)
        return instance
