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
        self.hover_color = "#3E3E42"  # Color for hover effect
        self.item_bg_color = "#252526"  # Slightly lighter than background for items
        
        # Create UI elements
        self._create_toolbar()
        self._create_panels_listbox()
        
        # Track selected panel
        self.selected_index = -1
        
        # Store panel data and image references
        self.panels = []
        self.thumbnails = []
        self.panel_frames = []  # Track panel frames for selection
    
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
        self.panels_frame = ttk.Frame(self.canvas)
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
    
    def _on_panel_click(self, index, event=None):
        """Handle click on a panel item."""
        # Ensure index is valid
        if 0 <= index < len(self.panels):
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
            for i, frame in enumerate(self.panel_frames):
                if i == index:
                    # Use colored background for selected item
                    frame.configure(background=self.selected_color)
                    
                    # Apply distinct style to all child labels
                    for child in frame.winfo_children():
                        if isinstance(child, ttk.Label):
                            child.configure(background=self.selected_color, foreground="white")
                        elif isinstance(child, ttk.Frame):
                            child.configure(background=self.selected_color)
                            # Also handle nested frames
                            for subchild in child.winfo_children():
                                if isinstance(subchild, ttk.Label):
                                    subchild.configure(background=self.selected_color, foreground="white")
                                elif isinstance(subchild, tk.Label):  # For image labels
                                    subchild.configure(background=self.selected_color)
                else:
                    # Use standard style for unselected items
                    frame.configure(background=self.bg_color)
                    
                    # Reset all child labels
                    for child in frame.winfo_children():
                        if isinstance(child, ttk.Label):
                            child.configure(style="TLabel")
                            child.configure(background=self.bg_color, foreground=self.text_color)
                        elif isinstance(child, ttk.Frame):
                            child.configure(background=self.bg_color)
                            # Also handle nested frames
                            for subchild in child.winfo_children():
                                if isinstance(subchild, ttk.Label):
                                    subchild.configure(background=self.bg_color, foreground=self.text_color)
                                elif isinstance(subchild, tk.Label):  # For image labels
                                    subchild.configure(background=self.bg_color)
            
            # Make sure the selected panel is visible
            self._ensure_visible(index)
    
    def _ensure_visible(self, index):
        """
        Ensure the selected panel is visible in the scrollable area.
        
        Args:
            index: Index of the panel to make visible
        """
        if 0 <= index < len(self.panel_frames):
            # Get the position of the panel frame
            frame = self.panel_frames[index]
            bbox = self.canvas.bbox(self.canvas_window)
            if bbox:
                canvas_height = bbox[3] - bbox[1]
                frame_y = frame.winfo_y()
                frame_height = frame.winfo_height()
                
                # Get the current scroll position
                scroll_top = self.canvas.canvasy(0)
                scroll_bottom = scroll_top + canvas_height
                
                # If the panel is not fully visible, scroll to make it visible
                if frame_y < scroll_top:
                    # Scroll up to show the panel at the top
                    self.canvas.yview_moveto(frame_y / bbox[3])
                elif frame_y + frame_height > scroll_bottom:
                    # Scroll down to show the panel at the bottom
                    self.canvas.yview_moveto((frame_y + frame_height - canvas_height) / bbox[3])
    
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
        
        # Clear panel frames list
        self.panel_frames = []
        
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
        # Create a frame for this panel item with proper styling
        # Use tk.Frame instead of ttk.Frame to allow direct background configuration
        item_frame = tk.Frame(self.panels_frame, padx=5, pady=5)
        
        # Configure background color directly
        if index == self.selected_index:
            item_frame.configure(background=self.selected_color)
        else:
            item_frame.configure(background=self.bg_color)
        
        # Store reference to the frame
        self.panel_frames.append(item_frame)
        
        # Add hover effect (use tag to ensure we use the correct index even if panels are reordered)
        item_frame.bind("<Enter>", lambda e, i=index: self._on_panel_hover(i, True))
        item_frame.bind("<Leave>", lambda e, i=index: self._on_panel_hover(i, False))
        
        item_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Make the frame selectable by clicking (use index from the loop)
        item_frame.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i, e))
        
        # Create a horizontal layout
        info_frame = tk.Frame(item_frame)
        if index == self.selected_index:
            info_frame.configure(background=self.selected_color)
        else:
            info_frame.configure(background=self.bg_color)
            
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Also make this frame clickable
        info_frame.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i, e))
        
        # Add shot number label with proper styling
        label_style = "Selected.TLabel" if index == self.selected_index else "TLabel"
        shot_label = ttk.Label(
            info_frame, 
            text=f"Scene {panel.scene_number}{panel.shot_number}",
            style=label_style,
            font=("Arial", 10, "bold")
        )
        if index == self.selected_index:
            shot_label.configure(background=self.selected_color, foreground="white")
        else:
            shot_label.configure(background=self.bg_color, foreground=self.text_color)
            
        shot_label.pack(anchor=tk.W)
        
        # Make label clickable too
        shot_label.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i, e))
        
        # Add description preview if available
        if panel.description:
            # Limit to first 50 chars
            preview = panel.description[:50] + "..." if len(panel.description) > 50 else panel.description
            desc_label = ttk.Label(info_frame, text=preview, style=label_style)
            if index == self.selected_index:
                desc_label.configure(background=self.selected_color, foreground="white")
            else:
                desc_label.configure(background=self.bg_color, foreground=self.text_color)
                
            desc_label.pack(anchor=tk.W)
            # Make this label clickable too
            desc_label.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i, e))
        
        # Add camera info
        camera_label = ttk.Label(info_frame, text=f"Camera: {panel.camera}", style=label_style)
        if index == self.selected_index:
            camera_label.configure(background=self.selected_color, foreground="white")
        else:
            camera_label.configure(background=self.bg_color, foreground=self.text_color)
            
        camera_label.pack(anchor=tk.W)
        # Make this label clickable too
        camera_label.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i, e))
        
        # Add thumbnail if available
        thumbnail = panel.get_thumbnail()
        if thumbnail:
            self.thumbnails.append(thumbnail)  # Keep reference
            thumb_label = tk.Label(item_frame, image=thumbnail, borderwidth=0, 
                                  background=self.selected_color if index == self.selected_index else self.bg_color)
            thumb_label.pack(side=tk.RIGHT, padx=5)
            
            # Also make thumbnail clickable
            thumb_label.bind("<Button-1>", lambda e, i=index: self._on_panel_click(i, e))
    
    def _on_panel_hover(self, index, is_enter):
        """Handle hover events on panel items."""
        # Skip if this is the selected panel
        if index == self.selected_index:
            return
                
        # Get the frame for this index
        if 0 <= index < len(self.panel_frames):
            frame = self.panel_frames[index]
            if is_enter:
                # Highlight on hover
                frame.configure(background=self.hover_color)
            else:
                # Remove highlight
                frame.configure(background=self.bg_color)
