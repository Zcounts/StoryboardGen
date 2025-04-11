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
            "M": colors.lime,          # bright, stands out from earlier greens
            "N": colors.lightblue,     # a softer blue than A=blue
            "O": colors.plum,          # a warm purple-pink
            "P": colors.rosybrown,     # muted earthy tone
            "Q": colors.chocolate,     # rich brownish-orange
            "R": colors.crimson,       # strong, deep red
            "S": colors.lightgreen,    # airy green distinct from B=darkgreen
            "T": colors.tomato,        # vivid orangey-red
            "U": colors.magenta,       # bold, bright magenta
            "V": colors.indigo,        # deeper variant of purple/blue
            "W": colors.darkkhaki,     # muted yellowish-brown
            "X": colors.lightsalmon,   # soft orange-pink
            "Y": colors.yellow,        # a pure, classic yellow
            "Z": colors.orchid,        # pink-purple hue
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
            textColor=colors.white,
            alignment=TA_LEFT
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
        
        # Add camera color legend
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("<b>Camera Legend:</b>", self.section_header_style))
        
        legend_data = []
        for camera, color in self.camera_colors.items():
            # Convert color to hex for HTML
            r, g, b = color.rgb()
            hex_color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
            
            # Create a color box with camera name
            legend_item = f'<span style="background-color:{hex_color}; color:white; padding:2px 5px;">{camera}</span>'
            
            # Add camera name if specified in panels
            camera_names = set()
            for panel in panels:
                if panel.camera == camera and hasattr(panel, 'camera_name') and panel.camera_name:
                    camera_names.add(panel.camera_name)
            
            if camera_names:
                legend_item += f" ({', '.join(camera_names)})"
                
            legend_data.append(Paragraph(legend_item, self.legend_style))
        
        # Create a table with legend items (3 columns)
        rows = []
        row = []
        for i, item in enumerate(legend_data):
            row.append(item)
            if (i + 1) % 3 == 0 or i == len(legend_data) - 1:
                # Fill empty cells
                while len(row) < 3:
                    row.append("")
                rows.append(row)
                row = []
        
        legend_table = Table(rows, colWidths=[6*cm, 6*cm, 6*cm])
        legend_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(legend_table)
        elements.append(Spacer(1, 5*mm))
        
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
        
        header_data = [
            [
                Paragraph(shot_text, self.shot_style),
                Paragraph(setup_text, ParagraphStyle(
                    name='SetupStyle',
                    parent=self.styles['Normal'],
                    fontSize=7,
                    alignment=TA_RIGHT
                ))
            ]
        ]
        
        header_table = Table(
            header_data,
            colWidths=[3.0*cm, 3.0*cm],
            rowHeights=[0.4*cm]
        )
        
        # Style the header table
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), camera_color),  # Use camera color for header background
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, 0), 5),
            ('RIGHTPADDING', (-1, 0), (-1, 0), 5),
        ]))
        
        panel_elements.append(header_table)
        
        # Add lens info if available
        if panel.lens:
            lens_text = f"Lens: {panel.lens}"
            panel_elements.append(Paragraph(lens_text, self.action_style))
        
        # Add camera name if available
        if hasattr(panel, 'camera_name') and panel.camera_name:
            camera_name_text = f"Camera: {panel.camera_name}"
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
        
        # Add action description
        action_text = ""
        if panel.action:
            action_text += f"<b>ACTION:</b> {panel.action}"
        
        if action_text:
            action_text += f"<br/><b>BGD:</b> {panel.bgd}"
            if panel.bgd == "Yes" and panel.bgd_notes:
                action_text += f": {panel.bgd_notes}"
            panel_elements.append(Paragraph(action_text, self.action_style))
        
        # Add subject if available
        if hasattr(panel, 'subject') and panel.subject:
            subject_text = f"<b>SUBJECT:</b> {panel.subject}"
            panel_elements.append(Paragraph(subject_text, self.action_style))
        
        # Description
        if panel.description:
            panel_elements.append(Paragraph(panel.description, self.action_style))
        
        # Additional information sections
        additional_text = ""
        
        # Handle the yes/no toggle fields for additional info
        if hasattr(panel, 'hair_makeup_enabled') and panel.hair_makeup_enabled == "Yes" and panel.hair_makeup:
            additional_text += f"<b>HAIR/MAKEUP:</b> {panel.hair_makeup}<br/>"
        elif panel.hair_makeup:  # Backward compatibility
            additional_text += f"<b>HAIR/MAKEUP:</b> {panel.hair_makeup}<br/>"
        
        if hasattr(panel, 'props_enabled') and panel.props_enabled == "Yes" and panel.props:
            additional_text += f"<b>PROPS:</b> {panel.props}<br/>"
        elif panel.props:  # Backward compatibility
            additional_text += f"<b>PROPS:</b> {panel.props}<br/>"
        
        if hasattr(panel, 'vfx_enabled') and panel.vfx_enabled == "Yes" and panel.vfx:
            additional_text += f"<b>VFX:</b> {panel.vfx}<br/>"
        elif panel.vfx:  # Backward compatibility
            additional_text += f"<b>VFX:</b> {panel.vfx}<br/>"
        
        if additional_text:
            panel_elements.append(Paragraph(additional_text, self.additional_info_style))
        
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
