from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from django.http import HttpResponse
from io import BytesIO
import os
from django.conf import settings

class ContratoPDFGenerator:
    def __init__(self, contrato):
        self.contrato = contrato
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Estilos personalizados
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            textColor=colors.black
        )
        
        self.clause_style = ParagraphStyle(
            'ClauseStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            textColor=colors.black
        )

    def add_header(self):
        """Agrega el encabezado con logo y título"""
        # Logo
        logo_path = os.path.join(settings.MEDIA_ROOT, 'logo', 'Logotipo.jpg')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=2*inch)
                logo.hAlign = 'CENTER'
                self.story.append(logo)
                self.story.append(Spacer(1, 20))
            except:
                pass  # Si hay error con la imagen, continuar sin logo
        
        # Título
        title = Paragraph("CONTRATO MUSICAL", self.title_style)
        self.story.append(title)
        
        subtitle = Paragraph("GRUPO MUSICAL<br/>BAHIA MIX", self.subtitle_style)
        self.story.append(subtitle)
        
        self.story.append(Spacer(1, 30))

    def add_contract_info(self):
        """Agrega la información básica del contrato"""
        # Fecha y lugar
        lugar_text = f"<b>Piura</b> de <b>{self.contrato.fecha_evento.strftime('%B %Y')}</b>"
        lugar_para = Paragraph(lugar_text, self.normal_style)
        self.story.append(lugar_para)
        
        self.story.append(Spacer(1, 20))
        
        # Información del contratante
        cliente_nombre = self.contrato.cliente.nombre_cliente if self.contrato.cliente else "_" * 30
        intro_text = (
            f"El Señor <b>Oscar Zarco Solano</b>, identificado con DNI <b>41648976</b> "
            f"Representante del grupo <b>BAHIA MIX</b> y el contratante <b>Señor(a) {cliente_nombre}</b> "
            f"interesado en contratar el grupo, tiene a bien realizar un contrato musical, "
            f"el contratante solicita los servicios musicales por <b>{self.contrato.tiempo_total or 5} horas</b> "
            f"y de conformidad se aceptan las siguientes cláusulas:"
        )
        intro_para = Paragraph(intro_text, self.normal_style)
        self.story.append(intro_para)
        
        self.story.append(Spacer(1, 20))

    def add_clauses(self):
        """Agrega las cláusulas del contrato"""
        clauses = [
            f"<b>1.-</b> El contratante el día <b>{self.contrato.fecha_evento.strftime('%d')}</b> del mes de <b>{self.contrato.fecha_evento.strftime('%B')}</b> del grupo <b>BAHIA MIX</b> para el día <b>{self.contrato.fecha_evento.strftime('%d')}</b> a partir de las <b>{self.contrato.hora_inicio.strftime('%H:%M')}</b> y finalizando a las <b>{self.contrato.hora_final.strftime('%H:%M')}</b> siendo la cantidad comprometida de <b>{self.contrato.pago_total}</b> soles.",
            
            f"<b>2.-</b> El contratante anticipa la cantidad de <b>{self.contrato.pago_adelanto or 0}</b> quedando a cuenta, <b>{self.contrato.pago_restante or 0}</b> cantidad que se hará efectiva antes de iniciar el festejo.",
            
            "<b>3.-</b> El contrato no podrá transferirse de fecha, en caso de suspensión del servicio, por cualquier causa contratante deberá pagar el 50% de la cantidad contratada como compensación.",
            
            "<b>4.-</b> El domicilio donde se efectuará el evento será en:",
            
            "<b>5.-</b> El contratante se compromete a proporcionar un lugar suficiente amplio para la ejecución del trabajo del grupo, corriente para que en caso de lluvia quede cubierto el equipo, además de proporcionar el suministro de energía eléctrica necesaria y suficiente para el buen funcionamiento de los equipos.",
            
            "<b>6.-</b> En caso de que el lugar del evento, posea otra orquesta, se suspende el evento si el contratante se compromete el pago del 100% de lo pactado.",
            
            "<b>7.-</b> En caso de diferir con otro grupo musical, tendrá prioridad el que haya contratado primero y respetando dicho tiempo y se ejecutará el horario de inicio y final de dicho contrato.",
            
            "<b>8.-</b> El grupo BAHIA MIX se compromete a realizar su trabajo en el horario y fecha establecidos en este contrato y en los términos expresados anteriormente.",
            
            "Leídas las cláusulas anteriores se firma en conformidad"
        ]
        
        for clause in clauses:
            clause_para = Paragraph(clause, self.clause_style)
            self.story.append(clause_para)
            self.story.append(Spacer(1, 8))

    def add_signatures(self):
        """Agrega la sección de firmas"""
        self.story.append(Spacer(1, 40))
        
        # Tabla de firmas
        signature_data = [
            ['CRISTHIAN FRANK ICARNAQUE LUJAN.', 'CONTRATANTE'],
            ['', ''],
            ['Representante del grupo bahía mix', 'Nombre:'],
            ['', 'DNI:']
        ]
        
        signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),
            ('LINEABOVE', (1, 0), (1, 0), 1, colors.black),
        ]))
        
        self.story.append(signature_table)

    def add_contact_info(self):
        """Agrega información de contacto"""
        self.story.append(Spacer(1, 30))
        
        contact_text = (
            "<b>Grupo musical Bahía Mix</b><br/>"
            "📱 928 267 419"
        )
        contact_para = Paragraph(contact_text, self.normal_style)
        self.story.append(contact_para)

    def generate_pdf(self):
        """Genera el PDF completo"""
        self.add_header()
        self.add_contract_info()
        self.add_clauses()
        self.add_signatures()
        self.add_contact_info()
        
        # Construir el documento
        self.doc.build(self.story)
        
        # Preparar respuesta HTTP
        self.buffer.seek(0)
        response = HttpResponse(
            self.buffer.getvalue(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="Contrato_{self.contrato.numero_contrato}.pdf"'
        
        return response


def generar_contrato_pdf_reportlab(contrato):
    """Función helper para generar PDF usando ReportLab"""
    generator = ContratoPDFGenerator(contrato)
    return generator.generate_pdf()