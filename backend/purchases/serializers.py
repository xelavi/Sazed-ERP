from rest_framework import serializers

from core.tax_utils import apply_line_vat
from providers.serializers import ProviderListSerializer
from .models import (
    PurchaseInvoice, PurchaseInvoiceLine,
    PurchaseInvoiceLineTax, PurchasePayment, PurchaseInvoiceTimeline,
    PurchaseQuoteDoc, PurchaseQuoteDocLine, PurchaseQuoteDocLineTax,
    RecurringPurchaseInvoice,
)


class PurchaseInvoiceLineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoiceLineTax
        fields = [
            'id', 'tax_rate', 'tax_name', 'tax_percent',
            'is_retention', 'tax_amount',
        ]


class PurchaseInvoiceLineSerializer(serializers.ModelSerializer):
    taxes = PurchaseInvoiceLineTaxSerializer(many=True, read_only=True)
    tax_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        allow_null=True, write_only=True,
    )

    class Meta:
        model = PurchaseInvoiceLine
        fields = [
            'id', 'position', 'product', 'description',
            'quantity', 'unit_price', 'discount_type',
            'discount_value', 'discount_amount', 'subtotal',
            'taxes', 'tax_percent',
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
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'invoice_type', 'status', 'number',
            'provider', 'provider_name',
            'provider_vat_id', 'provider_avatar_color', 'provider_initials',
            'issue_date', 'due_date', 'payment_method',
            'subtotal', 'total_tax', 'total_amount',
            'paid_amount', 'balance_due', 'is_overdue',
            'created_at',
        ]


class PurchaseInvoiceDetailSerializer(serializers.ModelSerializer):
    provider_data = ProviderListSerializer(source='provider', read_only=True)
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
            'id', 'invoice_type', 'company', 'provider',
            'issue_date', 'due_date', 'payment_method', 'currency',
            'discount_type', 'discount_value',
            'provider_notes', 'internal_notes',
            'created_by', 'updated_by', 'lines',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        if self.instance and self.instance.status != 'Draft':
            raise serializers.ValidationError(
                'Només es poden editar factures en estat esborrany.',
            )
        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        invoice = PurchaseInvoice.objects.create(**validated_data)

        company = invoice.company
        for line_data in lines_data:
            taxes_data = line_data.pop('taxes', [])
            tax_percent = line_data.pop('tax_percent', None)
            line = PurchaseInvoiceLine.objects.create(invoice=invoice, **line_data)
            for tax_data in taxes_data:
                PurchaseInvoiceLineTax.objects.create(invoice_line=line, **tax_data)
            if not taxes_data:
                apply_line_vat(PurchaseInvoiceLineTax, line, tax_percent, company)

        if lines_data:
            invoice.recalculate_totals()

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='created',
            action='Factura de compra creada com a esborrany',
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
            company = instance.company
            instance.lines.all().delete()
            for line_data in lines_data:
                taxes_data = line_data.pop('taxes', [])
                tax_percent = line_data.pop('tax_percent', None)
                line = PurchaseInvoiceLine.objects.create(
                    invoice=instance, **line_data,
                )
                for tax_data in taxes_data:
                    PurchaseInvoiceLineTax.objects.create(
                        invoice_line=line, **tax_data,
                    )
                if not taxes_data:
                    apply_line_vat(PurchaseInvoiceLineTax, line, tax_percent, company)
            instance.recalculate_totals()

        return instance


class RecurringPurchaseInvoiceSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(
        source='template.provider.name', read_only=True,
    )
    template_total = serializers.DecimalField(
        source='template.total_amount', max_digits=12, decimal_places=2,
        read_only=True,
    )
    frequency_display = serializers.CharField(
        source='get_frequency_display', read_only=True,
    )
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = RecurringPurchaseInvoice
        fields = [
            'id', 'template', 'provider_name', 'template_total',
            'frequency', 'frequency_display', 'interval', 'payment_term_days',
            'start_date', 'next_run', 'end_date', 'max_occurrences',
            'occurrences', 'last_run', 'active', 'is_finished',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'template', 'next_run', 'occurrences', 'last_run',
            'created_at', 'updated_at',
        ]


class RecurringPurchaseInvoiceCreateSerializer(serializers.Serializer):
    source_invoice = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseInvoice.objects.all(),
    )
    frequency = serializers.ChoiceField(
        choices=RecurringPurchaseInvoice.RecurrenceFrequency.choices,
    )
    interval = serializers.IntegerField(min_value=1, default=1)
    payment_term_days = serializers.IntegerField(min_value=0, default=30)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    max_occurrences = serializers.IntegerField(
        min_value=1, required=False, allow_null=True,
    )


# ---------- Purchase Quote serializers ----------

class PurchaseQuoteDocLineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseQuoteDocLineTax
        fields = [
            'id', 'tax_rate', 'tax_name', 'tax_percent',
            'is_retention', 'tax_amount',
        ]


class PurchaseQuoteDocLineSerializer(serializers.ModelSerializer):
    taxes = PurchaseQuoteDocLineTaxSerializer(many=True, read_only=True)
    tax_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        allow_null=True, write_only=True,
    )

    class Meta:
        model = PurchaseQuoteDocLine
        fields = [
            'id', 'position', 'product', 'description',
            'quantity', 'unit_price', 'subtotal',
            'taxes', 'tax_percent',
        ]
        read_only_fields = ['id', 'subtotal']


class PurchaseQuoteDocListSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_avatar_color = serializers.CharField(
        source='provider.avatar_color', read_only=True,
    )
    provider_initials = serializers.CharField(
        source='provider.initials', read_only=True,
    )
    converted_invoice_number = serializers.CharField(
        source='converted_invoice.number', read_only=True, default=None,
    )

    class Meta:
        model = PurchaseQuoteDoc
        fields = [
            'id', 'name', 'status', 'provider', 'provider_name',
            'provider_avatar_color', 'provider_initials',
            'issue_date', 'valid_until', 'currency',
            'subtotal', 'total_tax', 'total_amount',
            'converted_invoice', 'converted_invoice_number',
            'created_at',
        ]


class PurchaseQuoteDocDetailSerializer(serializers.ModelSerializer):
    provider_data = ProviderListSerializer(source='provider', read_only=True)
    lines = PurchaseQuoteDocLineSerializer(many=True, read_only=True)
    converted_invoice_number = serializers.CharField(
        source='converted_invoice.number', read_only=True, default=None,
    )

    class Meta:
        model = PurchaseQuoteDoc
        fields = '__all__'


class PurchaseQuoteDocWriteSerializer(serializers.ModelSerializer):
    lines = PurchaseQuoteDocLineSerializer(many=True, required=False)

    class Meta:
        model = PurchaseQuoteDoc
        fields = [
            'id', 'name', 'provider', 'issue_date', 'valid_until',
            'currency', 'status', 'provider_notes', 'internal_notes',
            'created_by', 'lines',
        ]
        read_only_fields = ['id']

    def _save_lines(self, quote, lines_data):
        company = quote.company
        for line_data in lines_data:
            taxes_data = line_data.pop('taxes', [])
            tax_percent = line_data.pop('tax_percent', None)
            line = PurchaseQuoteDocLine.objects.create(quote=quote, **line_data)
            for tax_data in taxes_data:
                PurchaseQuoteDocLineTax.objects.create(quote_line=line, **tax_data)
            if not taxes_data:
                apply_line_vat(PurchaseQuoteDocLineTax, line, tax_percent, company,
                               line_fk_name='quote_line')

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        quote = PurchaseQuoteDoc.objects.create(**validated_data)
        self._save_lines(quote, lines_data)
        if lines_data:
            quote.recalculate_totals()
        return quote

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines_data is not None:
            instance.lines.all().delete()
            self._save_lines(instance, lines_data)
            instance.recalculate_totals()
        return instance
