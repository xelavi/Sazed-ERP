from rest_framework import serializers

from providers.serializers import ProviderListSerializer
from .models import (
    PurchaseSeries, PurchaseInvoice, PurchaseInvoiceLine,
    PurchaseInvoiceLineTax, PurchasePayment, PurchaseInvoiceTimeline,
    PurchaseQuote,
)


class PurchaseSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSeries
        fields = [
            'id', 'name', 'prefix', 'pattern',
            'next_seq', 'reset_yearly', 'is_default', 'active',
            'created_at',
        ]


class PurchaseInvoiceLineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoiceLineTax
        fields = [
            'id', 'tax_rate', 'tax_name', 'tax_percent',
            'is_retention', 'tax_amount',
        ]


class PurchaseInvoiceLineSerializer(serializers.ModelSerializer):
    taxes = PurchaseInvoiceLineTaxSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseInvoiceLine
        fields = [
            'id', 'position', 'product', 'description',
            'quantity', 'unit_price', 'discount_type',
            'discount_value', 'discount_amount', 'subtotal', 'taxes',
        ]
        read_only_fields = ['id', 'discount_amount', 'subtotal']


class PurchasePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePayment
        fields = [
            'id', 'date', 'amount', 'method',
            'reference', 'notes', 'created_by', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PurchaseInvoiceTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoiceTimeline
        fields = ['id', 'event_type', 'action', 'actor', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']


class PurchaseQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseQuote
        fields = [
            'id', 'number', 'concept', 'amount',
            'date', 'valid_days', 'notes', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseInvoiceListSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(
        source='provider.name', read_only=True,
    )
    provider_vat_id = serializers.CharField(
        source='provider.vat_id', read_only=True,
    )
    provider_avatar_color = serializers.CharField(
        source='provider.avatar_color', read_only=True,
    )
    provider_initials = serializers.CharField(
        source='provider.initials', read_only=True,
    )
    series_prefix = serializers.CharField(
        source='series.prefix', read_only=True,
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'invoice_type', 'status', 'number',
            'series_prefix', 'provider', 'provider_name',
            'provider_vat_id', 'provider_avatar_color', 'provider_initials',
            'issue_date', 'due_date', 'payment_method',
            'subtotal', 'total_tax', 'total_amount',
            'paid_amount', 'balance_due', 'is_overdue',
            'created_at',
        ]


class PurchaseInvoiceDetailSerializer(serializers.ModelSerializer):
    provider_data = ProviderListSerializer(source='provider', read_only=True)
    series_data = PurchaseSeriesSerializer(source='series', read_only=True)
    lines = PurchaseInvoiceLineSerializer(many=True, read_only=True)
    payments = PurchasePaymentSerializer(many=True, read_only=True)
    timeline = PurchaseInvoiceTimelineSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = '__all__'


class PurchaseInvoiceWriteSerializer(serializers.ModelSerializer):
    lines = PurchaseInvoiceLineSerializer(many=True, required=False)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'invoice_type', 'series', 'provider',
            'issue_date', 'due_date', 'payment_method', 'currency',
            'discount_type', 'discount_value',
            'provider_notes', 'internal_notes',
            'created_by', 'updated_by', 'lines',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        if self.instance and self.instance.status != 'Draft':
            raise serializers.ValidationError(
                'Solo se pueden editar facturas en estado borrador.',
            )
        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        invoice = PurchaseInvoice.objects.create(**validated_data)

        for line_data in lines_data:
            taxes_data = line_data.pop('taxes', [])
            line = PurchaseInvoiceLine.objects.create(invoice=invoice, **line_data)
            for tax_data in taxes_data:
                PurchaseInvoiceLineTax.objects.create(invoice_line=line, **tax_data)

        if lines_data:
            invoice.recalculate_totals()

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='created',
            action='Factura de compra creada como borrador',
            actor=validated_data.get('created_by', 'System'),
            date=invoice.issue_date,
        )

        return invoice

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                taxes_data = line_data.pop('taxes', [])
                line = PurchaseInvoiceLine.objects.create(
                    invoice=instance, **line_data,
                )
                for tax_data in taxes_data:
                    PurchaseInvoiceLineTax.objects.create(
                        invoice_line=line, **tax_data,
                    )
            instance.recalculate_totals()

        return instance
