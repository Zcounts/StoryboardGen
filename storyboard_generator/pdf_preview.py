# storyboard_generator/pdf_preview.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
import io
import sys

class PDFPreview(ttk.Frame):
    """UI component for previewing a page of panels as it will appear in the PDF."""
    
    def __init__(self, master, pdf_exporter=None):
        """Initialize the preview widget."""
        super().__init__(master)
        self.pdf_exporter = pdf_exporter
        self.current_panels = []
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
        
        # Add scrollbar for previewing
        scrollbar = ttk.Scrollbar(self.preview_container, orient="vertical", command=self.preview_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.preview_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        self.preview_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Label for when no panel is selected
        self.no_panel_label = ttk.Label(
            self.preview_canvas,
            text="Select a panel to preview",
            background=self.bg_color,
            foreground=self.text_color
        )
        self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def update_preview(self, panel):
        """
        Update the preview with the given panel and its surrounding panels.
        
        Args:
            panel: The Panel object to preview, or None to clear
        """
        # Clear canvas
        self.preview_canvas.delete("all")
        
        if not panel:
            # Show the "no panel" label
            self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        # Hide the "no panel" label
        self.no_panel_label.place_forget()
        
        # Get the app object (parent of parent of this widget)
        app = self.master.master
        
        # Try to get a list of panels from the same scene
        self.current_panels = []
        found_panel = False
        
        if hasattr(app, 'panels'):
            scene_panels = []
            current_scene = panel.scene_number
            
            # Find all panels in the same scene
            for p in app.panels:
                if p.scene_number == current_scene:
                    scene_panels.append(p)
                    if p == panel:
                        found_panel = True
            
            # Include panels from the same scene
            self.current_panels = scene_panels
            
            # If no panels found in the same scene or the panel is not in the list,
            # fallback to just previewing this panel
            if not found_panel:
                self.current_panels = [panel]
        else:
            # Fallback to just previewing this panel
            self.current_panels = [panel]
        
        try:
            # Generate a preview using the PDF exporter
            if self.pdf_exporter:
                # Use the PDF exporter to create a PDF preview
                pdf_data = self.pdf_exporter.create_preview(self.current_panels)
                
                # Convert the PDF to an image for display
                # We'll use a simple message first
                preview_img = None
                
                try:
                    # If poppler/pdf2image is available, we can convert PDF to image
                    from pdf2image import convert_from_bytes
                    pages = convert_from_bytes(pdf_data.getvalue(), dpi=100)
                    if pages:
                        preview_img = pages[0]
                except ImportError:
                    # If pdf2image is not available, show a message
                    self.preview_canvas.create_text(
                        self.preview_canvas.winfo_width() // 2,
                        20,
                        text="PDF preview generated. Install pdf2image for image preview.",
                        fill=self.text_color,
                        anchor="n"
                    )
                
                # If we have a preview image, display it
                if preview_img:
                    # Resize to fit the canvas
                    canvas_width = self.preview_canvas.winfo_width()
                    if canvas_width <= 1:  # If canvas not yet drawn
                        canvas_width = 400
                    
                    # Calculate new dimensions maintaining aspect ratio
                    img_width, img_height = preview_img.size
                    new_width = min(canvas_width, img_width)
                    new_height = int(img_height * (new_width / img_width))
                    
                    preview_img = preview_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(preview_img)
                    self.preview_image = photo  # Keep a reference
                    
                    # Create image on canvas
                    self.preview_canvas.create_image(
                        canvas_width // 2, 10, 
                        image=photo, 
                        anchor="n"
                    )
                    
                    # Update scroll region
                    self.preview_canvas.configure(scrollregion=(0, 0, new_width, new_height + 20))
                else:
                    # If we couldn't convert the PDF to an image, draw a simulated preview
                    self._draw_simulated_preview()
            else:
                # If no PDF exporter, draw a simulated preview
                self._draw_simulated_preview()
                
        except Exception as e:
            # Show error message if preview generation fails
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                text=f"Error generating preview: {str(e)}",
                fill="#FF6666",
                font=("Arial", 10)
            )
    
    def _draw_simulated_preview(self):
        """Draw a simulated preview when PDF conversion is not available."""
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1:  # If canvas not yet drawn
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 500
        
        # Title text
        self.preview_canvas.create_text(
            canvas_width // 2, 20,
            text="PDF Preview - Simulated",
            fill=self.text_color,
            font=("Arial", 12, "bold"),
            anchor="n"
        )
        
        # Draw a grid of panel outlines (3x2)
        # Calculate panel size
        panel_width = (canvas_width - 40) // 3
        panel_height = (canvas_height - 100) // 2
        
        # Draw up to 6 panels
        for i, panel in enumerate(self.current_panels[:6]):
            row = i // 3
            col = i % 3
            
            # Calculate position
            x1 = 20 + col * panel_width
            y1 = 50 + row * panel_height
            x2 = x1 + panel_width - 5
            y2 = y1 + panel_height - 5
            
            # Draw panel outline
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="#555555",
                width=2
            )
            
            # Draw header
            header_height = 20
            header_color = self._get_scene_color(panel)
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y1 + header_height,
                fill=header_color,
                outline=header_color
            )
            
            # Add shot number text
            shot_text = f"Scene {panel.scene_number}{panel.shot_number}"
            self.preview_canvas.create_text(
                x1 + 5, y1 + header_height // 2,
                text=shot_text,
                fill=self.text_color,
                font=("Arial", 8, "bold"),
                anchor="w"
            )
            
            # Draw image area outline
            self.preview_canvas.create_rectangle(
                x1 + 5, y1 + header_height + 5, 
                x2 - 5, y1 + header_height + 5 + (panel_height // 3),
                outline="#555555",
                fill="#444444",
                width=1
            )
            
            # Add image placeholder text if no image
            if not (panel.image and panel.image_path and os.path.exists(panel.image_path)):
                self.preview_canvas.create_text(
                    (x1 + x2) // 2, 
                    y1 + header_height + 5 + (panel_height // 6),
                    text="No Image",
                    fill="#AAAAAA",
                    font=("Arial", 8)
                )
            else:
                # Try to show a small thumbnail of the image
                try:
                    img = panel.image.copy()
                    thumb_width = panel_width - 20
                    thumb_height = panel_height // 3 - 10
                    img.thumbnail((thumb_width, thumb_height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Store the photo to prevent garbage collection
                    if not hasattr(self, 'thumbnails'):
                        self.thumbnails = []
                    self.thumbnails.append(photo)
                    
                    # Create image on canvas
                    self.preview_canvas.create_image(
                        (x1 + x2) // 2, 
                        y1 + header_height + 5 + (panel_height // 6),
                        image=photo
                    )
                except Exception as e:
                    # If image display fails, show error text
                    self.preview_canvas.create_text(
                        (x1 + x2) // 2, 
                        y1 + header_height + 5 + (panel_height // 6),
                        text="Image Error",
                        fill="#FF6666",
                        font=("Arial", 8)
                    )
            
            # Draw technical info section
            tech_y = y1 + header_height + 5 + (panel_height // 3) + 5
            tech_height = 30
            self.preview_canvas.create_rectangle(
                x1 + 5, tech_y, 
                x2 - 5, tech_y + tech_height,
                outline="#555555",
                fill="#222222",
                width=1
            )
            
            # Draw text in technical info section
            tech_headers = ["SIZE", "TYPE", "MOVE", "EQUIP"]
            tech_values = [
                panel.size or "", 
                panel.type or "", 
                panel.move or "STATIC", 
                panel.equip or "STICKS"
            ]
            
            col_width = (panel_width - 10) // 4
            for j, (header, value) in enumerate(zip(tech_headers, tech_values)):
                # Header
                self.preview_canvas.create_text(
                    x1 + 5 + j * col_width + col_width // 2, 
                    tech_y + 8,
                    text=header,
                    fill="#AAAAAA",
                    font=("Arial", 6),
                    anchor="center"
                )
                
                # Value
                self.preview_canvas.create_text(
                    x1 + 5 + j * col_width + col_width // 2, 
                    tech_y + 22,
                    text=value,
                    fill=self.text_color,
                    font=("Arial", 6),
                    anchor="center"
                )
            
            # Action and description area
            action_y = tech_y + tech_height + 5
            
            if panel.action:
                self.preview_canvas.create_text(
                    x1 + 10, action_y,
                    text=f"ACTION: {panel.action[:30]}...",
                    fill=self.text_color,
                    font=("Arial", 7),
                    anchor="nw"
                )
                action_y += 15
            
            if panel.description:
                self.preview_canvas.create_text(
                    x1 + 10, action_y,
                    text=panel.description[:50] + "..." if len(panel.description) > 50 else panel.description,
                    fill=self.text_color,
                    font=("Arial", 7),
                    anchor="nw",
                    width=panel_width - 20
                )
        
        # Draw empty panels for remaining slots
        for i in range(len(self.current_panels), 6):
            row = i // 3
            col = i % 3
            
            # Calculate position
            x1 = 20 + col * panel_width
            y1 = 50 + row * panel_height
            x2 = x1 + panel_width - 5
            y2 = y1 + panel_height - 5
            
            # Draw empty panel outline
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="#333333",
                width=1
            )
        
        # Update scroll region
        total_height = 50 + 2 * panel_height + 20
        self.preview_canvas.configure(scrollregion=(0, 0, canvas_width, total_height))
    
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
