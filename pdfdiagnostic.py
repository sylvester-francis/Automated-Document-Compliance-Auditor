#!/usr/bin/env python
# PDF Generation Diagnostic Tool

import io
import os
import sys
import logging
import traceback
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('pdf_diagnostic')

def check_reportlab_installation():
    """Check if ReportLab is properly installed"""
    try:
        import reportlab
        logger.info(f"ReportLab version: {reportlab.Version}")
        return True
    except ImportError:
        logger.error("ReportLab is not installed. Install it using: pip install reportlab")
        return False

def check_dependencies():
    """Check required dependencies for ReportLab"""
    dependencies = {
        'PIL': 'pillow',
        'freetype': 'reportlab',
        'renderPM': 'reportlab'
    }
    
    results = {}
    
    # Check Pillow/PIL
    try:
        import PIL
        results['PIL'] = f"Installed: {PIL.__version__}"
    except ImportError:
        results['PIL'] = "Not installed"
    
    # Check renderPM (part of reportlab)
    try:
        from reportlab.graphics import renderPM
        results['renderPM'] = "Installed"
    except ImportError:
        results['renderPM'] = "Not installed - C extensions may be missing"
    
    return results

def test_basic_pdf_generation():
    """Try to generate a simple PDF to verify basic functionality"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a PDF in memory
        buffer = io.BytesIO()
        
        # Create the PDF object
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content
        pdf.drawString(100, 750, "Test PDF Generation")
        pdf.drawString(100, 730, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save the PDF
        pdf.showPage()
        pdf.save()
        
        # Get the value from the buffer
        pdf_value = buffer.getvalue()
        
        # Check if PDF was generated
        if pdf_value.startswith(b'%PDF-'):
            pdf_size = len(pdf_value)
            logger.info(f"Basic PDF generation successful. Size: {pdf_size} bytes")
            
            # Save the test file for inspection
            with open('test_basic.pdf', 'wb') as f:
                f.write(pdf_value)
            
            return True, pdf_size
        else:
            logger.error("Generated file doesn't appear to be a valid PDF")
            return False, 0
        
    except Exception as e:
        logger.error(f"Error generating basic PDF: {str(e)}")
        traceback.print_exc()
        return False, 0

def test_complex_pdf_generation():
    """Try to generate a more complex PDF with tables, styles and images"""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        
        # Create a PDF in memory
        buffer = io.BytesIO()
        
        # Create the PDF object
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Add a title
        elements.append(Paragraph("Complex PDF Test", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Add some paragraphs
        elements.append(Paragraph("This is a paragraph in normal style.", styles['Normal']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("This is a paragraph in heading1 style.", styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        # Create a table
        data = [
            ['Col 1', 'Col 2', 'Col 3'],
            ['Row 1', '1,1', '1,2'],
            ['Row 2', '2,1', '2,2'],
            ['Row 3', '3,1', '3,2']
        ]
        
        table = Table(data)
        
        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        # Build the PDF
        doc.build(elements)
        
        # Get the value from the buffer
        pdf_value = buffer.getvalue()
        
        # Check if PDF was generated
        if pdf_value.startswith(b'%PDF-'):
            pdf_size = len(pdf_value)
            logger.info(f"Complex PDF generation successful. Size: {pdf_size} bytes")
            
            # Save the test file for inspection
            with open('test_complex.pdf', 'wb') as f:
                f.write(pdf_value)
            
            return True, pdf_size
        else:
            logger.error("Generated file doesn't appear to be a valid PDF")
            return False, 0
        
    except Exception as e:
        logger.error(f"Error generating complex PDF: {str(e)}")
        traceback.print_exc()
        return False, 0

def test_pdf_exporter():
    """Test the project's PdfExporter class"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("pdf_exporter", 
                                                     "app/services/pdf_exporter.py")
        if not spec:
            logger.error("Could not find app/services/pdf_exporter.py")
            return False
            
        pdf_exporter_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pdf_exporter_module)
        
        # Try to create the exporter
        exporter = pdf_exporter_module.get_pdf_exporter()
        logger.info("Successfully created PDF exporter instance")
        
        # Try to generate a report with a mock document
        mock_document = {
            "_id": "test_doc_id",
            "filename": "test_document.txt",
            "document_type": "policy",
            "created_at": datetime.now(),
            "paragraphs": [
                {"id": "p1", "text": "This is a test paragraph."}
            ],
            "compliance_score": 85,
            "compliance_status": "compliant",
            "compliance_issues": [
                {
                    "issue_id": "issue1",
                    "rule_id": "rule1",
                    "paragraph_id": "p1",
                    "description": "Test issue description",
                    "severity": "medium",
                    "compliance_type": "GDPR",
                    "suggestions": ["Test suggestion"]
                }
            ]
        }
        
        # Mock the MongoDB find_one method to return our mock document
        from unittest.mock import MagicMock, patch
        
        # First, get a reference to the actual mongo module
        from app.extensions import mongo
        original_find_one = mongo.db.documents.find_one
        
        try:
            # Patch the find_one method
            mongo.db.documents.find_one = MagicMock(return_value=mock_document)
            
            # Try to generate a report
            pdf_data = exporter.generate_compliance_report("test_doc_id")
            
            if pdf_data and isinstance(pdf_data, bytes) and pdf_data.startswith(b'%PDF-'):
                pdf_size = len(pdf_data)
                logger.info(f"PDF exporter test successful. Size: {pdf_size} bytes")
                
                # Save the test file for inspection
                with open('test_exporter.pdf', 'wb') as f:
                    f.write(pdf_data)
                
                return True
            else:
                logger.error("Generated file doesn't appear to be a valid PDF")
                return False
                
        finally:
            # Restore the original method
            mongo.db.documents.find_one = original_find_one
            
    except Exception as e:
        logger.error(f"Error testing PDF exporter: {str(e)}")
        traceback.print_exc()
        return False

def check_fonts():
    """Check available fonts"""
    try:
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        fonts = c.getAvailableFonts()
        logger.info(f"Available fonts: {', '.join(fonts)}")
        return fonts
    except Exception as e:
        logger.error(f"Error checking fonts: {str(e)}")
        return []

def check_disk_space():
    """Check if there's enough disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_mb = free / (1024 * 1024)
        logger.info(f"Free disk space: {free_mb:.2f} MB")
        return free_mb > 100  # Check if at least 100MB available
    except Exception as e:
        logger.error(f"Error checking disk space: {str(e)}")
        return True  # Assume enough space if check fails

def check_permissions():
    """Check write permissions in required directories"""
    directories = [
        os.path.abspath('.'),
        os.path.abspath('./app/services'),
        os.path.abspath('./instance/uploads')
    ]
    
    results = {}
    
    for directory in directories:
        if os.path.exists(directory):
            test_file = os.path.join(directory, 'permission_test.txt')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                results[directory] = "Write permission: OK"
            except (IOError, PermissionError) as e:
                results[directory] = f"Write permission: FAILED - {str(e)}"
        else:
            results[directory] = "Directory does not exist"
    
    return results

def run_all_tests():
    """Run all diagnostic tests"""
    results = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "reportlab_installed": False,
        "dependencies": {},
        "basic_pdf": False,
        "complex_pdf": False,
        "pdf_exporter": False,
        "fonts": [],
        "disk_space": {},
        "permissions": {}
    }
    
    # Check if ReportLab is installed
    results["reportlab_installed"] = check_reportlab_installation()
    
    if results["reportlab_installed"]:
        # Check dependencies
        results["dependencies"] = check_dependencies()
        
        # Check available fonts
        results["fonts"] = check_fonts()
        
        # Test basic PDF generation
        basic_success, basic_size = test_basic_pdf_generation()
        results["basic_pdf"] = {"success": basic_success, "size": basic_size}
        
        # Test complex PDF generation
        complex_success, complex_size = test_complex_pdf_generation()
        results["complex_pdf"] = {"success": complex_success, "size": complex_size}
        
        # Test PDF exporter if basic tests pass
        if basic_success and complex_success:
            results["pdf_exporter"] = test_pdf_exporter()
    
    # Check disk space
    disk_ok = check_disk_space()
    results["disk_space"] = {"sufficient": disk_ok}
    
    # Check permissions
    results["permissions"] = check_permissions()
    
    return results

if __name__ == "__main__":
    print("Running PDF Generation Diagnostic Tool...")
    results = run_all_tests()
    
    print("\n===== PDF Generation Diagnostic Results =====")
    print(f"Time: {results['timestamp']}")
    print(f"ReportLab installed: {results['reportlab_installed']}")
    
    if results['reportlab_installed']:
        print("\nDependencies:")
        for dep, status in results['dependencies'].items():
            print(f"  - {dep}: {status}")
        
        print("\nBasic PDF generation:", 
              "SUCCESS" if results['basic_pdf']['success'] else "FAILED")
        if results['basic_pdf']['success']:
            print(f"  - Size: {results['basic_pdf']['size']} bytes")
        
        print("\nComplex PDF generation:", 
              "SUCCESS" if results['complex_pdf']['success'] else "FAILED")
        if results['complex_pdf']['success']:
            print(f"  - Size: {results['complex_pdf']['size']} bytes")
        
        print("\nPDF Exporter test:", 
              "SUCCESS" if results['pdf_exporter'] else "FAILED")
        
        print("\nAvailable fonts:")
        for font in results['fonts']:
            print(f"  - {font}")
    
    print("\nDisk space check:",
          "SUFFICIENT" if results['disk_space']['sufficient'] else "INSUFFICIENT")
    
    print("\nPermissions:")
    for directory, status in results['permissions'].items():
        print(f"  - {directory}: {status}")
    
    print("\nDiagnostic complete. See pdf_debug.log for detailed information.")
    
    # Determine if there are any issues
    if not results['reportlab_installed']:
        print("\n⚠️ ISSUE: ReportLab is not installed properly.")
    elif not results['basic_pdf']['success']:
        print("\n⚠️ ISSUE: Cannot generate even a basic PDF.")
    elif not results['complex_pdf']['success']:
        print("\n⚠️ ISSUE: Cannot generate a complex PDF with tables and styles.")
    elif not results['pdf_exporter']:
        print("\n⚠️ ISSUE: The PdfExporter class has issues.")
    elif not results['disk_space']['sufficient']:
        print("\n⚠️ ISSUE: Insufficient disk space.")
    
    # Check for permission issues
    permission_issues = False
    for directory, status in results['permissions'].items():
        if "FAILED" in status:
            permission_issues = True
            print(f"\n⚠️ ISSUE: Permission problem with directory {directory}")
    
    if (results['reportlab_installed'] and results['basic_pdf']['success'] and 
        results['complex_pdf']['success'] and results['pdf_exporter'] and 
        results['disk_space']['sufficient'] and not permission_issues):
        print("\n✅ All diagnostic tests passed. No issues detected.")