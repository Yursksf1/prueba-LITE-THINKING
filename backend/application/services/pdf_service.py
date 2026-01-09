"""
PDF Generation Service for inventory reports.

This service handles the generation of PDF documents for inventory data,
separating the PDF generation logic from the HTTP layer.
"""
from io import BytesIO
from datetime import datetime
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFGeneratorService:
    """
    Service for generating PDF documents for inventory reports.
    
    This service is designed to be reusable and independent of the HTTP layer,
    allowing it to be used for both download and email sending scenarios.
    """
    
    def __init__(self, page_size=A4):
        """
        Initialize the PDF generator.
        
        Args:
            page_size: Page size for the PDF (default: A4)
        """
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        
    def generate_inventory_pdf(
        self, 
        inventory_items: List[dict],
        company_name: Optional[str] = None,
        company_nit: Optional[str] = None
    ) -> BytesIO:
        """
        Generate a PDF report for inventory items.
        
        Args:
            inventory_items: List of inventory items with product and quantity info
            company_name: Optional company name for the report header
            company_nit: Optional company NIT for the report header
            
        Returns:
            BytesIO: PDF document in memory
            
        Example:
            >>> items = [
            ...     {
            ...         'product_code': 'PROD001',
            ...         'product_name': 'Laptop HP',
            ...         'quantity': 50,
            ...         'prices': {'USD': 1000.00, 'COP': 4000000.00}
            ...     }
            ... ]
            >>> pdf_service = PDFGeneratorService()
            >>> pdf_buffer = pdf_service.generate_inventory_pdf(
            ...     items, 
            ...     company_name='Acme Corp',
            ...     company_nit='123456789'
            ... )
        """
        # Create a BytesIO buffer to hold the PDF in memory
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Build the document content
        elements = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        title = Paragraph("Reporte de Inventario", title_style)
        elements.append(title)
        
        # Add company information if provided
        if company_name or company_nit:
            company_style = ParagraphStyle(
                'CompanyInfo',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#2d3748'),
                spaceAfter=10,
                alignment=TA_CENTER
            )
            
            if company_name:
                company_para = Paragraph(f"<b>Empresa:</b> {company_name}", company_style)
                elements.append(company_para)
            
            if company_nit:
                nit_para = Paragraph(f"<b>NIT:</b> {company_nit}", company_style)
                elements.append(nit_para)
        
        # Add generation date
        date_style = ParagraphStyle(
            'DateInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        date_para = Paragraph(f"<b>Fecha de generación:</b> {date_str}", date_style)
        elements.append(date_para)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Create the inventory table
        if inventory_items:
            # Table headers
            table_data = [['Código', 'Nombre', 'Cantidad', 'Precios']]
            
            # Add inventory data
            for item in inventory_items:
                # Format prices
                prices = item.get('prices', {})
                if isinstance(prices, dict) and prices:
                    price_strs = []
                    for k, v in prices.items():
                        try:
                            price_strs.append(f"{k}: ${float(v):,.2f}")
                        except (ValueError, TypeError):
                            price_strs.append(f"{k}: {v}")
                    price_str = ', '.join(price_strs)
                else:
                    price_str = 'N/A'
                table_data.append([
                    str(item.get('product_code', 'N/A')),
                    str(item.get('product_name', 'N/A')),
                    str(item.get('quantity', 0)),
                    price_str
                ])
            
            # Create table
            table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 2*inch])
            
            # Apply table styling
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Body styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Quantity column centered
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#718096')),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ]))
            
            elements.append(table)
        else:
            # No inventory items
            no_data_style = ParagraphStyle(
                'NoData',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#e53e3e'),
                alignment=TA_CENTER
            )
            no_data = Paragraph("No hay productos en el inventario.", no_data_style)
            elements.append(no_data)
        
        # Add footer with total count
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_LEFT
        )
        total_items = len(inventory_items)
        total_quantity = sum(item.get('quantity', 0) for item in inventory_items)
        footer = Paragraph(
            f"<b>Total de productos:</b> {total_items} | <b>Cantidad total:</b> {total_quantity}",
            footer_style
        )
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Reset buffer position to beginning
        buffer.seek(0)
        
        return buffer
