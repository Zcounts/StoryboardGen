# storyboard_generator/panels_list.py
import tkinter as tk
from tkinter import ttk

class PanelsList(ttk.Frame):
    """A custom widget that displays panels grouped by scene."""
    
    def __init__(self, master, on_select=None, on_add=None, on_delete=None, on_move_up=None, on_move_down=None, on_duplicate=None):
        """Initialize the panels list widget."""
        super().__init__(master)
        self.on_select = on_select
        self.on_add = on_add
        self.on_delete = on_delete
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.on_duplicate = on_duplicate
        
        self.panels = []
        self.scene_trees = {}  # Dictionary to store scene treeviews
        self.selected_panel_index = -1
        
        # Set colors for dark theme
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        
        # Configure style
        style = ttk.Style()
        style.configure("Dark.Treeview", 
                        background=self.bg_color,
                        foreground=self.text_color,
                        fieldbackground=self.bg_color)
        style.map("Dark.Treeview",
                 background=[("selected", "#3E3E42")],
                 foreground=[("selected", self.text_color)])
        style.configure("Dark.TFrame", background=self.bg_color)
        style.configure("Dark.TButton", background=self.accent_color, foreground=self.text_color)
        
        # Create the main frame
        self.config(style="Dark.TFrame")
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI components."""
        # Main container with scrollbar
        self.canvas = tk.Canvas(self, background=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Dark.TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title label
        ttk.Label(self.scrollable_frame, text="Storyboard Panels", style="Dark.TLabel").pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        # Button frame for panel management
        button_frame = ttk.Frame(self.scrollable_frame, style="Dark.TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add panel button
        self.add_button = ttk.Button(button_frame, text="Add", command=self._on_add_panel, style="Dark.TButton")
        self.add_button.pack(side=tk.LEFT, padx=2)
        
        # Delete panel button
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self._on_delete_panel, style="Dark.TButton")
        self.delete_button.pack(side=tk.LEFT, padx=2)
        
        # Move up button
        self.up_button = ttk.Button(button_frame, text="Up", command=self._on_move_panel_up, style="Dark.TButton")
        self.up_button.pack(side=tk.LEFT, padx=2)
        
        # Move down button
        self.down_button = ttk.Button(button_frame, text="Down", command=self._on_move_panel_down, style="Dark.TButton")
        self.down_button.pack(side=tk.LEFT, padx=2)
        
        # Duplicate button
        self.duplicate_button = ttk.Button(button_frame, text="Duplicate", command=self._on_duplicate_panel, style="Dark.TButton")
        self.duplicate_button.pack(side=tk.LEFT, padx=2)
        
        # Container for scenes
        self.scenes_container = ttk.Frame(self.scrollable_frame, style="Dark.TFrame")
        self.scenes_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def update_panels(self, panels):
        """
        Update the panels list with the given panels.
        
        Args:
            panels: List of Panel objects
        """
        self.panels = panels
        
        # Clear existing scenes
        for widget in self.scenes_container.winfo_children():
            widget.destroy()
        self.scene_trees = {}
        
        # Group panels by scene
        scene_groups = {}
        for panel in self.panels:
            scene_number = panel.scene_number
            if scene_number not in scene_groups:
                scene_groups[scene_number] = []
            scene_groups[scene_number].append(panel)
        
        # Sort scenes numerically
        sorted_scenes = sorted(scene_groups.keys(), key=lambda s: int(s) if s.isdigit() else float('inf'))
        
        # Create a tree for each scene
        for scene_number in sorted_scenes:
            scene_frame = ttk.LabelFrame(self.scenes_container, text=f"Scene {scene_number}", style="Dark.TLabelframe")
            scene_frame.pack(fill=tk.X, pady=5)
            
            # Create treeview for this scene
            tree = ttk.Treeview(scene_frame, columns=("shot", "description"), height=len(scene_groups[scene_number]), style="Dark.Treeview")
            tree.heading("#0", text="")
            tree.heading("shot", text="Shot")
            tree.heading("description", text="Description")
            
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("shot", width=80, anchor=tk.W)
            tree.column("description", width=200)
            
            tree.pack(fill=tk.X, pady=5)
            
            # Add panels to tree
            for i, panel in enumerate(scene_groups[scene_number]):
                shot_text = f"{scene_number}{panel.shot_number}" if panel.shot_number else f"{scene_number}"
                desc_text = panel.description[:30] + "..." if len(panel.description) > 30 else panel.description
                tree.insert("", tk.END, text="", values=(shot_text, desc_text), tags=(str(self.panels.index(panel)),))
            
            # Bind selection event
            tree.bind("<<TreeviewSelect>>", self._on_tree_select)
            
            # Store reference to tree
            self.scene_trees[scene_number] = tree
        
        # Select the current panel if any
        if self.selected_panel_index >= 0 and self.selected_panel_index < len(self.panels):
            self.select_panel(self.selected_panel_index)
    
    def _on_tree_select(self, event):
        """Handle selection events from any tree."""
        for scene_number, tree in self.scene_trees.items():
            selection = tree.selection()
            if selection:
                item = selection[0]
                # Get the panel index from tag
                panel_index = int(tree.item(item, "tags")[0])
                self.selected_panel_index = panel_index
                
                # Deselect in other trees
                for other_scene, other_tree in self.scene_trees.items():
                    if other_scene != scene_number:
                        other_tree.selection_remove(other_tree.selection())
                
                # Call selection callback
                if self.on_select:
                    self.on_select(panel_index)
                
                # Exit loop as we found our selection
                break
    
    def select_panel(self, panel_index):
        """
        Select a panel by its index in the panels list.
        
        Args:
            panel_index: Index of the panel to select
        """
        if panel_index < 0 or panel_index >= len(self.panels):
            return
        
        # Find which scene tree contains the panel
        panel = self.panels[panel_index]
        scene_number = panel.scene_number
        
        if scene_number in self.scene_trees:
            tree = self.scene_trees[scene_number]
            
            # Find the item with the matching tag
            for item in tree.get_children():
                if int(tree.item(item, "tags")[0]) == panel_index:
                    # Select this item
                    tree.selection_set(item)
                    tree.see(item)
                    self.selected_panel_index = panel_index
                    break
    
    def _on_add_panel(self):
        """Handle add panel button click."""
        if self.on_add:
            self.on_add()
    
    def _on_delete_panel(self):
        """Handle delete panel button click."""
        if self.on_delete and self.selected_panel_index >= 0:
            self.on_delete()
    
    def _on_move_panel_up(self):
        """Handle move up button click."""
        if self.on_move_up and self.selected_panel_index > 0:
            self.on_move_up()
    
    def _on_move_panel_down(self):
        """Handle move down button click."""
        if self.on_move_down and self.selected_panel_index >= 0 and self.selected_panel_index < len(self.panels) - 1:
            self.on_move_down()
    
    def _on_duplicate_panel(self):
        """Handle duplicate button click."""
        if self.on_duplicate and self.selected_panel_index >= 0:
            self.on_duplicate()
