# pdf_exporter.py

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PILImage
from io import BytesIO

class PDFExporter:
    """Class to handle PDF export of storyboards."""
    
    def __init__(self):
        """Initialize the PDF exporter."""
        # Set up styles
        self._setup_styles()
    
    def _setup_styles(self):
        """Set up paragraph styles for the PDF."""
        # Register fonts if needed
        # pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
        
        # Get base styles
        self.styles = getSampleStyleSheet()
        
        # Create custom styles
        self.title_style = ParagraphStyle(
            name='TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=10
        )
        
        self.header_style = ParagraphStyle(
            name='HeaderStyle',
            parent=self.styles['Heading2'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=5
        )
        
        self.shot_style = ParagraphStyle(
            name='ShotStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_LEFT
        )
        
        self.label_style = ParagraphStyle(
            name='LabelStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER
        )
        
        self.cell_style = ParagraphStyle(
            name='CellStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER
        )
        
        self.action_style = ParagraphStyle(
            name='ActionStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            leading=10
        )
        
        self.notes_style = ParagraphStyle(
            name='NotesStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.darkgrey
        )
    
    def export_storyboard(self, panels, output_path, project_name="Storyboard"):
        """
        Export the storyboard panels to a PDF file.
        
        Args:
            panels: List of Panel objects
            output_path: Path where to save the PDF file
            project_name: Name of the project for the title
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Sort panels by order
        sorted_panels = sorted(panels, key=lambda p: p.order)
        
        # Create content elements
        elements = []
        
        # Add title
        elements.append(Paragraph(f"<b>{project_name}</b>", self.title_style))
        elements.append(Spacer(1, 5*mm))
        
        # Process panels in groups of 4 (for 4 panels per row)
        panel_groups = [sorted_panels[i:i+4] for i in range(0, len(sorted_panels), 4)]
        
        # Process each group
        for group in panel_groups:
            # Create panel elements for this row
            panel_elements = []
            
            for panel in group:
                panel_element = self._create_panel_element(panel)
                panel_elements.append(panel_element)
            
            # Ensure we have 4 panels in the row by adding empty panels if needed
            while len(panel_elements) < 4:
                panel_elements.append(self._create_empty_panel())
            
            # Create a table for this row of panels
            panel_row = Table(
                [panel_elements],
                colWidths=[6.5*cm, 6.5*cm, 6.5*cm, 6.5*cm],
                rowHeights=[10*cm]
            )
            
            # Add styling to the row
            panel_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            
            # Add the row to the document
            elements.append(panel_row)
            elements.append(Spacer(1, 5*mm))
        
        # Add page numbers
        # This would require a custom PageTemplate, omitted for simplicity
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
    
    def _create_panel_element(self, panel):
        """Create a formatted element for a single panel."""
        # Main container for the panel
        panel_elements = []
        
        # Create header row with shot info
        header_data = [
            [
                self._create_shot_label(panel),
                self._create_lens_label(panel),
            ]
        ]
        
        header_table = Table(
            header_data,
            colWidths=[3.25*cm, 3.25*cm],
            rowHeights=[0.5*cm]
        )
        
        # Style the header table
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), self._get_shot_color(panel)),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, 0), 5),
            ('RIGHTPADDING', (-1, 0), (-1, 0), 5),
        ]))
        
        panel_elements.append(header_table)
        
        # Add image
        image_element = self._create_image_element(panel)
        panel_elements.append(image_element)
        
        # Create technical info table (SIZE, TYPE, MOVE, EQUIP)
        tech_data = [
            ['SIZE', 'TYPE', 'MOVE', 'EQUIP'],
            [
                Paragraph(panel.size or "", self.cell_style),
                Paragraph(panel.type or "", self.cell_style),
                Paragraph(panel.move or "STATIC", self.cell_style),
                Paragraph(panel.equip or "STICKS", self.cell_style)
            ]
        ]
        
        tech_table = Table(
            tech_data,
            colWidths=[1.625*cm, 1.625*cm, 1.625*cm, 1.625*cm],
            rowHeights=[0.5*cm, 0.6*cm]
        )
        
        # Style the tech table
        tech_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
        ]))
        
        panel_elements.append(tech_table)
        
        # Add action description
        action_text = ""
        if panel.action:
            action_text += f"<b>ACTION:</b> {panel.action}"
        
        if action_text:
            action_text += f"<br/><b>BGD:</b> {panel.bgd}"
            panel_elements.append(Paragraph(action_text, self.action_style))
        
        # Notes or additional description
        if panel.description:
            panel_elements.append(Paragraph(panel.description, self.notes_style))
        
        # Combine all elements into a single panel table
        panel_table = Table(
            [[element] for element in panel_elements],
            colWidths=[6.5*cm],
        )
        
        # Style the panel table with a border
        panel_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        return panel_table
    
    def _create_empty_panel(self):
        """Create an empty panel placeholder."""
        panel_table = Table(
            [[""]],
            colWidths=[6.5*cm],
            rowHeights=[10*cm]
        )
        
        panel_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        return panel_table
    
    def _create_shot_label(self, panel):
        """Create a formatted shot label for a panel."""
        shot_text = panel.shot_number if panel.shot_number else ""
        if not shot_text:
            shot_text = f"{panel.order + 1}"
        
        shot_text = f"{shot_text} - {panel.camera}"
        
        return Paragraph(shot_text, self.shot_style)
    
    def _create_lens_label(self, panel):
        """Create a formatted lens label for a panel."""
        lens_text = panel.lens if panel.lens else ""
        
        lens_style = ParagraphStyle(
            name='LensStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT
        )
        
        return Paragraph(lens_text, lens_style)
    
    def _create_image_element(self, panel):
        """Create an image element for the panel."""
        if not panel.image or not panel.image_path or not os.path.exists(panel.image_path):
            # Create an empty box if no image
            img_table = Table(
                [["No Image"]],
                colWidths=[6.5*cm],
                rowHeights=[5*cm]
            )
            
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.lightgrey),
            ]))
            
            return img_table
        
        try:
            # Create a properly sized image for the PDF
            # ReportLab wants the image dimensions in points
            img = PILImage.open(panel.image_path)
            img_width, img_height = img.size
            
            # Calculate aspect ratio
            aspect = img_width / img_height
            
            # Target width is 6.5 cm (about 184 points) minus some padding
            target_width = 6.3 * cm
            target_height = target_width / aspect
            
            # Ensure the height doesn't get too tall
            max_height = 5 * cm
            if target_height > max_height:
                target_height = max_height
                target_width = target_height * aspect
            
            # Create image object
            img_obj = Image(panel.image_path, width=target_width, height=target_height)
            
            # Create a table to hold the image and center it
            img_table = Table(
                [[img_obj]],
                colWidths=[6.5*cm],
                rowHeights=[5*cm]
            )
            
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            return img_table
            
        except Exception as e:
            print(f"Error processing image for PDF: {e}")
            
            # Return an error placeholder
            img_table = Table(
                [["Image Error"]],
                colWidths=[6.5*cm],
                rowHeights=[5*cm]
            )
            
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.red),
            ]))
            
            return img_table
    
    def _get_shot_color(self, panel):
        """Get a color for the shot label based on the shot number."""
        # Extract alphanumeric part from shot number if it exists
        shot_num = panel.shot_number if panel.shot_number else str(panel.order + 1)
        
        # Define a set of colors for different shots
        colors_list = [
            colors.blue,
            colors.orange,
            colors.green,
            colors.purple,
            colors.red,
            colors.brown,
            colors.darkgrey
        ]
        
        # Get color based on the first character of the shot number
        color_index = hash(shot_num[0]) % len(colors_list)
        return colors_list[color_index]
