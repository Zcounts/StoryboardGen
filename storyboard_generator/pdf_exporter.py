# storyboard_generator/pdf_exporter.py
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer, PageBreak
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
        
        # Camera colors
        self.camera_colors = {
            "Camera 1": colors.darkgreen,  # Green
            "Camera 2": colors.darkred,    # Red
            "Camera 3": colors.purple,     # Purple
            "Camera 4": colors.blue,       # Blue
            "Camera 5": colors.orange,     # Orange
            "Camera 6": colors.brown,      # Brown
        }
        
        # Shot letter colors
        self.shot_colors = {
            "A": colors.blue,
            "B": colors.darkgreen,
            "C": colors.orange,
            "D": colors.purple,
            "E": colors.darkred,
            "F": colors.brown,
            "G": colors.darkslategray,
            "H": colors.gold,
            "I": colors.cyan,
            "J": colors.pink,
            "K": colors.teal,
            "L": colors.lavender,
            "M": colors.lime,
            "N": colors.lightblue,
            "O": colors.plum,
            "P": colors.rosybrown,
            "Q": colors.chocolate,
            "R": colors.crimson,
            "S": colors.lightgreen,
            "T": colors.tomato,
            "U": colors.magenta,
            "V": colors.indigo,
            "W": colors.darkkhaki,
            "X": colors.lightsalmon,
            "Y": colors.yellow,
            "Z": colors.orchid,
        }
    
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
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        
        self.lens_style = ParagraphStyle(
            name='LensStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT
        )
        
        self.setup_style = ParagraphStyle(
            name='SetupStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_RIGHT
        )
        
        self.label_style = ParagraphStyle(
            name='LabelStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER
        )
        
        self.cell_style = ParagraphStyle(
            name='CellStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER
        )
        
        self.action_style = ParagraphStyle(
            name='ActionStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_LEFT,
            leading=8
        )
        
        self.notes_style = ParagraphStyle(
            name='NotesStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_LEFT,
            textColor=colors.darkgrey
        )
        
        self.section_header_style = ParagraphStyle(
            name='SectionHeaderStyle',
            parent=self.styles['Heading3'],
            fontSize=9,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=2
        )
        
        self.additional_info_style = ParagraphStyle(
            name='AdditionalInfoStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_LEFT,
            leading=8
        )
        
        self.legend_style = ParagraphStyle(
            name='LegendStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT
        )
    
    def export_storyboard(self, panels, output_path, project_name="Storyboard"):
        """
        Export the storyboard panels to a PDF file.
        
        Args:
            panels: List of Panel objects
            output_path: Path where to save the PDF file
            project_name: Name of the project for the title
        """
        # Create PDF document with portrait orientation
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,  # Portrait orientation
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Group panels by scene and sort within each scene
        scene_groups = {}
        for panel in panels:
            scene_number = panel.scene_number
            if scene_number not in scene_groups:
                scene_groups[scene_number] = []
            scene_groups[scene_number].append(panel)
        
        # Sort panels within each scene
        for scene_number, scene_panels in scene_groups.items():
            scene_groups[scene_number] = sorted(
                scene_panels,
                key=lambda p: p.shot_number if p.shot_number else ""
            )
        
        # Sort scenes numerically
        sorted_scenes = sorted(scene_groups.keys(), 
                             key=lambda s: int(s) if s.isdigit() else float('inf'))
        
        # Create content elements
        elements = []
        
        # Add title
        elements.append(Paragraph(f"<b>{project_name}</b>", self.title_style))
        
        # Process each scene - each scene starts on a new page
        for scene_number in sorted_scenes:
            # Add scene header
            elements.append(Paragraph(f"<b>Scene {scene_number}</b>", self.header_style))
            elements.append(Spacer(1, 2*mm))
            
            # Get panels for this scene
            scene_panels = scene_groups[scene_number]
            
            # Process panels in groups of 6 (for 3 columns x 2 rows per page)
            panel_groups = [scene_panels[i:i+6] for i in range(0, len(scene_panels), 6)]
            
            # Process each group
            for i, group in enumerate(panel_groups):
                # Create panel elements for this page
                panel_elements = []
                
                for panel in group:
                    panel_element = self._create_panel_element(panel)
                    panel_elements.append(panel_element)
                
                # Ensure we have 6 panels in the grid by adding empty panels if needed
                while len(panel_elements) < 6:
                    panel_elements.append(self._create_empty_panel())
                
                # Arrange panels in a 3x2 grid (3 columns, 2 rows)
                row1 = panel_elements[:3]
                row2 = panel_elements[3:6]
                
                # Create a table for the entire grid
                grid = Table(
                    [row1, row2],
                    colWidths=[6.0*cm, 6.0*cm, 6.0*cm],
                    rowHeights=[14*cm, 14*cm]
                )
                
                # Add styling to the grid
                grid.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                # Add a sub-header for multi-page scenes
                if len(panel_groups) > 1:
                    elements.append(Paragraph(f"Page {i+1} of {len(panel_groups)}", self.section_header_style))
                    elements.append(Spacer(1, 2*mm))
                
                # Add the grid to the document
                elements.append(grid)
                
                # Add page break after each grid except the last one in the scene
                if i < len(panel_groups) - 1:
                    elements.append(PageBreak())
            
            # Add page break after each scene (except the last one)
            if scene_number != sorted_scenes[-1]:
                elements.append(PageBreak())
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
    
    def _create_panel_element(self, panel):
        """Create a formatted element for a single panel."""
        # Main container for the panel
        panel_elements = []
        
        # Get shot letter for color
        shot_letter = panel.shot_number[0] if panel.shot_number else ""
        shot_color = self.shot_colors.get(shot_letter, colors.gray)
        
        # Get camera color
        camera_color = self.camera_colors.get(panel.camera, colors.gray)
        
        # Create header row with shot info and setup
        setup_text = f"Setup {panel.setup_number}" if hasattr(panel, 'setup_number') and panel.setup_number else ""
        shot_text = f"{panel.scene_number}{panel.shot_number}"
        lens_text = f"Lens: {panel.lens}" if panel.lens else ""
        
        # Create a table for the header with two columns
        header_data = [
            [
                Paragraph(shot_text, self.shot_style),
                Paragraph(lens_text, self.lens_style)
            ]
        ]
        
        header_table = Table(
            header_data,
            colWidths=[3.0*cm, 3.0*cm],
            rowHeights=[0.4*cm]
        )
        
        # Style the header table without background color
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, 0), 5),
            ('RIGHTPADDING', (-1, 0), (-1, 0), 5),
        ]))
        
        panel_elements.append(header_table)
        
        # Add setup info if available
        if setup_text:
            panel_elements.append(Paragraph(setup_text, self.setup_style))
        
        # Add camera name if available
        if hasattr(panel, 'camera_name') and panel.camera_name:
            camera_name_text = f"Camera: {panel.camera}"
            if panel.camera_name:
                camera_name_text += f" ({panel.camera_name})"
            panel_elements.append(Paragraph(camera_name_text, self.action_style))
        
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
            colWidths=[1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm],
            rowHeights=[0.4*cm, 0.5*cm]
        )
        
        # Style the tech table
        tech_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
        ]))
        
        panel_elements.append(tech_table)
        
        # Add action description and other fields
        info_text = ""
        
        # Camera with color indicator
        if panel.camera:
            # Use a small color rect as an indicator
            r, g, b = camera_color.rgb()
            hex_color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
            info_text += f'<font color="{hex_color}">■</font> <b>CAMERA:</b> {panel.camera}'
            if hasattr(panel, 'camera_name') and panel.camera_name:
                info_text += f" ({panel.camera_name})"
            info_text += "<br/>"
        
        # Action
        if panel.action:
            info_text += f"<b>ACTION:</b> {panel.action}<br/>"
        
        # Background
        if panel.bgd == "Yes" and panel.bgd_notes:
            info_text += f"<b>BGD:</b> {panel.bgd_notes}<br/>"
        
        # Subject
        if hasattr(panel, 'subject') and panel.subject:
            info_text += f"<b>SUBJECT:</b> {panel.subject}<br/>"
        
        # Description
        if panel.description:
            info_text += f"{panel.description}<br/>"
        
        # Add additional information sections if they have "Yes" enabled
        # Hair/Makeup/Wardrobe
        if hasattr(panel, 'hair_makeup_enabled') and panel.hair_makeup_enabled == "Yes" and panel.hair_makeup:
            info_text += f"<b>H/M/W:</b> {panel.hair_makeup}<br/>"
        elif panel.hair_makeup:  # Backward compatibility
            info_text += f"<b>H/M/W:</b> {panel.hair_makeup}<br/>"
        
        # Props
        if hasattr(panel, 'props_enabled') and panel.props_enabled == "Yes" and panel.props:
            info_text += f"<b>PROPS:</b> {panel.props}<br/>"
        elif panel.props:  # Backward compatibility
            info_text += f"<b>PROPS:</b> {panel.props}<br/>"
        
        # VFX
        if hasattr(panel, 'vfx_enabled') and panel.vfx_enabled == "Yes" and panel.vfx:
            info_text += f"<b>VFX:</b> {panel.vfx}<br/>"
        elif panel.vfx:  # Backward compatibility
            info_text += f"<b>VFX:</b> {panel.vfx}<br/>"
        
        # Audio
        if hasattr(panel, 'audio_notes') and panel.audio_notes:
            info_text += f"<b>AUDIO:</b> {panel.audio_notes}<br/>"
        
        # Add the combined info text
        if info_text:
            panel_elements.append(Paragraph(info_text, self.action_style))
        
        # Notes
        if panel.notes:
            panel_elements.append(Paragraph(f"<i>Notes: {panel.notes}</i>", self.notes_style))
        
        # Combine all elements into a single panel table
        panel_table = Table(
            [[element] for element in panel_elements],
            colWidths=[6.0*cm],
        )
        
        # Style the panel table with a border using shot color
        panel_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, shot_color),  # Use shot color for box outline
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
            colWidths=[6.0*cm],
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
                colWidths=[6.0*cm],
                rowHeights=[4*cm]
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
            
            # Target width is 6.0 cm (about 170 points) minus some padding
            target_width = 5.8 * cm
            target_height = target_width / aspect
            
            # Ensure the height doesn't get too tall
            max_height = 4 * cm
            if target_height > max_height:
                target_height = max_height
                target_width = target_height * aspect
            
            # Create image object
            img_obj = Image(panel.image_path, width=target_width, height=target_height)
            
            # Create a table to hold the image and center it
            img_table = Table(
                [[img_obj]],
                colWidths=[6.0*cm],
                rowHeights=[4*cm]
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
                colWidths=[6.0*cm],
                rowHeights=[4*cm]
            )
            
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.red),
            ]))
            
            return img_table
    
    def create_preview(self, panels):
        """
        Create a preview of a page of panels for display in the UI.
        
        Args:
            panels: List of Panel objects to preview
            
        Returns:
            BytesIO: PDF data in memory that can be converted to an image
        """
        # Create a PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        # Create the panel elements
        elements = []
        
        # Title
        elements.append(Paragraph("<b>PDF Preview</b>", self.title_style))
        elements.append(Spacer(1, 3*mm))
        
        # Create panel elements for this page (up to 6 - 3x2 grid)
        preview_panels = panels[:6]
        panel_elements = []
        
        for panel in preview_panels:
            panel_element = self._create_panel_element(panel)
            panel_elements.append(panel_element)
        
        # Ensure we have 6 panels in the grid by adding empty panels if needed
        while len(panel_elements) < 6:
            panel_elements.append(self._create_empty_panel())
        
        # Arrange panels in a 3x2 grid (3 columns, 2 rows)
        row1 = panel_elements[:3]
        row2 = panel_elements[3:6]
        
        # Create a table for the entire grid
        grid = Table(
            [row1, row2],
            colWidths=[6.0*cm, 6.0*cm, 6.0*cm],
            rowHeights=[12*cm, 12*cm]
        )
        
        # Add styling to the grid
        grid.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        # Add the grid to the document
        elements.append(grid)
        
        # Build the PDF
        doc.build(elements)
        
        # Reset buffer position for reading
        buffer.seek(0)
        return buffer
