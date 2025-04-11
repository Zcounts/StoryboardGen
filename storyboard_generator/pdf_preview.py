# storyboard_generator/pdf_preview.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
import io

class PDFPreview(ttk.Frame):
    """UI component for previewing a panel as it will appear in the PDF."""
    
    def __init__(self, master, pdf_exporter=None):
        """Initialize the preview widget."""
        super().__init__(master)
        self.pdf_exporter = pdf_exporter
        self.current_panel = None
        self.preview_image = None
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        self.highlight_color = "#007ACC"  # Blue highlight
        
        # Create the preview UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the preview UI components."""
        # Container frame with title
        self.preview_container = ttk.LabelFrame(self, text="PDF Preview")
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for displaying the preview
        self.preview_canvas = tk.Canvas(
            self.preview_container, 
            bg=self.bg_color,
            highlightthickness=0,
            bd=0  # No border
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Label for when no panel is selected
        self.no_panel_label = ttk.Label(
            self.preview_canvas,
            text="Select a panel to preview",
            background=self.bg_color,
            foreground=self.text_color
        )
        self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def update_preview(self, panel):
        """
        Update the preview with the given panel.
        
        Args:
            panel: The Panel object to preview, or None to clear
        """
        self.current_panel = panel
        
        # Clear any existing content
        self.preview_canvas.delete("all")
        
        if not panel:
            # Show the "no panel" label
            self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        # Hide the "no panel" label
        self.no_panel_label.place_forget()
        
        try:
            # Generate a preview using the PDF exporter
            if self.pdf_exporter:
                # Draw a panel representation
                panel_width = self.preview_canvas.winfo_width() - 40
                panel_height = self.preview_canvas.winfo_height() - 40
                
                # Make sure we have valid dimensions
                if panel_width <= 0:
                    panel_width = 300
                if panel_height <= 0:
                    panel_height = 400
                
                # Draw the panel with a dark background that's visible
                frame = self.preview_canvas.create_rectangle(
                    20, 20, 20 + panel_width, 20 + panel_height,
                    outline="#555555", width=2,
                    fill="#333333"  # Dark gray fill for visibility
                )
                
                # Draw header section
                header_height = 30
                header_color = self._get_scene_color(panel)
                header = self.preview_canvas.create_rectangle(
                    20, 20, 20 + panel_width, 20 + header_height,
                    fill=header_color,
                    outline=header_color  # Same color as fill to avoid white border
                )
                
                # Add shot number text
                shot_text = f"Scene {panel.scene_number}{panel.shot_number}"
                self.preview_canvas.create_text(
                    30, 20 + header_height//2,
                    text=shot_text,
                    fill=self.text_color,
                    anchor="w",
                    font=("Arial", 10, "bold")
                )
                
                # Add lens info if available
                if panel.lens:
                    self.preview_canvas.create_text(
                        20 + panel_width - 10, 20 + header_height//2,
                        text=panel.lens,
                        fill=self.text_color,
                        anchor="e",
                        font=("Arial", 9)
                    )
                
                # Image section placeholder
                img_height = 200
                img_y = 20 + header_height
                img_section = self.preview_canvas.create_rectangle(
                    20, img_y, 
                    20 + panel_width, 
                    img_y + img_height,
                    fill="#444444", 
                    outline="#555555"
                )
                
                # If panel has an image, try to display it
                if panel.image and panel.image_path and os.path.exists(panel.image_path):
                    try:
                        # Calculate display size while maintaining aspect ratio
                        img = panel.image.copy()
                        img_width, img_height_orig = img.size
                        aspect = img_width / img_height_orig
                        
                        new_width = min(panel_width - 10, int(img_height * aspect))
                        new_height = min(img_height - 10, int(new_width / aspect))
                        
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Keep a reference to prevent garbage collection
                        self.preview_image = photo
                        
                        # Calculate center position
                        x_pos = 20 + panel_width//2 - new_width//2
                        y_pos = img_y + img_height//2 - new_height//2
                        
                        # Create image on canvas
                        self.preview_canvas.create_image(
                            x_pos, y_pos, 
                            image=photo, 
                            anchor="nw"
                        )
                    except Exception as e:
                        # If image display fails, show error text
                        self.preview_canvas.create_text(
                            20 + panel_width//2, 
                            img_y + img_height//2,
                            text="Image preview error",
                            fill="#FF6666",
                            font=("Arial", 10)
                        )
                else:
                    # No image to display
                    self.preview_canvas.create_text(
                        20 + panel_width//2, 
                        img_y + img_height//2,
                        text="No image",
                        fill="#AAAAAA",
                        font=("Arial", 10)
                    )
                
                # Technical info section (SIZE, TYPE, MOVE, EQUIP)
                tech_y = img_y + img_height
                tech_height = 50
                tech_section = self.preview_canvas.create_rectangle(
                    20, tech_y, 
                    20 + panel_width, 
                    tech_y + tech_height,
                    fill="#222222", 
                    outline="#555555"
                )
                
                # Draw lines to separate columns
                col_width = panel_width / 4
                for i in range(1, 4):
                    self.preview_canvas.create_line(
                        20 + i * col_width, tech_y,
                        20 + i * col_width, tech_y + tech_height,
                        fill="#555555"
                    )
                
                # Draw line to separate header from values
                self.preview_canvas.create_line(
                    20, tech_y + 20,
                    20 + panel_width, tech_y + 20,
                    fill="#555555"
                )
                
                # Technical info headers
                for i, label in enumerate(["SIZE", "TYPE", "MOVE", "EQUIP"]):
                    self.preview_canvas.create_text(
                        20 + i * col_width + col_width/2, 
                        tech_y + 10,
                        text=label,
                        fill="#AAAAAA",
                        font=("Arial", 8, "bold")
                    )
                
                # Technical info values
                values = [
                    panel.size or "", 
                    panel.type or "", 
                    panel.move or "STATIC", 
                    panel.equip or "STICKS"
                ]
                
                for i, value in enumerate(values):
                    self.preview_canvas.create_text(
                        20 + i * col_width + col_width/2, 
                        tech_y + 35,
                        text=value,
                        fill=self.text_color,
                        font=("Arial", 8)
                    )
                
                # Description section
                desc_y = tech_y + tech_height
                desc_height = panel_height - header_height - img_height - tech_height
                desc_section = self.preview_canvas.create_rectangle(
                    20, desc_y, 
                    20 + panel_width, 
                    20 + panel_height,
                    fill="#222222", 
                    outline="#555555"
                )
                
                # Add description text
                desc_text = ""
                y_offset = 10
                
                # Action text
                if panel.action:
                    action_text = f"ACTION: {panel.action}"
                    self.preview_canvas.create_text(
                        30, desc_y + y_offset,
                        text=action_text,
                        fill=self.text_color,
                        anchor="nw",
                        width=panel_width - 20,
                        font=("Arial", 8, "bold")
                    )
                    y_offset += 20
                
                # Background info
                if panel.bgd == "Yes":
                    bgd_text = f"BGD: Yes" + (f" - {panel.bgd_notes}" if panel.bgd_notes else "")
                    self.preview_canvas.create_text(
                        30, desc_y + y_offset,
                        text=bgd_text,
                        fill=self.text_color,
                        anchor="nw",
                        width=panel_width - 20,
                        font=("Arial", 8, "bold")
                    )
                    y_offset += 20
                
                # Description 
                if panel.description:
                    self.preview_canvas.create_text(
                        30, desc_y + y_offset,
                        text=panel.description,
                        fill=self.text_color,
                        anchor="nw",
                        width=panel_width - 20,
                        font=("Arial", 8)
                    )
                    # Approximate height of text - increase offset based on text length
                    text_lines = len(panel.description) // 40 + 1
                    y_offset += text_lines * 12
                
                # Additional info like hair/makeup, props, vfx
                additional_info = []
                if panel.hair_makeup:
                    additional_info.append(f"HAIR/MAKEUP: {panel.hair_makeup}")
                if panel.props:
                    additional_info.append(f"PROPS: {panel.props}")
                if panel.vfx:
                    additional_info.append(f"VFX: {panel.vfx}")
                
                if additional_info:
                    for info in additional_info:
                        if y_offset + 15 < desc_height:  # Ensure it fits
                            self.preview_canvas.create_text(
                                30, desc_y + y_offset,
                                text=info,
                                fill=self.text_color,
                                anchor="nw",
                                width=panel_width - 20,
                                font=("Arial", 8, "bold")
                            )
                            y_offset += 15
                
                # Notes (if room)
                if panel.notes and y_offset + 15 < desc_height:
                    self.preview_canvas.create_text(
                        30, desc_y + y_offset,
                        text=f"Notes: {panel.notes}",
                        fill="#AAAAAA",  # Light gray
                        anchor="nw",
                        width=panel_width - 20,
                        font=("Arial", 8, "italic")
                    )
        except Exception as e:
            # Show error message if preview generation fails
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() / 2,
                self.preview_canvas.winfo_height() / 2,
                text=f"Error generating preview: {str(e)}",
                fill="#FF6666",
                font=("Arial", 10)
            )
    
    def _get_scene_color(self, panel):
        """Get a color for the shot label based on the scene number."""
        # Define a set of colors for different scenes - saturated and visible colors
        colors = [
            "#3F51B5",  # Blue
            "#4CAF50",  # Green
            "#FF9800",  # Orange
            "#9C27B0",  # Purple
            "#F44336",  # Red
            "#795548",  # Brown
            "#607D8B"   # Blue Grey
        ]
        
        # Get color based on the scene number
        try:
            scene_int = int(panel.scene_number)
            color_index = (scene_int - 1) % len(colors)
        except ValueError:
            # Use hash of scene number if not a valid integer
            color_index = hash(panel.scene_number) % len(colors)
        
        return colors[color_index]
