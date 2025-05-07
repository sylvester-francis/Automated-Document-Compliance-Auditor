"""
PDF export utilities for generating compliance reports.
"""
import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from flask import current_app

def generate_compliance_pdf(document, compliance_results):
    """
    Generate a PDF compliance report for a document using ReportLab.
    
    Args:
        document: Document object with metadata
        compliance_results: Compliance check results
        
    Returns:
        Path to the generated PDF file
    """
    # Create a temporary file for the PDF
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"compliance_report_{timestamp}.pdf"
    output_path = os.path.join(temp_dir, filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray
    ))
    
    # Build the PDF content
    elements = []
    
    # Title
    elements.append(Paragraph(f"Compliance Report: {document.get('filename', 'Unknown')}", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Document Information
    elements.append(Paragraph("Document Information", styles['Heading2']))
    
    # Document metadata table
    metadata = [
        ["Filename", document.get('filename', 'Unknown')],
        ["Date Uploaded", document.get('created_at', datetime.now()).strftime('%Y-%m-%d %H:%M') if hasattr(document.get('created_at', datetime.now()), 'strftime') else 'Unknown'],
        ["Document Type", document.get('document_type', 'Unknown')]
    ]
    
    # Add any additional metadata
    if document.get('metadata'):
        for key, value in document.get('metadata', {}).items():
            metadata.append([key.title(), str(value)])
    
    # Create the metadata table
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Compliance Summary
    elements.append(Paragraph("Compliance Summary", styles['Heading2']))
    
    score = document.get('compliance_score', 0)
    score_color = colors.red
    if score >= 80:
        score_color = colors.green
    elif score >= 50:
        score_color = colors.orange
    
    score_style = ParagraphStyle(
        name='Score',
        parent=styles['Normal'],
        fontSize=14,
        textColor=score_color,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph(f"Compliance Score: {score}%", score_style))
    elements.append(Paragraph(f"Status: {document.get('compliance_status', 'pending_review').replace('_', ' ').title()}", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Compliance Issues
    elements.append(Paragraph("Compliance Issues", styles['Heading2']))
    
    issues = document.get('compliance_issues', [])
    if issues:
        for issue in issues:
            # Create a style based on severity
            severity = issue.get('severity', 'low').lower()
            severity_color = colors.green
            if severity == 'high':
                severity_color = colors.red
            elif severity == 'medium':
                severity_color = colors.orange
            
            issue_style = ParagraphStyle(
                name=f'Issue{severity.title()}',
                parent=styles['Normal'],
                fontSize=10,
                borderLeftColor=severity_color,
                borderLeftWidth=2,
                borderLeftPadding=5,
                leftIndent=10
            )
            
            elements.append(Paragraph(f"<b>{issue.get('title', 'Unknown Issue')}</b>", issue_style))
            elements.append(Paragraph(f"<b>Severity:</b> {severity.title()}", issue_style))
            elements.append(Paragraph(f"<b>Description:</b> {issue.get('description', 'No description')}", issue_style))
            
            if issue.get('recommendation'):
                elements.append(Paragraph(f"<b>Recommendation:</b> {issue.get('recommendation')}", issue_style))
            
            if issue.get('references'):
                elements.append(Paragraph(f"<b>References:</b> {issue.get('references')}", issue_style))
            
            elements.append(Spacer(1, 0.15*inch))
    else:
        elements.append(Paragraph("No compliance issues found.", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Automated Document Compliance Auditor", styles['Footer']))
    elements.append(Paragraph("This report is for informational purposes only and does not constitute legal advice.", styles['Footer']))
    
    # Build the PDF
    doc.build(elements)
    
    return output_path

def generate_document_pdf(document):
    """
    Generate a PDF version of a document with its content using ReportLab.
    
    Args:
        document: Document object with content
        
    Returns:
        Path to the generated PDF file
    """
    # Create a temporary file for the PDF
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"document_{timestamp}.pdf"
    output_path = os.path.join(temp_dir, filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Content',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray
    ))
    
    # Build the PDF content
    elements = []
    
    # Title
    elements.append(Paragraph(document.get('filename', 'Document Export'), styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Document Information
    elements.append(Paragraph("Document Information", styles['Heading2']))
    
    # Document metadata table
    metadata = [
        ["Filename", document.get('filename', 'Unknown')],
        ["Date Uploaded", document.get('created_at', datetime.now()).strftime('%Y-%m-%d %H:%M') if hasattr(document.get('created_at', datetime.now()), 'strftime') else 'Unknown'],
        ["Document Type", document.get('document_type', 'Unknown')]
    ]
    
    # Add compliance score if available
    if document.get('compliance_score') is not None:
        metadata.append(["Compliance Score", f"{document.get('compliance_score')}%"])
    
    # Add any additional metadata
    if document.get('metadata'):
        for key, value in document.get('metadata', {}).items():
            metadata.append([key.title(), str(value)])
    
    # Create the metadata table
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Document Content
    elements.append(Paragraph("Document Content", styles['Heading2']))
    
    # Add paragraphs if available, otherwise add full content
    if document.get('paragraphs') and len(document.get('paragraphs', [])) > 0:
        for paragraph in document.get('paragraphs', []):
            if paragraph and paragraph.strip():
                elements.append(Paragraph(paragraph, styles['Content']))
    elif document.get('content'):
        content = document.get('content', '')
        # Split content into manageable chunks to avoid ReportLab limitations
        max_length = 2000  # Maximum safe length for a paragraph
        for i in range(0, len(content), max_length):
            chunk = content[i:i+max_length]
            if chunk and chunk.strip():
                elements.append(Paragraph(chunk, styles['Content']))
    else:
        elements.append(Paragraph("No content available for this document.", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Automated Document Compliance Auditor", styles['Footer']))
    elements.append(Paragraph("This document export is for informational purposes only.", styles['Footer']))
    
    # Build the PDF
    doc.build(elements)
    
    return output_path
