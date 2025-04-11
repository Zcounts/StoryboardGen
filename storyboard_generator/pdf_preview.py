# storyboard_generator/pdf_preview.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
import io
import sys
import math

class PDFPreview(ttk.Frame):
    """UI component for previewing a page of panels as it will appear in the PDF."""
    
    def __init__(self, master, pdf_exporter=None):
        """Initialize the preview widget."""
        super().__init__(master)
        self.pdf_exporter = pdf_exporter
        self.all_panels = []
        self.current_scene = None
        self.current_page = 0
        self.total_pages = 0
        self.preview_image = None
        self.scale_factor = 1.0  # For zoom functionality
        
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
            "A": "#3F51B5",  # Blue
            "B": "#4CAF50",  # Green
            "C": "#FF9800",  # Orange
            "D": "#9C27B0",  # Purple
            "E": "#F44336",  # Red
            "F": "#795548",  # Brown
            "G": "#607D8B",  # Blue Grey
            "H": "#FFC107",  # Amber
            "I": "#00BCD4",  # Cyan
            "J": "#E91E63",  # Pink
            "K": "#009688",  # Teal
            "L": "#673AB7",  # Deep Purple
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
        self.preview_container = ttk.LabelFrame(self, text="PDF Preview")
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
            text="Select a panel to preview",
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
    
    def update_preview(self, panel):
        """
        Update the preview with all panels from the app.
        
        Args:
            panel: The Panel object that was selected, or None to clear
        """
        # Clear canvas
        self.preview_canvas.delete("all")
        
        if not panel:
            # Show the "no panel" label
            self.no_panel_label.place(relx=0.5, rely=0.5, anchor="center")
            self.current_page = 0
            self.total_pages = 0
            self.page_label.config(text="Page: 0 / 0")
            return
        
        # Hide the "no panel" label
        self.no_panel_label.place_forget()
        
        # Get the app object (parent of parent of this widget)
        app = self.master.master
        
        # Get all panels from the app
        if hasattr(app, 'panels'):
            self.all_panels = app.panels
            
            # Find the page with the selected panel
            self.current_scene = panel.scene_number
            
            # Group panels by scene
            scene_groups = self._group_panels_by_scene()
            
            # Calculate total pages
            self.total_pages = 0
            for scene_panels in scene_groups.values():
                # Each scene starts on a new page
                # Each page can show up to 6 panels (3x2 grid)
                scene_pages = math.ceil(len(scene_panels) / 6)
                self.total_pages += scene_pages
            
            # Find the page number with the selected panel
            self.current_page = 0
            found_page = False
            for scene_number, scene_panels in scene_groups.items():
                if scene_number == panel.scene_number:
                    # Find which page in this scene has the selected panel
                    for i, p in enumerate(scene_panels):
                        if p.id == panel.id:
                            self.current_page += i // 6
                            found_page = True
                            break
                    if found_page:
                        break
                else:
                    # Add pages for previous scenes
                    self.current_page += math.ceil(len(scene_panels) / 6)
            
            # Update page label
            self.page_label.config(text=f"Page: {self.current_page + 1} / {self.total_pages}")
            
            # Draw the current page
            self._draw_page(self.current_page)
            
        else:
            # Fallback if app panels are not accessible
            self.all_panels = [panel]
            self.current_page = 0
            self.total_pages = 1
            self.page_label.config(text="Page: 1 / 1")
            self._draw_page(0)
    
    def _group_panels_by_scene(self):
        """Group panels by scene number."""
        scene_groups = {}
        for panel in self.all_panels:
            scene_number = panel.scene_number
            if scene_number not in scene_groups:
                scene_groups[scene_number] = []
            scene_groups[scene_number].append(panel)
        
        # Sort panels within each scene by shot letter
        for scene_number, scene_panels in scene_groups.items():
            scene_groups[scene_number] = sorted(scene_panels, 
                                              key=lambda p: p.shot_number if p.shot_number else "")
        
        return scene_groups
    
    def _draw_page(self, page_number):
        """Draw a specific page of the preview."""
        # Clear canvas and thumbnails
        self.preview_canvas.delete("all")
        self.thumbnails = []
        
        # Group panels by scene
        scene_groups = self._group_panels_by_scene()
        
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
        
        # Find panels for the current page
        page_panels = []
        current_page = 0
        
        # Sort scene numbers numerically
        sorted_scenes = sorted(scene_groups.keys(), 
                             key=lambda s: int(s) if s.isdigit() else float('inf'))
        
        for scene_number in sorted_scenes:
            scene_panels = scene_groups[scene_number]
            scene_page_count = math.ceil(len(scene_panels) / 6)
            
            for i in range(scene_page_count):
                if current_page == page_number:
                    # This is the page we want to draw
                    start_idx = i * 6
                    end_idx = min(start_idx + 6, len(scene_panels))
                    page_panels = scene_panels[start_idx:end_idx]
                    
                    # Add scene title
                    title_text = f"Scene {scene_number} - Page {i+1} of {scene_page_count}"
                    
                    # Calculate title position (top center of page)
                    title_x = display_width // 2
                    title_y = (display_height - page_display_height) // 2 + 20
                    
                    self.preview_canvas.create_text(
                        title_x, title_y,
                        text=title_text,
                        fill="black",
                        font=("Arial", 12, "bold")
                    )
                    
                    break
                
                current_page += 1
            
            if current_page > page_number:
                break
        
        # Draw panels in a 3x2 grid
        if page_panels:
            # Calculate panel size
            margin = 20
            grid_width = page_display_width - 2 * margin
            grid_height = page_display_height - 80  # Leave space for title and margins
            
            panel_width = grid_width // 3
            panel_height = grid_height // 2
            
            # Draw up to 6 panels
            for i, panel in enumerate(page_panels):
                row = i // 3
                col = i % 3
                
                # Calculate position
                x1 = (display_width - page_display_width) // 2 + margin + col * panel_width
                y1 = (display_height - page_display_height) // 2 + 50 + row * panel_height
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
                header_height = 20
                self.preview_canvas.create_rectangle(
                    x1, y1, x2, y1 + header_height,
                    fill=camera_color,
                    outline=camera_color
                )
                
                # Add shot number and camera text
                shot_text = f"{panel.scene_number}{panel.shot_number} - {panel.camera}"
                self.preview_canvas.create_text(
                    x1 + 5, y1 + header_height // 2,
                    text=shot_text,
                    fill=self.text_color,
                    font=("Arial", 8, "bold"),
                    anchor="w"
                )
                
                # Add lens info if available
                if panel.lens:
                    self.preview_canvas.create_text(
                        x2 - 5, y1 + header_height // 2,
                        text=f"{panel.lens}",
                        fill=self.text_color,
                        font=("Arial", 8),
                        anchor="e"
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
                        fill="#DDDDDD",
                        font=("Arial", 6),
                        anchor="center"
                    )
                
                # Action and description area
                action_y = tech_y + tech_height + 5
                
                if panel.action:
                    action_text = f"ACTION: {panel.action}"
                    if len(action_text) > 40:
                        action_text = action_text[:37] + "..."
                        
                    self.preview_canvas.create_text(
                        x1 + 10, action_y,
                        text=action_text,
                        fill="black",
                        font=("Arial", 7),
                        anchor="nw"
                    )
                    action_y += 15
                
                if panel.description:
                    desc_text = panel.description
                    if len(desc_text) > 100:
                        desc_text = desc_text[:97] + "..."
                        
                    self.preview_canvas.create_text(
                        x1 + 10, action_y,
                        text=desc_text,
                        fill="black",
                        font=("Arial", 7),
                        anchor="nw",
                        width=panel_width - 20
                    )
        
        # Draw empty panels for remaining slots if needed
        for i in range(len(page_panels), 6):
            row = i // 3
            col = i % 3
            
            # Calculate position
            x1 = (display_width - page_display_width) // 2 + margin + col * panel_width
            y1 = (display_height - page_display_height) // 2 + 50 + row * panel_height
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
    
    def _get_shot_color(self, shot_letter):
        """Get a color for the shot based on its letter."""
        default_color = "#555555"  # Default gray
        
        if not shot_letter:
            return default_color
            
        return self.shot_colors.get(shot_letter[0], default_color)
