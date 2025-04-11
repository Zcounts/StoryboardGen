# Update to app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from PIL import Image, ImageTk

from panel import Panel
from panel_editor import PanelEditor
from panels_list import PanelsList

class StoryboardApp:
    """Main application class for the Storyboard Generator."""
    
    def __init__(self, master):
        """Initialize the application."""
        self.master = master
        self.current_project = None
        self.project_dir = None
        self.panels = []
        self.current_panel_index = -1
        
        # Create the main UI components
        self._create_menu()
        self._create_main_frame()
        
        # Set up initial state
        self._new_project()
    
    def _create_menu(self):
        """Create the application menu bar."""
        # (Same as before)
        # ...
    
    def _create_main_frame(self):
        """Create the main application frame."""
        # Create main frame with left and right panes
        self.main_frame = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - Panels list
        self.left_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.left_frame, weight=1)
        
        # Right frame - Panel editor
        self.right_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.right_frame, weight=3)
        
        # Set up panels list
        self._setup_panels_list()
        
        # Set up panel editor
        self._setup_panel_editor()
    
    def _setup_panels_list(self):
        """Set up the panels list in the left frame."""
        # Panel list label
        ttk.Label(self.left_frame, text="Storyboard Panels").pack(pady=(0, 5), anchor=tk.W)
        
        # Create the custom panels list
        self.panels_list = PanelsList(self.left_frame, on_select=self._on_panel_select)
        self.panels_list.pack(fill=tk.BOTH, expand=True)
        
        # Store references to the panel management methods in the PanelsList
        self.panels_list.on_select = self
    
    def _setup_panel_editor(self):
        """Set up the panel editor in the right frame."""
        # Panel editor title
        ttk.Label(self.right_frame, text="Panel Editor").pack(pady=(0, 10), anchor=tk.W)
        
        # Create the panel editor
        self.panel_editor = PanelEditor(self.right_frame, on_panel_update=self._on_panel_update)
        self.panel_editor.pack(fill=tk.BOTH, expand=True)
        
        # Initially disable the panel editor
        self._update_panel_editor()
    
    def _on_panel_update(self, panel):
        """Handle panel update event from the editor."""
        if panel and panel in self.panels:
            # Update the panels list to reflect changes
            self._update_panels_list()
    
    def _update_panel_editor(self):
        """Update the panel editor with the currently selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Load the selected panel into the editor
            self.panel_editor.load_panel(self.panels[self.current_panel_index])
        else:
            # No panel selected, clear the editor
            self.panel_editor.load_panel(None)
    
    def _new_project(self):
        """Create a new project."""
        self.current_project = None
        self.project_dir = None
        self.panels = []
        self.current_panel_index = -1
        self._update_panels_list()
        self._update_panel_editor()
    
    def _open_project(self):
        """Open an existing project."""
        # (implementation remains the same)
        # ...
    
    def _save_project(self):
        """Save the current project."""
        # (implementation remains the same)
        # ...
    
    def _export_pdf(self):
        """Export the storyboard as PDF."""
        # (implementation remains the same)
        # ...
    
    def add_panel(self):
        """Add a new panel to the storyboard."""
        # Create a new panel
        panel = Panel()
        
        # If we have existing panels, set default values from the last panel
        if self.panels:
            last_panel = self.panels[-1]
            panel.scene_number = last_panel.scene_number
            panel.camera = last_panel.camera
        
        # Add to the list
        self.panels.append(panel)
        
        # Update UI
        self._update_panels_list()
        
        # Select the new panel
        self.current_panel_index = len(self.panels) - 1
        self.panels_list.select_panel(self.current_panel_index)
        
        # Update editor
        self._update_panel_editor()
    
    def delete_panel(self):
        """Delete the selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Remove the panel
            del self.panels[self.current_panel_index]
            
            # Update UI
            self._update_panels_list()
            
            # Adjust the selection
            if self.panels:
                if self.current_panel_index >= len(self.panels):
                    self.current_panel_index = len(self.panels) - 1
                self.panels_list.select_panel(self.current_panel_index)
            else:
                self.current_panel_index = -1
            
            # Update editor
            self._update_panel_editor()
    
    def move_panel_up(self):
        """Move the selected panel up in the order."""
        if 0 < self.current_panel_index < len(self.panels):
            # Swap with the previous panel
            self.panels[self.current_panel_index], self.panels[self.current_panel_index-1] = \
                self.panels[self.current_panel_index-1], self.panels[self.current_panel_index]
            
            # Update UI
            self._update_panels_list()
            
            # Update selection
            self.current_panel_index -= 1
            self.panels_list.select_panel(self.current_panel_index)
            
            # Update panel orders
            for i, panel in enumerate(self.panels):
                panel.order = i
    
    def move_panel_down(self):
        """Move the selected panel down in the order."""
        if 0 <= self.current_panel_index < len(self.panels) - 1:
            # Swap with the next panel
            self.panels[self.current_panel_index], self.panels[self.current_panel_index+1] = \
                self.panels[self.current_panel_index+1], self.panels[self.current_panel_index]
            
            # Update UI
            self._update_panels_list()
            
            # Update selection
            self.current_panel_index += 1
            self.panels_list.select_panel(self.current_panel_index)
            
            # Update panel orders
            for i, panel in enumerate(self.panels):
                panel.order = i
    
    def _on_panel_select(self, index):
        """Handle panel selection event."""
        if 0 <= index < len(self.panels):
            # Update the current panel index
            self.current_panel_index = index
            
            # Update the panel editor
            self._update_panel_editor()
    
    def _update_panels_list(self):
        """Update the panels list in the UI."""
        # Update the custom panels list
        self.panels_list.update_panels(self.panels)
