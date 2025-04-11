# storyboard_generator/shot_list.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PILImage
from io import BytesIO

class ShotList(ttk.Frame):
    """UI component for viewing and exporting the shot list."""
    
    def __init__(self, master, app=None):
        """Initialize the shot list widget."""
        super().__init__(master)
        self.app = app
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        self.highlight_color = "#007ACC"  # Blue highlight
        
        # Create the UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the shot list UI components."""
        # Container frame with title
        self.container = ttk.LabelFrame(self, text="Shot List")
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control bar
        self.control_frame = ttk.Frame(self.container)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        # Export buttons
        self.export_pdf_btn = ttk.Button(self.control_frame, text="Export to PDF", command=self._export_to_pdf)
        self.export_pdf_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_xml_btn = ttk.Button(self.control_frame, text="Export to XML", command=self._export_to_xml)
        self.export_xml_btn.pack(side=tk.LEFT, padx=5)
        
        # Filter options (by camera, setup, etc.)
        ttk.Label(self.control_frame, text="Filter by:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(self.control_frame, textvariable=self.filter_var, width=15)
        filter_combo['values'] = ("All", "Camera", "Setup", "Scene")
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        self.filter_value_var = tk.StringVar()
        self.filter_value_combo = ttk.Combobox(self.control_frame, textvariable=self.filter_value_var, width=15)
        self.filter_value_combo.pack(side=tk.LEFT, padx=5)
        self.filter_value_combo.bind("<<ComboboxSelected>>", self._update_shot_list)
        
        # Table for displaying the shot list
        self.table_frame = ttk.Frame(self.container)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas with scrollbar for the table
        self.canvas = tk.Canvas(self.table_frame, background=self.bg_color, highlightthickness=0)
        self.scrollbar_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.config(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame for the table inside the canvas
        self.shot_table_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.shot_table_frame, anchor="nw")
        
        # Bind events
        self.shot_table_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<MouseWheel>", self._on_mousewheel)
        
        # Add enter/leave binding to control when mousewheel scrolls this pane
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Track when mouse enters this widget."""
        self.active_scroll = True
        
    def _on_leave(self, event):
        """Track when mouse leaves this widget."""
        self.active_scroll = False
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling when in this pane."""
        if hasattr(self, 'active_scroll') and self.active_scroll:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_frame_configure(self, event):
        """Update scroll region when the inner frame changes size."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Update the width of the inner frame when the canvas changes size."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_filter_change(self, event=None):
        """Handle filter type change."""
        filter_type = self.filter_var.get()
        filter_values = ["All"]
        
        # Get relevant filter values
        if self.app and hasattr(self.app, 'panels'):
            if filter_type == "Camera":
                filter_values.extend(sorted(set(panel.camera for panel in self.app.panels)))
            elif filter_type == "Setup":
                filter_values.extend(sorted(set(panel.setup_number for panel in self.app.panels if hasattr(panel, 'setup_number'))))
            elif filter_type == "Scene":
                filter_values.extend(sorted(set(panel.scene_number for panel in self.app.panels)))
        
        # Update filter value dropdown
        self.filter_value_combo['values'] = filter_values
        self.filter_value_var.set("All")
        
        # Update the shot list
        self._update_shot_list()
    
    def update(self):
        """Update the shot list view with current panels."""
        self._on_filter_change()  # This will refresh the filter values and update the shot list
    
    def _update_shot_list(self, event=None):
        """Update the shot list table based on the current filter."""
        # Clear existing table
        for widget in self.shot_table_frame.winfo_children():
            widget.destroy()
        
        if not self.app or not hasattr(self.app, 'panels') or not self.app.panels:
            # No panels to display
            ttk.Label(self.shot_table_frame, text="No shots available").pack(pady=20)
            return
        
        # Get filtered panels
        filter_type = self.filter_var.get()
        filter_value = self.filter_value_var.get()
        
        panels = self.app.panels
        
        if filter_value != "All":
            if filter_type == "Camera":
                panels = [p for p in panels if p.camera == filter_value]
            elif filter_type == "Setup":
                panels = [p for p in panels if hasattr(p, 'setup_number') and p.setup_number == filter_value]
            elif filter_type == "Scene":
                panels = [p for p in panels if p.scene_number == filter_value]
        
        # Sort panels by scene number, then setup number, then shot number
        panels = sorted(panels, key=lambda p: (
            int(p.scene_number) if p.scene_number.isdigit() else float('inf'),
            int(p.setup_number) if hasattr(p, 'setup_number') and p.setup_number.isdigit() else float('inf'),
            p.shot_number
        ))
        
        # Create table headers
        headers = ["Scene", "Shot", "Setup", "Camera", "Subject", "Time", "Size", "Move", "Lens", "Description", "Notes", "Audio", "Thumbnail"]
        header_width = [50, 50, 50, 80, 120, 50, 80, 80, 80, 200, 150, 150, 100]
        
        # Create header row
        for i, header in enumerate(headers):
            header_frame = ttk.Frame(self.shot_table_frame, width=header_width[i], height=30)
            header_frame.grid(row=0, column=i, sticky="nsew")
            header_frame.grid_propagate(False)
            
            label = ttk.Label(header_frame, text=header, font=("Arial", 10, "bold"))
            label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create row for each panel
        for i, panel in enumerate(panels):
            row = i + 1
            
            # Scene
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[0], height=60)
            cell_frame.grid(row=row, column=0, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.scene_number)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Shot
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[1], height=60)
            cell_frame.grid(row=row, column=1, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.shot_number)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Setup
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[2], height=60)
            cell_frame.grid(row=row, column=2, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            setup_text = panel.setup_number if hasattr(panel, 'setup_number') else "1"
            label = ttk.Label(cell_frame, text=setup_text)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Camera
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[3], height=60)
            cell_frame.grid(row=row, column=3, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            camera_text = panel.camera
            if hasattr(panel, 'camera_name') and panel.camera_name:
                camera_text += f" ({panel.camera_name})"
                
            label = ttk.Label(cell_frame, text=camera_text)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Subject
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[4], height=60)
            cell_frame.grid(row=row, column=4, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            subject_text = panel.subject if hasattr(panel, 'subject') else ""
            label = ttk.Label(cell_frame, text=subject_text, wraplength=header_width[4]-10)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Time
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[5], height=60)
            cell_frame.grid(row=row, column=5, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            time_text = panel.shot_time if hasattr(panel, 'shot_time') else ""
            label = ttk.Label(cell_frame, text=time_text)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Size
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[6], height=60)
            cell_frame.grid(row=row, column=6, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.size)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Move
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[7], height=60)
            cell_frame.grid(row=row, column=7, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.move)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Lens
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[8], height=60)
            cell_frame.grid(row=row, column=8, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.lens)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Description
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[9], height=60)
            cell_frame.grid(row=row, column=9, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.description, wraplength=header_width[9]-10)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Notes
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[10], height=60)
            cell_frame.grid(row=row, column=10, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, text=panel.notes, wraplength=header_width[10]-10)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Audio
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[11], height=60)
            cell_frame.grid(row=row, column=11, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            audio_text = panel.audio_notes if hasattr(panel, 'audio_notes') else ""
            label = ttk.Label(cell_frame, text=audio_text, wraplength=header_width[11]-10)
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Thumbnail
            cell_frame = ttk.Frame(self.shot_table_frame, width=header_width[12], height=60)
            cell_frame.grid(row=row, column=12, sticky="nsew")
            cell_frame.grid_propagate(False)
            
            if panel.image and panel.image_path and os.path.exists(panel.image_path):
                try:
                    # Create a small thumbnail
                    thumbnail = panel.get_thumbnail()
                    if thumbnail:
                        thumb_label = ttk.Label(cell_frame, image=thumbnail)
                        thumb_label.image = thumbnail  # Keep a reference
                        thumb_label.place(relx=0.5, rely=0.5, anchor="center")
                except Exception as e:
                    label = ttk.Label(cell_frame, text="Error")
                    label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                label = ttk.Label(cell_frame, text="No Image")
                label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Make the grid resizable
        for i in range(len(headers)):
            self.shot_table_frame.columnconfigure(i, weight=1)
        
        for i in range(len(panels) + 1):
            self.shot_table_frame.rowconfigure(i, weight=1)
    
    def _export_to_pdf(self):
        """Export the shot list to a PDF file."""
        if not self.app or not hasattr(self.app, 'panels') or not self.app.panels:
            messagebox.showerror("Error", "No shots available to export.")
            return
        
        # Get filtered panels
        filter_type = self.filter_var.get()
        filter_value = self.filter_value_var.get()
        
        panels = self.app.panels
        
        if filter_value != "All":
            if filter_type == "Camera":
                panels = [p for p in panels if p.camera == filter_value]
            elif filter_type == "Setup":
                panels = [p for p in panels if hasattr(p, 'setup_number') and p.setup_number == filter_value]
            elif filter_type == "Scene":
                panels = [p for p in panels if p.scene_number == filter_value]
        
        # Get project name if available
        project_name = "Storyboard Shot List"
        if hasattr(self.app, 'current_project_path') and self.app.current_project_path:
            project_name = os.path.splitext(os.path.basename(self.app.current_project_path))[0] + " - Shot List"
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Shot List to PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf"), ("All Files", "*.*")],
            initialfile=f"{project_name}.pdf"
        )
        
        if not file_path:
            return
        
        try:
            # Create PDF exporter
            shot_list_exporter = ShotListPDFExporter()
            
            # Export to PDF
            shot_list_exporter.export_shot_list(panels, file_path, project_name)
            
            messagebox.showinfo("Success", f"Shot list exported to PDF successfully:\n{file_path}")
            
            # Ask if user wants to open the PDF
            if messagebox.askyesno("Open PDF", "Would you like to open the exported PDF?"):
                self._open_file(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to PDF: {str(e)}")
    
    def _export_to_xml(self):
        """Export the shot list to an XML file."""
        if not self.app or not hasattr(self.app, 'panels') or not self.app.panels:
            messagebox.showerror("Error", "No shots available to export.")
            return
        
        # Get filtered panels
        filter_type = self.filter_var.get()
        filter_value = self.filter_value_var.get()
        
        panels = self.app.panels
        
        if filter_value != "All":
            if filter_type == "Camera":
                panels = [p for p in panels if p.camera == filter_value]
            elif filter_type == "Setup":
                panels = [p for p in panels if hasattr(p, 'setup_number') and p.setup_number == filter_value]
            elif filter_type == "Scene":
                panels = [p for p in panels if p.scene_number == filter_value]
        
        # Get project name if available
        project_name = "Storyboard Shot List"
        if hasattr(self.app, 'current_project_path') and self.app.current_project_path:
            project_name = os.path.splitext(os.path.basename(self.app.current_project_path))[0] + " - Shot List"
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Shot List to XML",
            defaultextension=".xml",
            filetypes=[("XML Document", "*.xml"), ("All Files", "*.*")],
            initialfile=f"{project_name}.xml"
        )
        
        if not file_path:
            return
        
        try:
            # Create XML exporter
            shot_list_exporter = ShotListXMLExporter()
            
            # Export to XML
            shot_list_exporter.export_shot_list(panels, file_path, project_name)
            
            messagebox.showinfo("Success", f"Shot list exported to XML successfully:\n{file_path}")
            
            # Ask if user wants to open the XML
            if messagebox.askyesno("Open XML", "Would you like to open the exported XML?"):
                self._open_file(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to XML: {str(e)}")
    
    def _open_file(self, file_path):
        """Open a file with the default application."""
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")


class ShotListPDFExporter:
    """Class to handle PDF export of shot lists."""
    
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
        
        self.table_header_style = ParagraphStyle(
            name='TableHeaderStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.table_cell_style = ParagraphStyle(
            name='TableCellStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT
        )
        
        self.table_cell_center_style = ParagraphStyle(
            name='TableCellCenterStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER
        )
        
        self.notes_style = ParagraphStyle(
            name='NotesStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_LEFT,
            textColor=colors.darkgrey
        )
    
    def export_shot_list(self, panels, output_path, project_name="Shot List"):
        """
        Export the shot list panels to a PDF file.
        
        Args:
            panels: List of Panel objects
            output_path: Path where to save the PDF file
            project_name: Name of the project for the title
        """
        # Create PDF document in landscape orientation
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Sort panels by scene number, then setup number, then shot number
        sorted_panels = sorted(panels, key=lambda p: (
            int(p.scene_number) if p.scene_number.isdigit() else float('inf'),
            int(p.setup_number) if hasattr(p, 'setup_number') and p.setup_number.isdigit() else float('inf'),
            p.shot_number
        ))
        
        # Create content elements
        elements = []
        
        # Add title
        elements.append(Paragraph(f"<b>{project_name}</b>", self.title_style))
        elements.append(Spacer(1, 5*mm))
        
        # Add date
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")
        elements.append(Paragraph(f"Generated: {date_str}", self.styles['Normal']))
        elements.append(Spacer(1, 5*mm))
        
        # Create camera color legend
        legend_data = []
        legend_header = ["Camera", "Color"]
        legend_data.append(legend_header)
        
        for camera, color in self.camera_colors.items():
            legend_data.append([
                Paragraph(camera, self.table_cell_style),
                ""  # Empty cell will be colored with the camera color
            ])
        
        # Create legend table
        legend_table = Table(
            legend_data,
            colWidths=[3*cm, 2*cm],
            style=[
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
            ]
        )
        
        # Add camera colors to the legend
        for i, (camera, color) in enumerate(self.camera_colors.items(), start=1):
            legend_table.setStyle([('BACKGROUND', (1, i), (1, i), color)])
        
        elements.append(legend_table)
        elements.append(Spacer(1, 5*mm))
        
        # Create shot list table data
        table_data = []
        
        # Define headers
        headers = [
            "Scene", "Shot", "Setup", "Camera", "Subject", "Time", 
            "Size", "Move", "Lens", "Description", "Notes", "Audio", "Image"
        ]
        
        # Define column widths
        col_widths = [
            1.5*cm, 1.5*cm, 1.5*cm, 2*cm, 3*cm, 1.5*cm, 
            2*cm, 2*cm, 1.5*cm, 4*cm, 4*cm, 3*cm, 2.5*cm
        ]
        
        # Add headers to table
        table_data.append([Paragraph(h, self.table_header_style) for h in headers])
        
        # Add each panel as a row
        for panel in sorted_panels:
            # Get camera color
            camera_color = self.camera_colors.get(panel.camera, colors.white)
            
            # Prepare cell data
            scene = Paragraph(panel.scene_number, self.table_cell_center_style)
            shot = Paragraph(panel.shot_number, self.table_cell_center_style)
            
            setup = Paragraph(
                panel.setup_number if hasattr(panel, 'setup_number') else "1", 
                self.table_cell_center_style
            )
            
            camera_text = panel.camera
            if hasattr(panel, 'camera_name') and panel.camera_name:
                camera_text += f"<br/>({panel.camera_name})"
            camera = Paragraph(camera_text, self.table_cell_center_style)
            
            subject = Paragraph(
                panel.subject if hasattr(panel, 'subject') else "", 
                self.table_cell_style
            )
            
            time = Paragraph(
                panel.shot_time if hasattr(panel, 'shot_time') else "", 
                self.table_cell_center_style
            )
            
            size = Paragraph(panel.size or "", self.table_cell_center_style)
            move = Paragraph(panel.move or "STATIC", self.table_cell_center_style)
            lens = Paragraph(panel.lens or "", self.table_cell_center_style)
            
            description = Paragraph(panel.description or "", self.table_cell_style)
            notes = Paragraph(panel.notes or "", self.table_cell_style)
            
            audio = Paragraph(
                panel.audio_notes if hasattr(panel, 'audio_notes') else "", 
                self.table_cell_style
            )
            
            # Create thumbnail image if available
            if panel.image and panel.image_path and os.path.exists(panel.image_path):
                try:
                    # Create a small thumbnail image
                    img = PILImage.open(panel.image_path)
                    thumb_width = 2*cm
                    thumb_height = 1.5*cm
                    
                    # Calculate aspect ratio
                    img_width, img_height = img.size
                    aspect = img_width / img_height
                    
                    # Resize based on aspect ratio
                    if aspect > 1:  # Wider than tall
                        thumb_height = thumb_width / aspect
                    else:  # Taller than wide
                        thumb_width = thumb_height * aspect
                        
                    # Create image object
                    image = Image(panel.image_path, width=thumb_width, height=thumb_height)
                except Exception as e:
                    # If image creation fails, use a placeholder
                    image = Paragraph("Image Error", self.table_cell_center_style)
            else:
                # No image available
                image = Paragraph("No Image", self.table_cell_center_style)
            
            # Add row to table data
            table_data.append([
                scene, shot, setup, camera, subject, time, 
                size, move, lens, description, notes, audio, image
            ])
        
        # Create the table
        shot_list_table = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1  # Repeat header row on each page
        )
        
        # Style the table
        table_style = TableStyle([
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Vertical alignment for all cells
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Center specific columns
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Scene
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Shot
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Setup
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Camera
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Time
            ('ALIGN', (6, 1), (8, -1), 'CENTER'),  # Size, Move, Lens
            
            # Font sizes
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Row heights
            ('ROWHEIGHT', (0, 0), (-1, 0), 20),
            ('ROWHEIGHT', (0, 1), (-1, -1), 40),
            
            # Thumbnail column alignment
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),
        ])
        
        # Add camera color to rows
        for i, panel in enumerate(sorted_panels, start=1):
            camera_color = self.camera_colors.get(panel.camera, colors.white)
            table_style.add('BACKGROUND', (3, i), (3, i), camera_color)
            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.white)
        
        shot_list_table.setStyle(table_style)
        
        # Add table to elements
        elements.append(shot_list_table)
        
        # Build the PDF
        doc.build(elements)
        
        return output_path


class ShotListXMLExporter:
    """Class to handle XML export of shot lists."""
    
    def export_shot_list(self, panels, output_path, project_name="Shot List"):
        """
        Export the shot list panels to an XML file.
        
        Args:
            panels: List of Panel objects
            output_path: Path where to save the XML file
            project_name: Name of the project for the title
        """
        # Sort panels by scene number, then setup number, then shot number
        sorted_panels = sorted(panels, key=lambda p: (
            int(p.scene_number) if p.scene_number.isdigit() else float('inf'),
            int(p.setup_number) if hasattr(p, 'setup_number') and p.setup_number.isdigit() else float('inf'),
            p.shot_number
        ))
        
        # Create root element
        root = ET.Element("ShotList")
        
        # Add metadata
        metadata = ET.SubElement(root, "Metadata")
        
        # Project name
        project = ET.SubElement(metadata, "Project")
        project.text = project_name
        
        # Date
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")
        date = ET.SubElement(metadata, "GeneratedDate")
        date.text = date_str
        
        # Add shots
        shots = ET.SubElement(root, "Shots")
        
        # Add each panel as a shot element
        for panel in sorted_panels:
            shot = ET.SubElement(shots, "Shot")
            
            # Basic info
            scene = ET.SubElement(shot, "Scene")
            scene.text = panel.scene_number
            
            shot_number = ET.SubElement(shot, "ShotNumber")
            shot_number.text = panel.shot_number
            
            setup = ET.SubElement(shot, "Setup")
            setup.text = panel.setup_number if hasattr(panel, 'setup_number') else "1"
            
            camera = ET.SubElement(shot, "Camera")
            camera.text = panel.camera
            
            if hasattr(panel, 'camera_name') and panel.camera_name:
                camera_name = ET.SubElement(shot, "CameraName")
                camera_name.text = panel.camera_name
            
            # Technical info
            technical = ET.SubElement(shot, "Technical")
            
            size = ET.SubElement(technical, "Size")
            size.text = panel.size or ""
            
            move = ET.SubElement(technical, "Move")
            move.text = panel.move or "STATIC"
            
            equip = ET.SubElement(technical, "Equipment")
            equip.text = panel.equip or "STICKS"
            
            lens = ET.SubElement(technical, "Lens")
            lens.text = panel.lens or ""
            
            # Additional info
            if hasattr(panel, 'subject') and panel.subject:
                subject = ET.SubElement(shot, "Subject")
                subject.text = panel.subject
            
            if hasattr(panel, 'shot_time') and panel.shot_time:
                time = ET.SubElement(shot, "Time")
                time.text = panel.shot_time
            
            if panel.description:
                description = ET.SubElement(shot, "Description")
                description.text = panel.description
            
            if panel.notes:
                notes = ET.SubElement(shot, "Notes")
                notes.text = panel.notes
            
            if hasattr(panel, 'audio_notes') and panel.audio_notes:
                audio = ET.SubElement(shot, "Audio")
                audio.text = panel.audio_notes
            
            # Background info
            if panel.bgd == "Yes":
                background = ET.SubElement(shot, "Background")
                background.text = panel.bgd_notes
            
            # Additional fields
            if panel.hair_makeup:
                hair_makeup = ET.SubElement(shot, "HairMakeup")
                hair_makeup.text = panel.hair_makeup
            
            if panel.props:
                props = ET.SubElement(shot, "Props")
                props.text = panel.props
            
            if panel.vfx:
                vfx = ET.SubElement(shot, "VFX")
                vfx.text = panel.vfx
            
            # Image path (relative path if in project)
            if panel.image_path:
                image_path = ET.SubElement(shot, "ImagePath")
                image_path.text = os.path.basename(panel.image_path)
        
        # Create a pretty-printed XML string
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return output_path
