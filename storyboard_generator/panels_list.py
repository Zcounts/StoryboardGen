# storyboard_generator/panels_list.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

class PanelsList(ttk.Frame):
    """Custom widget to display and manage a list of storyboard panels."""
    
    def __init__(self, master, on_select=None, on_add=None, on_delete=None, 
                 on_move_up=None, on_move_down=None, on_duplicate=None):
        """
        Initialize the panels list widget.
        
        Args:
            master: Parent widget
            on_select: Callback when a panel is selected
            on_add: Callback to add a new panel
            on_delete: Callback to delete the selected panel
            on_move_up: Callback to move the selected panel up
            on_move_down: Callback to move the selected panel down
            on_duplicate: Callback to duplicate the selected panel
        """
        super().__init__(master)
        
        # Store callbacks
        self.on_select = on_select
        self.on_add = on_add
        self.on_delete = on_delete
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.on_duplicate = on_duplicate
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        self.selected_color = "#007ACC"  # Blue for selection
        
        # Create UI elements
        self._create_toolbar()
        self._create_panels_listbox()
        
        # Track selected panel
        self.selected_index = -1
        
        # Store panel data and image references
        self.panels = []
        self.thumbnails = []
    
    def _create_toolbar(self):
        """Create the toolbar with panel management buttons."""
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add button
        self.add_btn = ttk.Button(toolbar, text="Add", command=self._on_add_click)
        self.add_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        self.delete_btn = ttk.Button(toolbar, text="Delete", command=self._on_delete_click)
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Duplicate button
        self.duplicate_btn = ttk.Button(toolbar, text="Duplicate", command=self._on_duplicate_click)
        self.duplicate_btn.pack(side=tk.LEFT, padx=2)
        
        # Up button
        self.up_btn = ttk.Button(toolbar, text="Up", command=self._on_up_click)
        self.up_btn.pack(side=tk.LEFT, padx=2)
        
        # Down button
        self.down_btn = ttk.Button(toolbar, text="Down", command=self._on_down_click)
        self.down_btn.pack(side=tk.LEFT, padx=2)
    
    def _create_panels_listbox(self):
        """Create the listbox to display panels."""
        # Create a frame with a canvas and scrollbar for the panel list
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a canvas that will hold the panels
        self.canvas = tk.Canvas(self.list_frame, bg=self.bg_color, 
                               highlightthickness=0, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar to scroll the canvas
        scrollbar.config(command=self.canvas.yview)
        
        # Create a frame inside the canvas to hold panel items
        self.panels_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.panels_frame, anchor="nw", tags="self.panels_frame"
        )
        
        # Update scroll region when frame size changes
        self.panels_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_frame_configure(self, event):
        """Update the scroll region when the frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Resize the inner frame when the canvas changes size."""
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_add_click(self):
        """Handle click on the Add button."""
        if self.on_add:
            self.on_add()
    
    def _on_delete_click(self):
        """Handle click on the Delete button."""
        if self.on_delete and self.selected_index >= 0:
            self.on_delete()
    
    def _on_duplicate_click(self):
        """Handle click on the Duplicate button."""
        if self.on_duplicate and self.selected_index >= 0:
            self.on_duplicate()
    
    def _on_up_click(self):
        """Handle click on the Up button."""
        if self.on_move_up and self.selected_index > 0:
            self.on_move_up()
    
    def _on_down_click(self):
        """Handle click on the Down button."""
        if self.on_move_down and self.selected_index >= 0:
            self.on_move_down()
    
    def _on_panel_click(self, index):
        """Handle click on a panel item."""
        self.select_panel(index)
        if self.on_select:
            self.on_select(index)
    
    def select_panel(self, index):
        """
        Select a panel by index.
        
        Args:
            index: Index of the panel to select
        """
        if 0 <= index < len(self.panels):
            # Update the selected index
            self.selected_index = index
            
            # Update the visual selection in the UI
            for i, frame in enumerate(self.panels_frame.winfo_children()):
                if i == index:
                    frame.configure(style="Selected.TFrame")
                else:
                    frame.configure(style="TFrame")
    
    def update_panels(self, panels):
        """
        Update the list with new panels.
        
        Args:
            panels: List of Panel objects
        """
        # Store the panel data
        self.panels = panels
        
        # Keep track of thumbnails to prevent garbage collection
        self.thumbnails = []
        
        # Clear existing panel items
        for widget in self.panels_frame.winfo_children():
            widget.destroy()
        
        # Add panel items for each panel
        for i, panel in enumerate(panels):
            self._add_panel_item(i, panel)
        
        # Update the selection
        if self.selected_index >= len(panels):
            self.selected_index = len(panels) - 1 if panels else -1
        
        if self.selected_index >= 0:
            self.select_panel(self.selected_index)
    
    def _add_panel_item(self, index, panel):
        """
        Add a panel item to the list.
        
        Args:
            index: Index of the panel
            panel: Panel object
        """
        # Create a frame for this panel item
        item_style = "Selected.TFrame" if index == self.selected_index else "TFrame"
        item_frame = ttk.Frame(self.panels_frame, style=item_style, padding=5)
        item_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Make the frame selectable by clicking
        item_frame.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i))
        
        # Create a horizontal layout
        info_frame = ttk.Frame(item_frame, style="TFrame")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add shot number label
        shot_label = ttk.Label(
            info_frame, 
            text=f"Scene {panel.scene_number}{panel.shot_number}",
            style="TLabel",
            font=("Arial", 10, "bold")
        )
        shot_label.pack(anchor=tk.W)
        
        # Add description preview if available
        if panel.description:
            # Limit to first 50 chars
            preview = panel.description[:50] + "..." if len(panel.description) > 50 else panel.description
            desc_label = ttk.Label(info_frame, text=preview, style="TLabel")
            desc_label.pack(anchor=tk.W)
        
        # Add camera info
        camera_label = ttk.Label(info_frame, text=f"Camera: {panel.camera}", style="TLabel")
        camera_label.pack(anchor=tk.W)
        
        # Add thumbnail if available
        thumbnail = panel.get_thumbnail()
        if thumbnail:
            self.thumbnails.append(thumbnail)  # Keep reference
            thumb_label = ttk.Label(item_frame, image=thumbnail, style="TLabel")
            thumb_label.pack(side=tk.RIGHT, padx=5)
            
            # Also make thumbnail clickable
            thumb_label.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i))
