from rest_framework import serializers

from core.tax_utils import apply_line_vat
from customers.serializers import CustomerListSerializer
from .models import (
    InvoiceSeries, Invoice, InvoiceLine,
    InvoiceLineTax, Payment, InvoiceTimeline, EventLog,
    Quote, QuoteLine, QuoteLineTax, RecurringInvoice,
)


class InvoiceSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceSeries
        fields = [
            'id', 'name', 'prefix', 'pattern',
            'next_seq', 'reset_yearly', 'is_default', 'active',
            'created_at',
        ]


class InvoiceLineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineTax
        fields = [
            'id', 'tax_rate', 'tax_name', 'tax_percent',
            'is_retention', 'tax_amount',
        ]


class InvoiceLineSerializer(serializers.ModelSerializer):
    taxes = InvoiceLineTaxSerializer(many=True, read_only=True)
    # Porcentaje de IVA editado en el frontend. Se traduce a un InvoiceLineTax
    # al guardar (write-only, no es un campo del modelo).
    tax_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        allow_null=True, write_only=True,
    )

    class Meta:
        model = InvoiceLine
        fields = [
            'id', 'position', 'product', 'description',
            'quantity', 'unit_price', 'discount_type',
            'discount_value', 'discount_amount', 'subtotal',
            'taxes', 'tax_percent',
        ]
        read_only_fields = ['id', 'discount_amount', 'subtotal']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'date', 'amount', 'method',
            'reference', 'notes', 'created_by', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class InvoiceTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceTimeline
        fields = ['id', 'event_type', 'action', 'actor', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------- Invoice serializers ----------

class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer para la tabla/listado de facturas."""

    customer_name = serializers.CharField(
        source='customer.name', read_only=True,
    )
    customer_vat_id = serializers.CharField(
        source='customer.vat_id', read_only=True,
    )
    customer_avatar_color = serializers.CharField(
        source='customer.avatar_color', read_only=True,
    )
    customer_initials = serializers.CharField(
        source='customer.initials', read_only=True,
    )
    series_prefix = serializers.CharField(
        source='series.prefix', read_only=True,
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_type', 'status', 'number',
            'series_prefix', 'customer', 'customer_name',
            'customer_vat_id', 'customer_avatar_color', 'customer_initials',
            'issue_date', 'due_date', 'payment_method',
            'subtotal', 'total_tax', 'total_amount',
            'paid_amount', 'balance_due', 'is_overdue',
            # VeriFactu
            'tipo_factura_verifactu', 'estado_aeat', 'hash_actual',
            'created_at',
        ]


class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = ['id', 'accion', 'usuario', 'ip', 'fecha_hora', 'detalles']
        read_only_fields = fields


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer para el detalle completo de una factura."""

    customer_data = CustomerListSerializer(source='customer', read_only=True)
    series_data = InvoiceSeriesSerializer(source='series', read_only=True)
    lines = InvoiceLineSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    timeline = InvoiceTimelineSerializer(many=True, read_only=True)
    event_logs = EventLogSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar facturas borrador."""

    lines = InvoiceLineSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_type', 'series', 'customer',
            'issue_date', 'due_date', 'payment_method', 'currency',
            'discount_type', 'discount_value',
            'customer_notes', 'internal_notes',
            'created_by', 'updated_by', 'lines',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """Impedir edición de facturas no borrador."""
        if self.instance and self.instance.status != 'Draft':
            raise serializers.ValidationError(
                'Solo se pueden editar facturas en estado borrador.',
            )
        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        invoice = Invoice.objects.create(**validated_data)
        company = getattr(invoice, 'company', None)

        for line_data in lines_data:
            taxes_data = line_data.pop('taxes', [])
            tax_percent = line_data.pop('tax_percent', None)
            line = InvoiceLine.objects.create(invoice=invoice, **line_data)
            for tax_data in taxes_data:
                InvoiceLineTax.objects.create(invoice_line=line, **tax_data)
            if not taxes_data:
                apply_line_vat(InvoiceLineTax, line, tax_percent, company)

        if lines_data:
            invoice.recalculate_totals()

        # Timeline entry
        InvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='created',
            action='Factura creada como borrador',
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
            # Replace all lines
            company = getattr(instance, 'company', None)
            instance.lines.all().delete()
            for line_data in lines_data:
                taxes_data = line_data.pop('taxes', [])
                tax_percent = line_data.pop('tax_percent', None)
                line = InvoiceLine.objects.create(
                    invoice=instance, **line_data,
                )
                for tax_data in taxes_data:
                    InvoiceLineTax.objects.create(
                        invoice_line=line, **tax_data,
                    )
                if not taxes_data:
                    apply_line_vat(InvoiceLineTax, line, tax_percent, company)
            instance.recalculate_totals()

        return instance


# ---------- Quote (Sales) serializers ----------

class QuoteLineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteLineTax
        fields = [
            'id', 'tax_rate', 'tax_name', 'tax_percent',
            'is_retention', 'tax_amount',
        ]


class QuoteLineSerializer(serializers.ModelSerializer):
    taxes = QuoteLineTaxSerializer(many=True, read_only=True)
    tax_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        allow_null=True, write_only=True,
    )

    class Meta:
        model = QuoteLine
        fields = [
            'id', 'position', 'product', 'description',
            'quantity', 'unit_price', 'subtotal',
            'taxes', 'tax_percent',
        ]
        read_only_fields = ['id', 'subtotal']


class QuoteListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_avatar_color = serializers.CharField(
        source='customer.avatar_color', read_only=True,
    )
    customer_initials = serializers.CharField(
        source='customer.initials', read_only=True,
    )
    converted_invoice_number = serializers.CharField(
        source='converted_invoice.number', read_only=True, default=None,
    )

    class Meta:
        model = Quote
        fields = [
            'id', 'name', 'status', 'customer', 'customer_name',
            'customer_avatar_color', 'customer_initials',
            'issue_date', 'valid_until', 'currency',
            'subtotal', 'total_tax', 'total_amount',
            'converted_invoice', 'converted_invoice_number',
            'created_at',
        ]


class QuoteDetailSerializer(serializers.ModelSerializer):
    customer_data = CustomerListSerializer(source='customer', read_only=True)
    lines = QuoteLineSerializer(many=True, read_only=True)
    converted_invoice_number = serializers.CharField(
        source='converted_invoice.number', read_only=True, default=None,
    )

    class Meta:
        model = Quote
        fields = '__all__'


class RecurringInvoiceSerializer(serializers.ModelSerializer):
    """Lectura de un plan de recurrencia de venta."""

    customer_name = serializers.CharField(
        source='template.customer.name', read_only=True,
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
        model = RecurringInvoice
        fields = [
            'id', 'template', 'customer_name', 'template_total',
            'frequency', 'frequency_display', 'interval', 'payment_term_days',
            'start_date', 'next_run', 'end_date', 'max_occurrences',
            'occurrences', 'last_run', 'active', 'is_finished',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'template', 'next_run', 'occurrences', 'last_run',
            'created_at', 'updated_at',
        ]


class RecurringInvoiceCreateSerializer(serializers.Serializer):
    """Crea un plan a partir de una factura existente."""

    source_invoice = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all(),
    )
    frequency = serializers.ChoiceField(
        choices=RecurringInvoice.RecurrenceFrequency.choices,
    )
    interval = serializers.IntegerField(min_value=1, default=1)
    payment_term_days = serializers.IntegerField(min_value=0, default=30)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    max_occurrences = serializers.IntegerField(
        min_value=1, required=False, allow_null=True,
    )


class QuoteWriteSerializer(serializers.ModelSerializer):
    lines = QuoteLineSerializer(many=True, required=False)

    class Meta:
        model = Quote
        fields = [
            'id', 'name', 'customer', 'issue_date', 'valid_until',
            'currency', 'status', 'customer_notes', 'internal_notes',
            'created_by', 'lines',
        ]
        read_only_fields = ['id']

    def _save_lines(self, quote, lines_data):
        company = quote.company
        for line_data in lines_data:
            taxes_data = line_data.pop('taxes', [])
            tax_percent = line_data.pop('tax_percent', None)
            line = QuoteLine.objects.create(quote=quote, **line_data)
            for tax_data in taxes_data:
                QuoteLineTax.objects.create(quote_line=line, **tax_data)
            if not taxes_data:
                apply_line_vat(QuoteLineTax, line, tax_percent, company,
                               line_fk_name='quote_line')

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        quote = Quote.objects.create(**validated_data)
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
