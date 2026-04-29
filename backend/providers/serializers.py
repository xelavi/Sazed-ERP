from rest_framework import serializers

from core.models import Tag
from core.serializers import TagSerializer
from .models import Provider, ProviderNote, ProviderActivity, PurchaseOrder

try:
    from purchases.models import PurchaseQuote
except ImportError:
    PurchaseQuote = None


class ProviderNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderNote
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProviderActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderActivity
        fields = ['id', 'activity_type', 'date', 'subject', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'number', 'concept', 'total_amount', 'balance_due',
            'date', 'notes', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProviderListSerializer(serializers.ModelSerializer):

    linked = serializers.SerializerMethodField()

    class Meta:
        model = Provider
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
        queryset=Tag.objects.all(),
        required=False,
    )
    linked = serializers.SerializerMethodField()
    linked_contact_ids = serializers.PrimaryKeyRelatedField(
        source='linked_contacts', many=True, write_only=True,
        queryset=Provider.objects.all(), required=False,
    )
    notes = ProviderNoteSerializer(many=True, read_only=True)
    activities = ProviderActivitySerializer(many=True, read_only=True)
    purchase_orders = PurchaseOrderSerializer(many=True, read_only=True)
    purchase_invoices_count = serializers.SerializerMethodField()

    total_purchased = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )
    pending_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )
    total_documents = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'contact_type', 'email', 'phone', 'website',
            'status', 'vat_id', 'legal_name',
            'address', 'city', 'province', 'postal_code', 'country',
            'payment_method', 'bank_account',
            'avatar_color', 'initials', 'internal_notes',
            'tags', 'tag_ids', 'linked', 'linked_contact_ids',
            'notes', 'activities', 'purchase_orders', 'purchase_invoices_count',
            'total_purchased', 'pending_balance', 'total_documents',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_linked(self, obj):
        return list(obj.linked_contacts.values_list('name', flat=True))

    def get_purchase_invoices_count(self, obj):
        if hasattr(obj, 'purchase_invoices'):
            return obj.purchase_invoices.count()
        return 0


class ProviderWriteSerializer(serializers.ModelSerializer):

    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=Tag.objects.all(),
        required=False,
    )
    linked_contact_ids = serializers.PrimaryKeyRelatedField(
        source='linked_contacts', many=True, write_only=True,
        queryset=Provider.objects.all(), required=False,
    )

    class Meta:
        model = Provider
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
        provider = Provider.objects.create(**validated_data)
        if tags:
            provider.tags.set(tags)
        if linked:
            provider.linked_contacts.set(linked)
        return provider

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
