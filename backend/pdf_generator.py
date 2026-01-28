from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime
import json

class PDFGenerator:
    # PDF report generator for detection results
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea')
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#4a5568')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_full_report(self, history_entries):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Title section
        elements.append(Paragraph("Animal Detection System Report", self.title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Statistics section
        elements.append(Paragraph("Overall Statistics", self.heading_style))
        
        total_entries = len(history_entries)
        total_animals = sum(entry.total_animals for entry in history_entries)
        total_cats = sum(entry.cats_count for entry in history_entries)
        total_dogs = sum(entry.dogs_count for entry in history_entries)
        
        stats_data = [
            ["Metric", "Value"],
            ["Total Images Processed", str(total_entries)],
            ["Total Animals Detected", str(total_animals)],
            ["Total Cats Detected", str(total_cats)],
            ["Total Dogs Detected", str(total_dogs)],
            ["Average Animals per Image", f"{total_animals/total_entries:.2f}" if total_entries > 0 else "0.00"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 30))
        
        # Detailed history section
        if history_entries:
            elements.append(Paragraph("Detailed Detection History", self.heading_style))
            
            history_data = [["ID", "Filename", "Date", "Animals", "Cats", "Dogs", "Time(s)", "Confidence"]]
            
            for entry in history_entries:
                date_str = entry.upload_time.strftime('%Y-%m-%d %H:%M') if entry.upload_time else "N/A"
                history_data.append([
                    str(entry.id),
                    entry.filename[:30] + "..." if len(entry.filename) > 30 else entry.filename,
                    date_str,
                    str(entry.total_animals),
                    str(entry.cats_count),
                    str(entry.dogs_count),
                    f"{entry.processing_time:.2f}",
                    f"{entry.confidence:.2f}"
                ])
            
            history_table = Table(history_data, colWidths=[0.5*inch, 2*inch, 1.2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('ALIGN', (3, 1), (5, -1), 'CENTER'),
            ]))
            
            elements.append(history_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_single_report(self, entry):
        """Generate report for a single detection entry"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Title section
        elements.append(Paragraph("Animal Detection Report", self.title_style))
        elements.append(Paragraph(f"Detection ID: {entry.id}", self.styles['Normal']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Image information section
        elements.append(Paragraph("Image Information", self.heading_style))
        
        info_data = [
            ["Field", "Value"],
            ["Filename", entry.filename],
            ["Upload Time", entry.upload_time.strftime('%Y-%m-%d %H:%M:%S') if entry.upload_time else "N/A"],
            ["Processing Time", f"{entry.processing_time:.2f} seconds"],
            ["Confidence Threshold", f"{entry.confidence:.2f}"],
            ["Total Animals", str(entry.total_animals)],
            ["Cats Detected", str(entry.cats_count)],
            ["Dogs Detected", str(entry.dogs_count)]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 30))
        
        # Detections list section
        if entry.detections_json:
            detections = json.loads(entry.detections_json)
            if detections:
                elements.append(Paragraph("Detected Animals", self.heading_style))
                
                detection_data = [["#", "Animal Type", "Confidence", "Bounding Box", "Area"]]
                
                for i, detection in enumerate(detections, 1):
                    bbox = detection.get('bbox', [])
                    bbox_str = f"[{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]" if bbox else "N/A"
                    area = detection.get('area', 'N/A')
                    
                    detection_data.append([
                        str(i),
                        detection.get('class', 'Unknown').title(),
                        f"{detection.get('confidence', 0) * 100:.1f}%",
                        bbox_str,
                        str(area)
                    ])
                
                detection_table = Table(detection_data, colWidths=[0.5*inch, 1.2*inch, 1.2*inch, 2*inch, 1*inch])
                detection_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ]))
                
                elements.append(detection_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer