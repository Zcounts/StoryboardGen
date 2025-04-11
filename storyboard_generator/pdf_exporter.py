# storyboard_generator/pdf_exporter.py
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
        
        self.section_header_style = ParagraphStyle(
            name='SectionHeaderStyle',
            parent=self.styles['Heading3'],
            fontSize=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=2
        )
        
        self.additional_info_style = ParagraphStyle(
            name='AdditionalInfoStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            leading=10
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
        
        # Sort panels by scene and then by shot
        sorted_panels = sorted(panels, key=lambda p: (int(p.scene_number) if p.scene_number.isdigit() else float('inf'), 
                                                    p.shot_number))
        
        # Create content elements
        elements = []
        
        # Add title
        elements.append(Paragraph(f"<b>{project_name}</b>", self.title_style))
        elements.append(Spacer(1, 5*mm))
        
        # Group panels by scene
        scene_groups = {}
        for panel in sorted_panels:
            scene_number = panel.scene_number
            if scene_number not in scene_groups:
                scene_groups[scene_number] = []
            scene_groups[scene_number].append(panel)
        
        # Sort scenes numerically
        sorted_scenes = sorted(scene_groups.keys(), key=lambda s: int(s) if s.isdigit() else float('inf'))
        
        # Process each scene
        for scene_number in sorted_scenes:
            # Add scene header
            elements.append(Paragraph(f"<b>Scene {scene_number}</b>", self.header_style))
            elements.append(Spacer(1, 2*mm))
            
            # Get panels for this scene
            scene_panels = scene_groups[scene_number]
            
            # Process panels in groups of 3 (for 3 panels per row)
            panel_groups = [scene_panels[i:i+3] for i in range(0, len(scene_panels), 3)]
            
            # Process each group
            for group in panel_groups:
                # Create panel elements for this row
                panel_elements = []
                
                for panel in group:
                    panel_element = self._create_panel_element(panel)
                    panel_elements.append(panel_element)
                
                # Ensure we have 3 panels in the row by adding empty panels if needed
                while len(panel_elements) < 3:
                    panel_elements.append(self._create_empty_panel())
                
                # Create a table for this row of panels
                panel_row = Table(
                    [panel_elements],
                    colWidths=[8.5*cm, 8.5*cm, 8.5*cm],
                    rowHeights=[12*cm]
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
            
            # Add space between scenes
            elements.append(Spacer(1, 5*mm))
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
    
    def _create_panel_element(self, panel):
        """Create a formatted element for a single panel."""
        # Main container for the panel
        panel_elements = []
        
        # Create header row with shot info
        shot_text = panel.get_full_shot_number() if hasattr(panel, 'get_full_shot_number') else f"{panel.scene_number}{panel.shot_number}"
        header_data = [
            [
                Paragraph(shot_text, self.shot_style),
                Paragraph(panel.lens, ParagraphStyle(
                    name='LensStyle',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    alignment=TA_RIGHT
                ))
            ]
        ]
        
        header_table = Table(
            header_data,
            colWidths=[4.25*cm, 4.25*cm],
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
            colWidths=[2.125*cm, 2.125*cm, 2.125*cm, 2.125*cm],
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
            if panel.bgd == "Yes" and panel.bgd_notes:
                action_text += f": {panel.bgd_notes}"
            panel_elements.append(Paragraph(action_text, self.action_style))
        
        # Description
        if panel.description:
            panel_elements.append(Paragraph(panel.description, self.action_style))
        
        # Additional information sections
        if panel.hair_makeup or panel.props or panel.vfx:
            additional_text = ""
            
            if panel.hair_makeup:
                additional_text += f"<b>HAIR/MAKEUP:</b> {panel.hair_makeup}<br/>"
            
            if panel.props:
                additional_text += f"<b>PROPS:</b> {panel.props}<br/>"
            
            if panel.vfx:
                additional_text += f"<b>VFX:</b> {panel.vfx}<br/>"
            
            if additional_text:
                panel_elements.append(Paragraph(additional_text, self.additional_info_style))
        
        # Notes
        if panel.notes:
            panel_elements.append(Paragraph(f"<i>Notes: {panel.notes}</i>", self.notes_style))
        
        # Combine all elements into a single panel table
        panel_table = Table(
            [[element] for element in panel_elements],
            colWidths=[8.5*cm],
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
            colWidths=[8.5*cm],
            rowHeights=[12*cm]
        )
        
        panel_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        return panel_table
    
    def _create_image_element(self, panel):
        """Create an image element for the panel."""
        if not panel.image or not panel.image_path or not os.path.exists(panel.image_path):
            # Create an empty box if no image
            img_table = Table(
                [["No Image"]],
                colWidths=[8.5*cm],
                rowHeights=[6*cm]
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
            
            # Target width is 8.5 cm (about 240 points) minus some padding
            target_width = 8.3 * cm
            target_height = target_width / aspect
            
            # Ensure the height doesn't get too tall
            max_height = 6 * cm
            if target_height > max_height:
                target_height = max_height
                target_width = target_height * aspect
            
            # Create image object
            img_obj = Image(panel.image_path, width=target_width, height=target_height)
            
            # Create a table to hold the image and center it
            img_table = Table(
                [[img_obj]],
                colWidths=[8.5*cm],
                rowHeights=[6*cm]
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
                colWidths=[8.5*cm],
                rowHeights=[6*cm]
            )
            
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.red),
            ]))
            
            return img_table
    
    def _get_shot_color(self, panel):
        """Get a color for the shot label based on the scene number."""
        # Extract scene number
        scene_num = panel.scene_number
        
        # Define a set of colors for different scenes
        colors_list = [
            colors.blue,
            colors.darkgreen,
            colors.orange,
            colors.purple,
            colors.darkred,
            colors.brown,
            colors.darkslategray
        ]
        
        # Get color based on the scene number
        try:
            scene_int = int(scene_num)
            color_index = (scene_int - 1) % len(colors_list)
        except ValueError:
            color_index = hash(scene_num) % len(colors_list)
            
        return colors_list[color_index]
    
    def create_preview(self, panel):
        """
        Create a preview of a single panel for display in the UI.
        
        Args:
            panel: The Panel object to preview
            
        Returns:
            PIL.Image: An image of the panel preview
        """
        # This is a simplified version that would need to be implemented in a real application
        # For now, return a placeholder method that would be used for generating a preview
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate
        
        # Create a PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(10*cm, 15*cm),
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        # Create the panel element
        elements = []
        panel_element = self._create_panel_element(panel)
        elements.append(panel_element)
        
        # Build the PDF
        doc.build(elements)
        
        # Convert PDF to image (simplified version)
        # In a real implementation, you would use a PDF library to render the PDF to an image
        # For now, just return a placeholder message
        buffer.seek(0)
        return buffer
