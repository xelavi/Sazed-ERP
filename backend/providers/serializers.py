from rest_framework import serializers

from core.models import Tag
from core.serializers import TagSerializer
from customers.models import Customer, CustomerNote, CustomerActivity
from customers.serializers import CustomerNoteSerializer, CustomerActivitySerializer


class ProviderListSerializer(serializers.ModelSerializer):
    linked = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_type', 'email', 'city', 'status',
            'vat_id', 'avatar_color', 'initials', 'linked',
            'created_at', 'updated_at',
        ]

    def get_linked(self, obj):
        return list(obj.linked_contacts.values_list('name', flat=True))


class ProviderDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=Tag.objects.all(), required=False,
    )
    linked = serializers.SerializerMethodField()
    linked_contact_ids = serializers.PrimaryKeyRelatedField(
        source='linked_contacts', many=True, write_only=True,
        queryset=Customer.objects.filter(is_supplier=True), required=False,
    )
    notes = CustomerNoteSerializer(many=True, read_only=True)
    activities = CustomerActivitySerializer(many=True, read_only=True)
    purchase_invoices_count = serializers.SerializerMethodField()

    total_purchased = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )
    pending_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_type', 'email', 'phone', 'website',
            'status', 'vat_id', 'legal_name',
            'address', 'city', 'province', 'postal_code', 'country',
            'payment_method', 'bank_account',
            'avatar_color', 'initials', 'internal_notes',
            'tags', 'tag_ids', 'linked', 'linked_contact_ids',
            'notes', 'activities', 'purchase_invoices_count',
            'total_purchased', 'pending_balance',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_linked(self, obj):
        return list(obj.linked_contacts.values_list('name', flat=True))

    def get_purchase_invoices_count(self, obj):
        return obj.purchase_invoices.filter(is_template=False).count()


class ProviderWriteSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=Tag.objects.all(), required=False,
    )
    linked_contact_ids = serializers.PrimaryKeyRelatedField(
        source='linked_contacts', many=True, write_only=True,
        queryset=Customer.objects.filter(is_supplier=True), required=False,
    )

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_type', 'email', 'phone', 'website',
            'status', 'vat_id', 'legal_name',
            'address', 'city', 'province', 'postal_code', 'country',
            'payment_method', 'bank_account',
            'avatar_color', 'initials', 'internal_notes',
            'tag_ids', 'linked_contact_ids',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        linked = validated_data.pop('linked_contacts', [])
        validated_data['is_supplier'] = True
        validated_data.setdefault('is_customer', False)
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
