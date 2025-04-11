# storyboard_generator/pdf_preview.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
import io
import sys
import math

class PDFPreview(ttk.Frame):
    """UI component for previewing all panels as they will appear in the PDF."""
    
    def __init__(self, master, pdf_exporter=None):
        """Initialize the preview widget."""
        super().__init__(master)
        self.pdf_exporter = pdf_exporter
        self.all_panels = []
        self.current_page = 0
        self.total_pages = 0
        self.preview_image = None
        self.scale_factor = 1.0  # For zoom functionality
        self.base_font_size = 8  # Base font size for scaling
        
        # Camera colors
        self.camera_colors = {
            "Camera 1": "#4CAF50",  # Green
            "Camera 2": "#F44336",  # Red
            "Camera 3": "#9C27B0",  # Purple
            "Camera 4": "#2196F3",  # Blue
            "Camera 5": "#FF9800",  # Orange
            "Camera 6": "#795548",  # Brown
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
        self.preview_container = ttk.LabelFrame(self, text="Storyboard Preview")
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control bar at the top
        self.control_frame = ttk.Frame(self.preview_container)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        # Page navigation
        self.page_label = ttk.Label(self.control_frame, text="Page: 0 / 0")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        self.prev_btn = ttk.Button(self.control_frame, text="← Prev", command=self._prev_page)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(self.control_frame, text="Next →", command=self._next_page)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        self.zoom_out_btn = ttk.Button(self.control_frame, text="−", width=3, command=self._zoom_out)
        self.zoom_out_btn.pack(side=tk.RIGHT, padx=5)
        
        self.zoom_in_btn = ttk.Button(self.control_frame, text="+", width=3, command=self._zoom_in)
        self.zoom_in_btn.pack(side=tk.RIGHT, padx=5)
        
        self.zoom_label = ttk.Label(self.control_frame, text="100%")
        self.zoom_label.pack(side=tk.RIGHT, padx=5)
        
        # Canvas frame (with scrollbars)
        self.canvas_frame = ttk.Frame(self.preview_container)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal")
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical")
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for displaying the preview
        self.preview_canvas = tk.Canvas(
            self.canvas_frame, 
            bg=self.bg_color,
            highlightthickness=0,
            bd=0,  # No border
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        self.h_scrollbar.config(command=self.preview_canvas.xview)
        self.v_scrollbar.config(command=self.preview_canvas.yview)
        
        # Label for when no panel is selected
        self.no_panel_label = ttk.Label(
            self.preview_canvas,
            text="No panels to preview",
            background=self.bg_color,
            foreground=self.text_color
        )
        self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind mouse wheel events for scrolling and zooming
        self.preview_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.preview_canvas.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        
        # Bind canvas resize event
        self.preview_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Initialize thumbnail storage
        self.thumbnails = []
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_ctrl_mousewheel(self, event):
        """Handle mouse wheel + Ctrl for zooming."""
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize event."""
        if hasattr(self, 'current_page'):
            self._draw_page(self.current_page)
    
    def _zoom_in(self):
        """Increase zoom level."""
        if self.scale_factor < 2.0:
            self.scale_factor += 0.1
            self.zoom_label.config(text=f"{int(self.scale_factor * 100)}%")
            self._draw_page(self.current_page)
    
    def _zoom_out(self):
        """Decrease zoom level."""
        if self.scale_factor > 0.5:
            self.scale_factor -= 0.1
            self.zoom_label.config(text=f"{int(self.scale_factor * 100)}%")
            self._draw_page(self.current_page)
    
    def _prev_page(self):
        """Navigate to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._draw_page(self.current_page)
    
    def _next_page(self):
        """Navigate to the next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._draw_page(self.current_page)
    
    def update_preview(self, selected_panel=None):
        """
        Update the preview with all panels from the app.
        
        Args:
            selected_panel: The Panel object that was selected, or None to clear
        """
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Get the app object (parent of parent of this widget)
        app = self.master.master
        
        # Get all panels from the app
        if hasattr(app, 'panels') and app.panels:
            self.all_panels = app.panels
            
            # Calculate total pages (6 panels per page)
            self.total_pages = math.ceil(len(self.all_panels) / 6)
            
            # Update page label
            self.page_label.config(text=f"Page: 1 / {self.total_pages}")
            
            # Find which page contains the selected panel
            self.current_page = 0
            if selected_panel:
                for i, panel in enumerate(self.all_panels):
                    if panel.id == selected_panel.id:
                        self.current_page = i // 6
                        break
            
            # Hide the "no panel" label
            self.no_panel_label.place_forget()
            
            # Draw the current page
            self._draw_page(self.current_page)
        else:
            # Show the "no panel" label
            self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
            self.current_page = 0
            self.total_pages = 0
            self.page_label.config(text="Page: 0 / 0")
    
    def _draw_page(self, page_number):
        """Draw a specific page of the preview."""
        # Clear canvas and thumbnails
        self.preview_canvas.delete("all")
        self.thumbnails = []
        
        # Get canvas dimensions
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Use default dimensions if canvas not yet drawn
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 800
        
        # Apply scale factor
        display_width = int(canvas_width * self.scale_factor)
        display_height = int(canvas_height * self.scale_factor)
        
        # A4 aspect ratio is approximately 1:1.41
        page_width = 595  # A4 width in points
        page_height = 842  # A4 height in points
        
        # Scale page to fit display
        scale = min(display_width / page_width, display_height / page_height)
        page_display_width = int(page_width * scale)
        page_display_height = int(page_height * scale)
        
        # Draw page background
        self.preview_canvas.create_rectangle(
            (display_width - page_display_width) // 2,
            (display_height - page_display_height) // 2,
            (display_width + page_display_width) // 2,
            (display_height + page_display_height) // 2,
            fill="white",
            outline="#333333",
            width=1
        )
        
        # Draw title
        title_text = f"Storyboard Preview - Page {page_number + 1} of {self.total_pages}"
        title_x = display_width // 2
        title_y = (display_height - page_display_height) // 2 + 20
        
        # Calculate scaling for text (independent of zoom)
        font_size = int(self.base_font_size * scale)
        
        self.preview_canvas.create_text(
            title_x, title_y,
            text=title_text,
            fill="black",
            font=("Arial", font_size * 2, "bold")
        )
        
        # Draw camera color legend
        legend_y = title_y + 25
        legend_x = (display_width - page_display_width) // 2 + 50
        
        legend_title = "Camera Colors:"
        self.preview_canvas.create_text(
            legend_x, legend_y,
            text=legend_title,
            fill="black",
            font=("Arial", font_size + 2, "bold"),
            anchor="w"
        )
        
        for i, (camera, color) in enumerate(self.camera_colors.items()):
            # Draw color box
            box_x = legend_x + (i * 100 * scale)
            box_y = legend_y + 20
            
            self.preview_canvas.create_rectangle(
                box_x, box_y,
                box_x + 15, box_y + 15,
                fill=color,
                outline="black"
            )
            
            # Draw camera name
            self.preview_canvas.create_text(
                box_x + 25, box_y + 7,
                text=camera,
                fill="black",
                font=("Arial", font_size, "normal"),
                anchor="w"
            )
        
        # Calculate start index for panels on this page
        start_idx = page_number * 6
        end_idx = min(start_idx + 6, len(self.all_panels))
        page_panels = self.all_panels[start_idx:end_idx]
        
        # Draw panels in a 3x2 grid
        if page_panels:
            # Calculate panel size and positions
            margin = 20 * scale
            grid_width = page_display_width - (2 * margin)
            grid_height = page_display_height - 100 * scale  # Leave space for title and margin
            
            panel_width = grid_width // 3
            panel_height = grid_height // 2
            
            # Draw panels
            for i, panel in enumerate(page_panels):
                row = i // 3
                col = i % 3
                
                # Calculate position
                x1 = (display_width - page_display_width) // 2 + margin + col * panel_width
                y1 = (display_height - page_display_height) // 2 + 80 * scale + row * panel_height
                x2 = x1 + panel_width - 5
                y2 = y1 + panel_height - 5
                
                # Get shot letter for color
                shot_letter = panel.shot_number[0] if panel.shot_number else ""
                shot_color = self.shot_colors.get(shot_letter, "#555555")
                
                # Get camera color
                camera_color = self.camera_colors.get(panel.camera, "#555555")
                
                # Draw panel outline with shot color
                self.preview_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline=shot_color,
                    width=2
                )
                
                # Draw header with camera color
                header_height = 20 * scale
                self.preview_canvas.create_rectangle(
                    x1, y1, x2, y1 + header_height,
                    fill=camera_color,
                    outline=camera_color
                )
                
                # Calculate header text size (relative to panel, not zoom)
                header_font_size = int(font_size * 0.9)
                
                # Add shot number and camera text (camera name hidden as requested)
                shot_text = f"{panel.scene_number}{panel.shot_number}"
                self.preview_canvas.create_text(
                    x1 + 5, y1 + header_height // 2,
                    text=shot_text,
                    fill=self.text_color,
                    font=("Arial", header_font_size, "bold"),
                    anchor="w"
                )
                
                # Add lens info if available
                if panel.lens:
                    self.preview_canvas.create_text(
                        x2 - 5, y1 + header_height // 2,
                        text=f"{panel.lens}",
                        fill=self.text_color,
                        font=("Arial", header_font_size),
                        anchor="e"
                    )
                
                # Draw image area outline
                img_height = panel_height // 3
                self.preview_canvas.create_rectangle(
                    x1 + 5, y1 + header_height + 5, 
                    x2 - 5, y1 + header_height + 5 + img_height,
                    outline="#555555",
                    fill="#444444",
                    width=1
                )
                
                # Add image placeholder text if no image
                if not (panel.image and panel.image_path and os.path.exists(panel.image_path)):
                    self.preview_canvas.create_text(
                        (x1 + x2) // 2, 
                        y1 + header_height + 5 + (img_height // 2),
                        text="No Image",
                        fill="#AAAAAA",
                        font=("Arial", header_font_size)
                    )
                else:
                    # Try to show a small thumbnail of the image
                    try:
                        img = panel.image.copy()
                        thumb_width = panel_width - 20
                        thumb_height = img_height - 10
                        img.thumbnail((thumb_width, thumb_height), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Store the photo to prevent garbage collection
                        self.thumbnails.append(photo)
                        
                        # Create image on canvas
                        self.preview_canvas.create_image(
                            (x1 + x2) // 2, 
                            y1 + header_height + 5 + (img_height // 2),
                            image=photo
                        )
                    except Exception as e:
                        # If image display fails, show error text
                        self.preview_canvas.create_text(
                            (x1 + x2) // 2, 
                            y1 + header_height + 5 + (img_height // 2),
                            text="Image Error",
                            fill="#FF6666",
                            font=("Arial", header_font_size)
                        )
                
                # Draw technical info section
                tech_y = y1 + header_height + 5 + img_height + 5
                tech_height = 30 * scale
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
                
                tech_font_size = int(font_size * 0.7)
                col_width = (panel_width - 10) // 4
                for j, (header, value) in enumerate(zip(tech_headers, tech_values)):
                    # Header
                    self.preview_canvas.create_text(
                        x1 + 5 + j * col_width + col_width // 2, 
                        tech_y + 8 * scale,
                        text=header,
                        fill="#AAAAAA",
                        font=("Arial", tech_font_size),
                        anchor="center"
                    )
                    
                    # Value
                    self.preview_canvas.create_text(
                        x1 + 5 + j * col_width + col_width // 2, 
                        tech_y + 8 * scale + 14 * scale,
                        text=value,
                        fill="#DDDDDD",
                        font=("Arial", tech_font_size),
                        anchor="center"
                    )
                
                # Action and description area
                action_y = tech_y + tech_height + 5
                desc_font_size = int(font_size * 0.8)
                
                if panel.action:
                    action_text = f"ACTION: {panel.action}"
                    if len(action_text) > 40:
                        action_text = action_text[:37] + "..."
                        
                    self.preview_canvas.create_text(
                        x1 + 10, action_y,
                        text=action_text,
                        fill="black",
                        font=("Arial", desc_font_size),
                        anchor="nw"
                    )
                    action_y += 15 * scale
                
                if panel.description:
                    desc_text = panel.description
                    if len(desc_text) > 100:
                        desc_text = desc_text[:97] + "..."
                        
                    self.preview_canvas.create_text(
                        x1 + 10, action_y,
                        text=desc_text,
                        fill="black",
                        font=("Arial", desc_font_size),
                        anchor="nw",
                        width=panel_width - 20
                    )
        
        # Draw empty panels for remaining slots if needed
        for i in range(len(page_panels), 6):
            row = i // 3
            col = i % 3
            
            # Calculate position
            margin = 20 * scale
            grid_width = page_display_width - (2 * margin)
            grid_height = page_display_height - 100 * scale
            
            panel_width = grid_width // 3
            panel_height = grid_height // 2
            
            x1 = (display_width - page_display_width) // 2 + margin + col * panel_width
            y1 = (display_height - page_display_height) // 2 + 80 * scale + row * panel_height
            x2 = x1 + panel_width - 5
            y2 = y1 + panel_height - 5
            
            # Draw empty panel outline
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="#333333",
                width=1
            )
        
        # Update scroll region
        self.preview_canvas.configure(scrollregion=(0, 0, display_width, display_height))
