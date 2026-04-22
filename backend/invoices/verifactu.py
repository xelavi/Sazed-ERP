"""
VeriFactu — Motor criptográfico, generador XML, cliente mock AEAT y PDF.

Cumple con:
  - RD 1007/2023 — Reglamento RRSIF / VERI*FACTU
  - ROF RD 1619/2012 — Reglamento Obligaciones de Facturación (Art. 6)
  - Ley 37/1992 (IVA)

Fases:
  2 — Hash SHA-256 encadenado
  3 — XML de alta RegistroAltaRegistroFacturacion
  4 — Mock servidor AEAT
  5 — PDF legal A4 con QR VERI*FACTU
"""
from __future__ import annotations

import hashlib
import io
import logging
from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from django.utils import timezone
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Identificacion del sistema (RRSIF art. 8.p)
SISTEMA_ID = 'ERP-TFG-VERIFACTU'
SISTEMA_VERSION = '1.0'
SISTEMA_PRODUCTOR_NIF = 'B00000000'
SISTEMA_PRODUCTOR_NOMBRE = 'TFG ERP System'


# ==============================================================================
# FASE 2 - Motor criptografico SHA-256 encadenado
# ==============================================================================

class VeriFactuHashService:
    """
    Calcula y encadena el hash SHA-256 conforme al RRSIF RD 1007/2023.
    Cadena: NIF_Emisor + Num_Factura + Fecha(DD-MM-YYYY) + Tipo + Importe + Hash_Anterior
    """

    @staticmethod
    def tipo_factura(invoice) -> str:
        return 'R1' if invoice.invoice_type == 'CreditNote' else 'F1'

    @staticmethod
    def _build_chain_string(nif_emisor, num_factura, fecha, tipo, importe_total, hash_anterior):
        return (
            nif_emisor
            + num_factura
            + fecha.strftime('%d-%m-%Y')
            + tipo
            + f'{importe_total:.2f}'
            + (hash_anterior or '')
        )

    @staticmethod
    def calculate(chain_str: str) -> str:
        return hashlib.sha256(chain_str.encode('utf-8')).hexdigest()

    @classmethod
    def get_previous_invoice(cls, invoice):
        from .models import Invoice
        company = invoice.series.company
        return (
            Invoice.objects
            .filter(series__company=company, hash_actual__gt='', fecha_generacion_registro__isnull=False)
            .exclude(pk=invoice.pk)
            .order_by('-fecha_generacion_registro')
            .first()
        )

    @classmethod
    def seal(cls, invoice) -> None:
        company = invoice.series.company
        nif_emisor = (company.tax_id or '') if company else ''
        prev = cls.get_previous_invoice(invoice)
        hash_anterior = prev.hash_actual if prev else ''
        tipo = cls.tipo_factura(invoice)
        chain = cls._build_chain_string(nif_emisor, invoice.number, invoice.issue_date, tipo, invoice.total_amount, hash_anterior)
        invoice.hash_anterior = hash_anterior
        invoice.hash_actual = cls.calculate(chain)
        invoice.tipo_factura_verifactu = tipo
        invoice.fecha_generacion_registro = timezone.now()
        invoice.estado_aeat = 'Pendiente'
        invoice.save(update_fields=['hash_anterior', 'hash_actual', 'tipo_factura_verifactu', 'fecha_generacion_registro', 'estado_aeat'])


# ==============================================================================
# FASE 3 - Generador XML (RegistroAltaRegistroFacturacion)
# ==============================================================================

class VeriFactuXmlGenerator:
    """
    Genera el XML de alta conforme al Anexo OM que desarrolla el RD 1007/2023.
    Incluye todos los campos obligatorios del art. 7-8 del RRSIF.
    """

    @staticmethod
    def _indent(xml_bytes: bytes) -> str:
        parsed = minidom.parseString(xml_bytes)
        return parsed.toprettyxml(indent='    ', encoding=None)

    @classmethod
    def generate(cls, invoice) -> str:
        company = invoice.series.company
        nif_emisor = (company.tax_id or 'DESCONOCIDO') if company else 'DESCONOCIDO'
        nombre_emisor = ((company.legal_name or company.name) if company else 'DESCONOCIDO')
        fecha_str = invoice.issue_date.strftime('%d-%m-%Y')

        root = Element('RegistroAltaRegistroFacturacion')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        # Cabecera
        cabecera = SubElement(root, 'Cabecera')
        obligado = SubElement(cabecera, 'ObligadoEmision')
        SubElement(obligado, 'NIF').text = nif_emisor
        SubElement(obligado, 'NombreRazonSocial').text = nombre_emisor
        sistema = SubElement(cabecera, 'SistemaInformatico')
        SubElement(sistema, 'NombreSistema').text = SISTEMA_ID
        SubElement(sistema, 'Version').text = SISTEMA_VERSION
        SubElement(sistema, 'NIF').text = SISTEMA_PRODUCTOR_NIF
        SubElement(sistema, 'NombreRazonSocial').text = SISTEMA_PRODUCTOR_NOMBRE

        # RegistroFacturacion
        reg = SubElement(root, 'RegistroFacturacion')

        id_fac = SubElement(reg, 'IDFactura')
        SubElement(id_fac, 'NumSerieFactura').text = invoice.number or ''
        SubElement(id_fac, 'FechaExpedicionFactura').text = fecha_str

        tipo_vf = invoice.tipo_factura_verifactu or 'F1'
        SubElement(reg, 'TipoFactura').text = tipo_vf

        # Rectificativa
        if tipo_vf == 'R1' and invoice.rectified_invoice:
            orig = invoice.rectified_invoice
            fact_rect = SubElement(reg, 'FacturasRectificadas')
            id_rect = SubElement(fact_rect, 'IDFacturaRectificada')
            SubElement(id_rect, 'NumSerieFactura').text = orig.number or ''
            SubElement(id_rect, 'FechaExpedicionFactura').text = orig.issue_date.strftime('%d-%m-%Y')
            SubElement(reg, 'TipoRectificativa').text = 'S'

        # Destinatario
        customer = invoice.customer
        if customer:
            destinatarios = SubElement(reg, 'Destinatarios')
            dest = SubElement(destinatarios, 'IDDestinatario')
            nif_dest = invoice.customer_vat_snapshot or getattr(customer, 'vat_id', '') or ''
            nombre_dest = invoice.customer_name_snapshot or getattr(customer, 'name', '') or ''
            if nif_dest:
                SubElement(dest, 'NIF').text = nif_dest
            SubElement(dest, 'NombreRazonSocial').text = nombre_dest

        # Descripcion operaciones
        lineas_desc = '; '.join(line.description[:80] for line in invoice.lines.all()[:3]) or 'Servicios/productos segun detalle'
        SubElement(reg, 'DescripcionOperaciones').text = lineas_desc[:250]

        # Desglose IVA
        desglose = SubElement(reg, 'Desglose')
        tax_groups = {}
        for line in invoice.lines.all():
            for lt in line.taxes.all():
                if not lt.is_retention:
                    key = str(lt.tax_percent)
                    tax_groups.setdefault(key, Decimal('0'))
                    tax_groups[key] += lt.tax_amount
        base_total = invoice.tax_base
        if not tax_groups:
            tax_groups['0.00'] = Decimal('0')
        items = list(tax_groups.items())
        for i, (percent, cuota) in enumerate(items):
            if len(items) == 1:
                base = base_total
            else:
                total_cuota = sum(v for v in tax_groups.values())
                base = (base_total * cuota / total_cuota).quantize(Decimal('0.01')) if total_cuota > 0 else Decimal('0')
            detalle = SubElement(desglose, 'DetalleDesglose')
            SubElement(detalle, 'TipoImpositivo').text = percent
            SubElement(detalle, 'BaseImponible').text = f'{base:.2f}'
            SubElement(detalle, 'CuotaRepercutida').text = f'{cuota:.2f}'
            if invoice.total_retention > 0:
                SubElement(detalle, 'CuotaRetenida').text = f'{invoice.total_retention:.2f}'

        SubElement(reg, 'ImporteTotal').text = f'{invoice.total_amount:.2f}'

        # Encadenamiento
        encadenamiento = SubElement(reg, 'Encadenamiento')
        if invoice.hash_anterior:
            prev = VeriFactuHashService.get_previous_invoice(invoice)
            reg_anterior = SubElement(encadenamiento, 'RegistroAnterior')
            SubElement(reg_anterior, 'NumSerieFacturaAnterior').text = (prev.number if prev else '')
            SubElement(reg_anterior, 'FechaExpedicionFacturaAnterior').text = (prev.issue_date.strftime('%d-%m-%Y') if prev else '')
            SubElement(reg_anterior, 'Huella').text = invoice.hash_anterior
        else:
            SubElement(encadenamiento, 'PrimerRegistro').text = 'S'

        SubElement(reg, 'Huella').text = invoice.hash_actual or ''

        if invoice.fecha_generacion_registro:
            ts = invoice.fecha_generacion_registro
            SubElement(reg, 'FechaHoraHusoGenRegistro').text = ts.strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'

        xml_bytes = tostring(root, encoding='unicode').encode('utf-8')
        return cls._indent(xml_bytes)


# ==============================================================================
# FASE 4 - Mock AEAT
# ==============================================================================

class MockAeatService:

    @staticmethod
    def validate_payload(xml_str: str) -> tuple:
        for field in ['<Huella>', '<ImporteTotal>', '<NIF>']:
            if field not in xml_str:
                return False, f'Falta campo obligatorio: {field}'
        return True, ''

    @classmethod
    def submit(cls, invoice) -> dict:
        from .models import EventLog
        xml_str = VeriFactuXmlGenerator.generate(invoice)
        ok, error_msg = cls.validate_payload(xml_str)
        if not ok:
            invoice.estado_aeat = 'Rechazado'
            invoice.save(update_fields=['estado_aeat'])
            EventLog.objects.create(invoice=invoice, accion='Rechazado_AEAT', detalles=f'Validacion fallida: {error_msg}')
            raise ValidationError(f'Mock AEAT rechazo el registro: {error_msg}')
        import uuid
        csv_mock = f'MOCK-CSV-{uuid.uuid4().hex[:9].upper()}'
        invoice.estado_aeat = 'Aceptado'
        invoice.verifactu_csv = csv_mock
        invoice.save(update_fields=['estado_aeat', 'verifactu_csv'])
        EventLog.objects.create(invoice=invoice, accion='Aceptado_AEAT', detalles=f'CSV: {csv_mock}')
        logger.info('VeriFactu mock AEAT acepto factura %s. CSV: %s', invoice.number, csv_mock)
        return {'estado': 'Aceptado', 'csv': csv_mock, 'mensaje': 'Registro procesado correctamente (Simulacion)', 'xml': xml_str}


# ==============================================================================
# FASE 5 - PDF legal A4 con QR VERI*FACTU
# ==============================================================================

def _build_qr_url(invoice) -> str:
    company = invoice.series.company
    nif = (company.tax_id or '') if company else ''
    num = invoice.number or ''
    fecha = invoice.issue_date.strftime('%d-%m-%Y')
    importe = f'{invoice.total_amount:.2f}'
    return (
        'https://www2.agenciatributaria.gob.es/wlpl/inwinv/es/zs/inv/verifFactura'
        f'?NIF={nif}&NUM={num}&FECHA={fecha}&IMPORTE={importe}'
    )


def generate_invoice_pdf(invoice) -> bytes:
    """
    Genera el PDF de la factura con todos los requisitos legales del ROF
    (RD 1619/2012, Art. 6) y el bloque VERI*FACTU con QR obligatorio.

    Campos obligatorios incluidos:
      - NIF y razon social del emisor + domicilio completo
      - NIF y razon social del destinatario + domicilio
      - Numero y serie de la factura
      - Fecha de expedicion
      - Descripcion de operaciones
      - Base imponible, tipo impositivo (IVA %), cuota tributaria
      - Importe total con divisa
      - En rectificativas: referencia a la factura original
      - Codigo QR VERI*FACTU + leyenda 'factura verificable'
      - Huella SHA-256 y CSV AEAT
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            BaseDocTemplate, Frame, PageTemplate,
            Table, TableStyle, Paragraph, Spacer,
            Image as RLImage, HRFlowable, KeepTogether,
        )
    except ImportError as exc:
        raise ImportError('pip install reportlab') from exc
    try:
        import qrcode
    except ImportError as exc:
        raise ImportError('pip install qrcode[pil]') from exc

    # Datos emisor
    company = invoice.series.company
    c_nombre = (company.legal_name or company.name) if company else 'Empresa'
    c_nif    = (company.tax_id or '') if company else ''
    c_dir    = (company.address or '') if company else ''
    c_ciudad = f'{company.postal_code or ""} {company.city or ""} ({company.province or ""})'.strip(' ()') if company else ''
    c_email  = (company.email or '') if company else ''
    c_tel    = (company.phone or '') if company else ''

    # Datos destinatario
    cust      = invoice.customer
    cust_nombre = invoice.customer_name_snapshot or getattr(cust, 'name', '') or ''
    cust_nif    = invoice.customer_vat_snapshot or getattr(cust, 'vat_id', '') or ''
    cust_dir    = getattr(cust, 'address', '') or ''
    cust_pc     = getattr(cust, 'postal_code', '') or ''
    cust_city   = getattr(cust, 'city', '') or ''
    cust_prov   = getattr(cust, 'province', '') or ''
    cust_ciudad = f'{cust_pc} {cust_city} ({cust_prov})'.strip(' ()')
    cust_email  = getattr(cust, 'email', '') or ''

    fecha_exp = invoice.issue_date.strftime('%d/%m/%Y')
    fecha_vto = invoice.due_date.strftime('%d/%m/%Y')
    is_rect   = invoice.tipo_factura_verifactu == 'R1'
    titulo    = 'FACTURA RECTIFICATIVA' if is_rect else 'FACTURA'
    numero    = invoice.number or 'BORRADOR'

    # QR
    qr_buf = None
    if invoice.hash_actual:
        qr_url = _build_qr_url(invoice)
        qr_img = qrcode.make(qr_url, border=2)
        qr_buf = io.BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_buf.seek(0)

    # Colores
    C_PRIMARY = colors.HexColor('#1a1a2e')
    C_ACCENT  = colors.HexColor('#667eea')
    C_LIGHT   = colors.HexColor('#f8f9fa')
    C_BORDER  = colors.HexColor('#dee2e6')
    C_GREY    = colors.HexColor('#6c757d')
    C_ORANGE  = colors.HexColor('#fd7e14')
    C_WHITE   = colors.white

    def ps(name, **kw):
        d = dict(fontName='Helvetica', fontSize=9, leading=12, textColor=C_PRIMARY, spaceAfter=0, spaceBefore=0)
        d.update(kw)
        return ParagraphStyle(name, **d)

    S = {
        'normal'      : ps('N'),
        'bold'        : ps('B', fontName='Helvetica-Bold'),
        'small'       : ps('S', fontSize=7.5, leading=10, textColor=C_GREY),
        'small_bold'  : ps('SB', fontSize=7.5, leading=10, fontName='Helvetica-Bold'),
        'tiny'        : ps('T', fontSize=6.5, leading=9, textColor=C_GREY),
        'title'       : ps('TT', fontName='Helvetica-Bold', fontSize=20, textColor=C_ACCENT, leading=24),
        'subtitle'    : ps('ST', fontName='Helvetica-Bold', fontSize=10),
        'sec_hdr'     : ps('SH', fontName='Helvetica-Bold', fontSize=8, textColor=C_WHITE, leading=11),
        'right'       : ps('R', alignment=TA_RIGHT),
        'center'      : ps('C', alignment=TA_CENTER),
        'center_small': ps('CS', fontSize=7, alignment=TA_CENTER, textColor=C_GREY),
        'total_l'     : ps('TL', fontName='Helvetica-Bold', fontSize=9, alignment=TA_RIGHT),
        'total_v'     : ps('TV', fontSize=9, alignment=TA_RIGHT),
        'grand_l'     : ps('GL', fontName='Helvetica-Bold', fontSize=11, textColor=C_WHITE, alignment=TA_RIGHT),
        'grand_v'     : ps('GV', fontName='Helvetica-Bold', fontSize=11, textColor=C_WHITE, alignment=TA_RIGHT),
        'vf_label'    : ps('VL', fontSize=7, fontName='Helvetica-Bold', textColor=C_ACCENT, alignment=TA_CENTER),
        'vf_text'     : ps('VT', fontSize=6, textColor=C_GREY, alignment=TA_CENTER, fontName='Courier', leading=8),
    }

    buf  = io.BytesIO()
    W, H = A4
    mh   = 18 * mm   # margin horizontal
    mv   = 15 * mm   # margin vertical top
    mb   = 18 * mm   # margin bottom
    PW   = W - 2 * mh  # ancho util

    elements = []

    # ---- Encabezado: emisor | factura ----
    emisor_lines = [Paragraph(c_nombre, S['bold'])]
    if c_nif:    emisor_lines.append(Paragraph(f'NIF: {c_nif}', S['small']))
    if c_dir:    emisor_lines.append(Paragraph(c_dir, S['small']))
    if c_ciudad: emisor_lines.append(Paragraph(c_ciudad, S['small']))
    if c_email:  emisor_lines.append(Paragraph(c_email, S['small']))
    if c_tel:    emisor_lines.append(Paragraph(c_tel, S['small']))

    fac_lines = [
        Paragraph(titulo, S['title']),
        Paragraph(f'N.° {numero}', S['subtitle']),
        Spacer(1, 2 * mm),
        Paragraph(f'Fecha de emisión: <b>{fecha_exp}</b>', S['small_bold']),
        Paragraph(f'Fecha de vencimiento: {fecha_vto}', S['small']),
    ]
    if invoice.payment_method:
        fac_lines.append(Paragraph(f'Forma de pago: {invoice.payment_method}', S['small']))

    hdr = Table([[emisor_lines, fac_lines]], colWidths=[PW * 0.52, PW * 0.48])
    hdr.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN',  (1,0), (1,0),   'RIGHT'),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
        ('RIGHTPADDING',  (0,0), (-1,-1), 0),
        ('TOPPADDING',    (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(hdr)
    elements.append(HRFlowable(width=PW, thickness=2, color=C_ACCENT, spaceAfter=4*mm, spaceBefore=3*mm))

    # ---- Emisor / Destinatario ----
    def party_block(titulo_bloque, nombre, nif, direccion, ciudad, email, col_w):
        rows = [[Paragraph(titulo_bloque.upper(), S['sec_hdr'])]]
        rows.append([Paragraph(nombre, S['bold'])])
        if nif:      rows.append([Paragraph(f'NIF/CIF: {nif}', S['small'])])
        if direccion: rows.append([Paragraph(direccion, S['small'])])
        if ciudad:   rows.append([Paragraph(ciudad, S['small'])])
        if email:    rows.append([Paragraph(email, S['small'])])
        t = Table(rows, colWidths=[col_w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), C_ACCENT),
            ('BOX',        (0,0), (-1,-1), 0.5, C_BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
            ('TOPPADDING',    (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        return t

    col_party = PW * 0.48
    parties = Table(
        [[party_block('Emisor', c_nombre, c_nif, c_dir, c_ciudad, c_email, col_party),
          Spacer(4*mm, 1),
          party_block('Destinatario', cust_nombre, cust_nif, cust_dir, cust_ciudad, cust_email, col_party)]],
        colWidths=[col_party, 4*mm, col_party],
    )
    parties.setStyle(TableStyle([
        ('VALIGN',         (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',    (0,0), (-1,-1), 0),
        ('RIGHTPADDING',   (0,0), (-1,-1), 0),
        ('TOPPADDING',     (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 0),
    ]))
    elements.append(parties)
    elements.append(Spacer(1, 4*mm))

    # ---- Aviso rectificativa ----
    if is_rect and invoice.rectified_invoice:
        orig = invoice.rectified_invoice
        rt = Table([[
            Paragraph('FACTURA RECTIFICATIVA', S['small_bold']),
            Paragraph(f'Rectifica la factura: <b>{orig.number}</b> de fecha {orig.issue_date.strftime("%d/%m/%Y")}', S['small']),
        ]], colWidths=[PW * 0.3, PW * 0.7])
        rt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff3cd')),
            ('BOX',        (0,0), (-1,-1), 0.5, colors.HexColor('#ffc107')),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(rt)
        elements.append(Spacer(1, 3*mm))

    # ---- Lineas de factura ----
    col_w = [PW*0.40, PW*0.09, PW*0.13, PW*0.09, PW*0.11, PW*0.18]
    line_rows = [[
        Paragraph('DESCRIPCION', S['sec_hdr']),
        Paragraph('CANT.', S['sec_hdr']),
        Paragraph('P.UNIT.', S['sec_hdr']),
        Paragraph('DTO.', S['sec_hdr']),
        Paragraph('IVA', S['sec_hdr']),
        Paragraph('SUBTOTAL', S['sec_hdr']),
    ]]
    for line in invoice.lines.all():
        iva_pct = ''
        for lt in line.taxes.all():
            if not lt.is_retention:
                iva_pct = f'{lt.tax_percent:.0f}%'
                break
        dto_txt = '—'
        if line.discount_type and line.discount_value:
            dto_txt = f'{line.discount_value:.1f}%' if line.discount_type == 'percent' else f'{line.discount_value:.2f} €'
        line_rows.append([
            Paragraph(line.description, S['normal']),
            Paragraph(f'{line.quantity:.2f}', S['right']),
            Paragraph(f'{line.unit_price:.2f} €', S['right']),
            Paragraph(dto_txt, S['center']),
            Paragraph(iva_pct, S['center']),
            Paragraph(f'{line.subtotal:.2f} €', S['right']),
        ])

    lt = Table(line_rows, colWidths=col_w)
    lt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), C_ACCENT),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_WHITE, C_LIGHT]),
        ('GRID',          (0,0), (-1,-1), 0.3, C_BORDER),
        ('LINEBELOW',     (0,0), (-1,0), 1, C_ACCENT),
        ('LEFTPADDING',   (0,0), (-1,-1), 5),
        ('RIGHTPADDING',  (0,0), (-1,-1), 5),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('FONTSIZE',      (0,0), (-1,-1), 8.5),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(lt)
    elements.append(Spacer(1, 3*mm))

    # ---- Notas + Totales ----
    notes_rows = []
    if invoice.customer_notes:
        notes_rows += [[Paragraph('Observaciones:', S['small_bold'])], [Paragraph(invoice.customer_notes, S['small'])]]
    if invoice.payment_method:
        notes_rows += [[Paragraph('Forma de pago:', S['small_bold'])], [Paragraph(invoice.payment_method, S['small'])]]

    notes_t = Table(notes_rows or [[Paragraph('', S['small'])]], colWidths=[PW * 0.52])
    notes_t.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1)]))

    # Filas de totales
    tot_rows = []
    tot_rows.append([Paragraph('Base imponible:', S['total_l']), Paragraph(f'{invoice.tax_base:.2f} €', S['total_v'])])
    shown_iva = {}
    for line in invoice.lines.all():
        for lt_item in line.taxes.all():
            if not lt_item.is_retention:
                k = str(lt_item.tax_percent)
                shown_iva.setdefault(k, Decimal('0'))
                shown_iva[k] += lt_item.tax_amount
    if not shown_iva:
        shown_iva = {'0.00': Decimal('0')}
    for pct, cuota in shown_iva.items():
        tot_rows.append([Paragraph(f'IVA ({pct}%):', S['total_l']), Paragraph(f'{cuota:.2f} €', S['total_v'])])
    if invoice.total_retention > 0:
        tot_rows.append([Paragraph('Retención (-IRPF):', S['total_l']), Paragraph(f'-{invoice.total_retention:.2f} €', S['total_v'])])
    if invoice.discount_amount > 0:
        tot_rows.append([Paragraph('Descuento global:', S['total_l']), Paragraph(f'-{invoice.discount_amount:.2f} €', S['total_v'])])
    tot_rows.append([Paragraph('TOTAL A PAGAR:', S['grand_l']), Paragraph(f'{invoice.total_amount:.2f} {invoice.currency}', S['grand_v'])])

    tot_t = Table(tot_rows, colWidths=[PW * 0.27, PW * 0.21])
    last = len(tot_rows) - 1
    tot_t.setStyle(TableStyle([
        ('ALIGN',        (0,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE',     (0,0), (-1,-1), 8.5),
        ('TOPPADDING',   (0,0), (-1,-1), 2),
        ('BOTTOMPADDING',(0,0), (-1,-1), 2),
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('LINEABOVE',    (0,last), (-1,last), 1.5, C_ACCENT),
        ('BACKGROUND',   (0,last), (-1,last), C_ACCENT),
        ('BOX',          (0,0), (-1,last-1), 0.3, C_BORDER),
    ]))

    bottom = Table([[notes_t, '', tot_t]], colWidths=[PW*0.52, PW*0.02, PW*0.46])
    bottom.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    elements.append(bottom)
    elements.append(Spacer(1, 5*mm))
    elements.append(HRFlowable(width=PW, thickness=0.5, color=C_BORDER, spaceAfter=3*mm))

    # ---- Bloque VERI*FACTU ----
    if invoice.hash_actual:
        qr_image = RLImage(qr_buf, width=28*mm, height=28*mm)
        qr_url_text = _build_qr_url(invoice)
        vf_info = [
            Paragraph('VERI*FACTU — Factura verificable en la AEAT', S['vf_label']),
            Spacer(1, 1*mm),
            Paragraph('Factura verificable en la sede electrónica de la AEAT — VERI*FACTU', S['center_small']),
            Spacer(1, 1*mm),
            Paragraph(f'Huella SHA-256: {invoice.hash_actual}', S['vf_text']),
        ]
        if invoice.verifactu_csv:
            vf_info.append(Paragraph(f'CSV AEAT: {invoice.verifactu_csv}', S['vf_text']))
        if invoice.fecha_generacion_registro:
            ts_str = invoice.fecha_generacion_registro.strftime('%d/%m/%Y %H:%M:%S')
            vf_info.append(Paragraph(f'Fecha de sellado: {ts_str}', S['vf_text']))
        vf_info.append(Paragraph(f'URL verificación: {qr_url_text}', S['vf_text']))

        vf_t = Table([[qr_image, vf_info]], colWidths=[32*mm, PW - 32*mm])
        vf_t.setStyle(TableStyle([
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
            ('BOX',            (0,0), (-1,-1), 0.8, C_ACCENT),
            ('BACKGROUND',     (0,0), (-1,-1), colors.HexColor('#f0f4ff')),
            ('LEFTPADDING',    (0,0), (-1,-1), 4),
            ('RIGHTPADDING',   (0,0), (-1,-1), 4),
            ('TOPPADDING',     (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 4),
        ]))
        elements.append(KeepTogether(vf_t))
    else:
        elements.append(Paragraph(
            'BORRADOR — Esta factura no ha sido aprobada ni registrada en la AEAT.',
            ParagraphStyle('Draft', fontName='Helvetica-Bold', fontSize=9, textColor=C_ORANGE, alignment=TA_CENTER),
        ))

    # ---- Construir el PDF ----
    def _on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(C_GREY)
        canvas.drawRightString(W - mh, 8*mm, f'Pagina {doc.page}')
        canvas.drawString(mh, 8*mm, f'{numero} | {c_nombre} | NIF: {c_nif}')
        canvas.restoreState()

    doc = BaseDocTemplate(buf, pagesize=A4, rightMargin=mh, leftMargin=mh, topMargin=mv, bottomMargin=mb)
    frame = Frame(mh, mb, W - 2*mh, H - mv - mb, id='main')
    template = PageTemplate(id='main', frames=[frame], onPage=_on_page)
    doc.addPageTemplates([template])
    doc.build(elements)
    return buf.getvalue()
