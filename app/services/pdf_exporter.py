# app/services/pdf_exporter.py

import io
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.extensions import mongo

logger = logging.getLogger(__name__)

class PdfExporter:
    """Service for exporting data to PDF reports"""
    
    def __init__(self):
        """Initialize PDF exporter"""
        self.styles = getSampleStyleSheet()
        
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='Section',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='Issue',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray
        ))
    
    def generate_compliance_report(self, document_id: str) -> bytes:
        """
        Generate a compliance report PDF for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            PDF file content as bytes
        """
        try:
            # Get document from database
            document = mongo.db.documents.find_one({"_id": document_id})
            if not document:
                raise ValueError(f"Document not found: {document_id}")
            
            # Set up PDF buffer
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Create content
            elements = []
            
            # Add header
            elements.append(Paragraph("Compliance Audit Report", self.styles['Title']))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add document info
            elements.append(Paragraph(f"Document: {document.get('filename', 'Unknown')}", self.styles['Subtitle']))
            elements.append(Paragraph(f"Document Type: {document.get('document_type', 'Unknown')}", self.styles['Normal']))
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add compliance score section
            elements.append(Paragraph("Compliance Score", self.styles['Section']))
            
            # Add compliance score visualization
            compliance_score = document.get('compliance_score', 0)
            elements.append(self._create_score_chart(compliance_score))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add compliance issues section
            elements.append(Paragraph("Compliance Issues", self.styles['Section']))
            
            # Get compliance issues
            issues = document.get('compliance_issues', [])
            
            if not issues:
                elements.append(Paragraph("No compliance issues were identified.", self.styles['Normal']))
            else:
                # Create issues table
                elements.append(self._create_issues_table(issues))
                elements.append(Spacer(1, 0.2 * inch))
                
                # Add detailed issues
                elements.append(PageBreak())
                elements.append(Paragraph("Detailed Issues", self.styles['Section']))
                
                for i, issue in enumerate(issues):
                    elements.append(Paragraph(f"Issue {i+1}: {issue.get('description', '')}", self.styles['Subtitle']))
                    elements.append(Paragraph(f"Severity: {issue.get('severity', 'medium').upper()}", self.styles['Normal']))
                    elements.append(Paragraph(f"Type: {issue.get('compliance_type', 'Unknown')}", self.styles['Normal']))
                    
                    # Add paragraph text if available
                    if 'paragraph_id' in issue:
                        for para in document.get('paragraphs', []):
                            if para.get('id') == issue['paragraph_id']:
                                elements.append(Paragraph("Relevant Text:", self.styles['Normal']))
                                elements.append(Paragraph(para.get('text', ''), self.styles['Issue']))
                                break
                    
                    # Add suggestions if available
                    if 'suggestions' in issue and issue['suggestions']:
                        elements.append(Paragraph("Suggestions:", self.styles['Normal']))
                        for suggestion in issue['suggestions']:
                            elements.append(Paragraph(suggestion, self.styles['Issue']))
                    
                    elements.append(Spacer(1, 0.2 * inch))
            
            # Build PDF
            doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            # Return PDF data
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise
    
    def _add_page_number(self, canvas, doc):
        """Add page number to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(inch, 0.5 * inch, f"Page {canvas.getPageNumber()}")
        canvas.drawString(doc.width - 2 * inch, 0.5 * inch, "Automated Document Compliance Auditor")
        canvas.restoreState()
    
    def _create_score_chart(self, score: float) -> Drawing:
        """Create a pie chart for compliance score"""
        drawing = Drawing(400, 150)
        
        # Create pie chart
        pie = Pie()
        pie.x = 150
        pie.y = 25
        pie.width = 100
        pie.height = 100
        pie.data = [score, 100 - score]
        pie.labels = None
        
        # Set colors based on score
        if score >= 80:
            color = colors.green
        elif score >= 60:
            color = colors.orange
        else:
            color = colors.red
        
        pie.slices[0].fillColor = color
        pie.slices[1].fillColor = colors.lightgrey
        
        drawing.add(pie)
        
        # Add score text
        from reportlab.graphics.shapes import String
        drawing.add(String(195, 75, f"{score}%", fontSize=20, fillColor=colors.black))
        
        return drawing
    
    def _create_issues_table(self, issues: List[Dict[str, Any]]) -> Table:
        """Create a table for compliance issues"""
        data = [['Issue', 'Severity', 'Type']]
        
        for issue in issues:
            row = [
                issue.get('description', 'Unknown issue'),
                issue.get('severity', 'medium').upper(),
                issue.get('compliance_type', 'Unknown')
            ]
            data.append(row)
        
        table = Table(data, colWidths=[3*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        return table

# Singleton instance
_exporter_instance = None

def get_pdf_exporter():
    """Get or create the PDF exporter singleton instance"""
    global _exporter_instance
    if _exporter_instance is None:
        _exporter_instance = PdfExporter()
    return _exporter_instance